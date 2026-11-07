#!/usr/bin/env python
"""
One-time database initialization script for Medical LLM UI project.

This script creates and seeds the `doctors` and `hospitals` collections
with sample data from the model definitions. It does NOT modify users,
chats, or appointments collections.

Usage:
    # Dry-run (default) - shows what would be done without writing
    python -m scripts.initialize_medical_data

    # Apply changes - actually writes to MongoDB
    python -m scripts.initialize_medical_data --apply

    # Verbose output
    python -m scripts.initialize_medical_data --apply --verbose

The script is idempotent: re-running it will not duplicate records.
It uses the project's existing configuration and database connection approach.
"""

import argparse
import asyncio
import sys
from typing import List

# Add parent directory to path for imports
sys.path.insert(0, str(__file__).rsplit("\\", 2)[0])

from motor.motor_asyncio import AsyncIOMotorClient
from config import settings
from models.doctor import DOCTORS_DATA
from models.hospital import HOSPITALS_DATA


async def check_database_connection(client: AsyncIOMotorClient, db_name: str) -> bool:
    """Verify we can connect to the correct database."""
    try:
        await client.admin.command("ping")
        db = client[db_name]
        collections = await db.list_collection_names()
        print(f"[OK] Connected to database: {db_name}")
        print(f"  Existing collections: {collections}")
        return True
    except Exception as e:
        print(f"[ERROR] Failed to connect to database: {e}")
        return False


async def get_collection_counts(db, collection_names: List[str]) -> dict:
    """Get document counts for specified collections."""
    counts = {}
    for name in collection_names:
        if name in await db.list_collection_names():
            counts[name] = await db[name].count_documents({})
        else:
            counts[name] = 0  # Collection doesn't exist yet
    return counts


async def create_indexes(db, apply: bool, verbose: bool):
    """Create indexes for doctors and hospitals collections."""
    indexes_to_create = [
        # Doctors indexes
        ("doctors", "specialization", "supports get_all_doctors regex filter"),
        ("doctors", "id", "supports get_doctor_by_id lookup"),
        # Hospitals indexes
        ("hospitals", "city", "supports get_all_hospitals city filter"),
        ("hospitals", "specializations", "supports $elemMatch specialization filter"),
        ("hospitals", "emergency_available", "supports emergency_only filter"),
        ("hospitals", "id", "supports get_hospital_by_id lookup"),
        # Appointments indexes (collection created lazily on first insert)
        # These will be created when the first appointment is made
        # but we document them here for reference
    ]

    print("\n--- Index Creation ---")
    for coll_name, field, reason in indexes_to_create:
        if coll_name in await db.list_collection_names():
            index_name = f"{field}_1"
            if apply:
                try:
                    await db[coll_name].create_index(field, name=index_name)
                    print(f"  [OK] Created index on {coll_name}.{field} ({reason})")
                except Exception as e:
                    if "already exists" in str(e).lower() or "duplicate key" in str(e).lower():
                        print(f"  - Index {coll_name}.{field} already exists")
                    else:
                        print(f"  [ERROR] Failed to create index {coll_name}.{field}: {e}")
            elif verbose:
                print(f"  [DRY-RUN] Would create index on {coll_name}.{field} ({reason})")


async def seed_doctors(db, apply: bool, verbose: bool) -> dict:
    """Seed the doctors collection with DOCTORS_DATA."""
    result = {"checked": 0, "inserted": 0, "skipped": 0, "errors": 0}

    if "doctors" not in await db.list_collection_names():
        if apply:
            # Collection will be created on first insert
            pass
        elif verbose:
            print("  [dry-run] Collection 'doctors' will be created on first insert")

    for doctor in DOCTORS_DATA:
        result["checked"] += 1
        doctor_id = doctor.get("id")

        # Check if doctor already exists
        existing = await db.doctors.find_one({"id": doctor_id})
        if existing:
            result["skipped"] += 1
            if verbose:
                print(f"  - Doctor {doctor_id} already exists, skipping")
            continue

        if apply:
            try:
                await db.doctors.insert_one(doctor)
                result["inserted"] += 1
                print(f"  [OK] Inserted doctor: {doctor_id}")
            except Exception as e:
                result["errors"] += 1
                print(f"  [ERROR] Failed to insert doctor {doctor_id}: {e}")
        elif verbose:
            print(f"  [DRY-RUN] Would insert doctor: {doctor_id} ({doctor.get('name')}, {doctor.get('specialization')})")

    return result


async def seed_hospitals(db, apply: bool, verbose: bool) -> dict:
    """Seed the hospitals collection with HOSPITALS_DATA."""
    result = {"checked": 0, "inserted": 0, "skipped": 0, "errors": 0}

    if "hospitals" not in await db.list_collection_names():
        if apply:
            pass
        elif verbose:
            print("  [dry-run] Collection 'hospitals' will be created on first insert")

    for hospital in HOSPITALS_DATA:
        result["checked"] += 1
        hospital_id = hospital.get("id")

        # Check if hospital already exists
        existing = await db.hospitals.find_one({"id": hospital_id})
        if existing:
            result["skipped"] += 1
            if verbose:
                print(f"  - Hospital {hospital_id} already exists, skipping")
            continue

        if apply:
            try:
                await db.hospitals.insert_one(hospital)
                result["inserted"] += 1
                print(f"  [OK] Inserted hospital: {hospital_id}")
            except Exception as e:
                result["errors"] += 1
                print(f"  [ERROR] Failed to insert hospital {hospital_id}: {e}")
        elif verbose:
            print(f"  [DRY-RUN] Would insert hospital: {hospital_id} ({hospital.get('name')}, {hospital.get('city')})")

    return result


async def verify_data_integrity(db, verbose: bool):
    """Verify that the seeded data can be queried correctly."""
    print("\n--- Data Integrity Verification ---")

    # Test doctor queries
    doctor_count = await db.doctors.count_documents({})
    print(f"  Doctors total: {doctor_count}")

    if doctor_count > 0:
        specializations = await db.doctors.distinct("specialization")
        print(f"  Unique specializations: {len(specializations)} - {sorted(specializations)}")

        # Test get_doctor_by_id
        sample = await db.doctors.find_one({})
        if sample:
            doc_id = sample.get("id")
            found = await db.doctors.find_one({"id": doc_id})
            print(f"  get_doctor_by_id('{doc_id}'): {'[OK] found' if found else '[ERROR] NOT FOUND'}")

    # Test hospital queries
    hospital_count = await db.hospitals.count_documents({})
    print(f"  Hospitals total: {hospital_count}")

    if hospital_count > 0:
        cities = await db.hospitals.distinct("city")
        print(f"  Unique cities: {len(cities)} - {sorted(cities)}")

        # Test aggregation for specializations
        pipeline = [
            {"$unwind": "$specializations"},
            {"$group": {"_id": "$specializations"}},
            {"$sort": {"_id": 1}}
        ]
        hosp_specs = []
        async for doc in db.hospitals.aggregate(pipeline):
            hosp_specs.append(doc["_id"])
        print(f"  Unique hospital specializations: {len(hosp_specs)} - {hosp_specs}")

        # Test get_hospital_by_id
        sample = await db.hospitals.find_one({})
        if sample:
            hosp_id = sample.get("id")
            found = await db.hospitals.find_one({"id": hosp_id})
            print(f"  get_hospital_by_id('{hosp_id}'): {'[OK] found' if found else '[ERROR] NOT FOUND'}")


async def main():
    parser = argparse.ArgumentParser(
        description="Initialize medical data collections in MongoDB",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python -m scripts.initialize_medical_data           # Dry-run (default)
    python -m scripts.initialize_medical_data --apply   # Actually write to database
    python -m scripts.initialize_medical_data --apply --verbose
        """
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Actually write changes to MongoDB (default is dry-run)"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Show detailed output"
    )
    args = parser.parse_args()

    mode = "APPLY" if args.apply else "DRY-RUN"
    print(f"=== Medical Data Initialization ({mode}) ===")
    print(f"Database: {settings.database_name}")
    print(f"Sample data: {len(DOCTORS_DATA)} doctors, {len(HOSPITALS_DATA)} hospitals")
    print("Note: Sample data contains fictional/demonstration listings, not verified real providers")

    # Connect to MongoDB
    client = AsyncIOMotorClient(
        settings.mongodb_url,
        tls=True,
        tlsAllowInvalidCertificates=True,
        serverSelectionTimeoutMS=30000,
        connectTimeoutMS=30000,
        socketTimeoutMS=30000,
    )

    try:
        db = client[settings.database_name]

        # Verify connection
        if not await check_database_connection(client, settings.database_name):
            return 1

        # Show current state
        print("\n--- Current Collection Counts ---")
        counts = await get_collection_counts(db, ["users", "chats", "doctors", "hospitals", "appointments"])
        for coll, count in counts.items():
            status = "✓" if count > 0 else ("(missing)" if count == 0 and coll not in ["users", "chats"] else "")
            print(f"  {coll}: {count} {status}")

        if not args.apply:
            print("\n--- Dry-run mode: no changes will be written ---")
            print("Use --apply to execute the initialization")

        # Create indexes
        await create_indexes(db, args.apply, args.verbose)

        # Seed doctors
        print("\n--- Seeding Doctors ---")
        doctor_result = await seed_doctors(db, args.apply, args.verbose)
        print(f"  Checked: {doctor_result['checked']}, Inserted: {doctor_result['inserted']}, "
              f"Skipped: {doctor_result['skipped']}, Errors: {doctor_result['errors']}")

        # Seed hospitals
        print("\n--- Seeding Hospitals ---")
        hospital_result = await seed_hospitals(db, args.apply, args.verbose)
        print(f"  Checked: {hospital_result['checked']}, Inserted: {hospital_result['inserted']}, "
              f"Skipped: {hospital_result['skipped']}, Errors: {hospital_result['errors']}")

        # Verify if applied
        if args.apply and (doctor_result['inserted'] > 0 or hospital_result['inserted'] > 0):
            await verify_data_integrity(db, args.verbose)

        # Final summary
        print("\n--- Summary ---")
        final_counts = await get_collection_counts(db, ["doctors", "hospitals"])
        for coll, count in final_counts.items():
            print(f"  {coll}: {count} documents")

        total_errors = doctor_result['errors'] + hospital_result['errors']
        if total_errors > 0:
            print(f"\n[WARNING] Completed with {total_errors} error(s)")
            return 1
        elif args.apply:
            print("\n[OK] Initialization completed successfully")
            return 0
        else:
            print("\n[OK] Dry-run completed. Run with --apply to execute.")
            return 0

    except Exception as e:
        print(f"\n[FATAL] Error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    finally:
        client.close()


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))