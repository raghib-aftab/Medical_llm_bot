from motor.motor_asyncio import AsyncIOMotorClient
from typing import List, Optional
from datetime import datetime
import zoneinfo
from bson import ObjectId
from config import settings

class DatabaseService:
    def __init__(self):
        self.client: Optional[AsyncIOMotorClient] = None
        self.db = None
        self._indexes_created = False
        
    async def connect(self):
        """Connect to MongoDB"""
        self.client = AsyncIOMotorClient(
            settings.mongodb_url,
            tls=True,
            tlsAllowInvalidCertificates=True,
            serverSelectionTimeoutMS=30000,  # Increased timeout
            connectTimeoutMS=30000,
            socketTimeoutMS=30000,
            retryWrites=True,
            retryReads=True,
            maxPoolSize=10,
            minPoolSize=1
        )
        self.db = self.client[settings.database_name]
        
    async def _ensure_indexes(self):
        """Create indexes if not already created"""
        if not self._indexes_created:
            try:
                await self.db.users.create_index("email", unique=True)
                self._indexes_created = True
            except Exception as e:
                print(f"Warning: Could not create indexes: {e}")
        
    async def close(self):
        """Close MongoDB connection"""
        if self.client:
            self.client.close()
    
    # ============ User Operations ============
    
    async def create_user(self, email: str, name: str, hashed_password: str, phone: str = None) -> str:
        """Create a new user and return their ID"""
        user_doc = {
            "email": email.lower(),
            "name": name,
            "hashed_password": hashed_password,
            "phone": phone,
            "created_at": datetime.now(zoneinfo.ZoneInfo("Asia/Kolkata"))
        }
        result = await self.db.users.insert_one(user_doc)
        return str(result.inserted_id)
    
    async def get_user_by_email(self, email: str) -> Optional[dict]:
        """Get a user by email (case-insensitive)"""
        user = await self.db.users.find_one({"email": email.lower()})
        if user:
            user["id"] = str(user.pop("_id"))
        return user
    
    async def get_user_by_id(self, user_id: str) -> Optional[dict]:
        """Get a user by ID"""
        try:
            user = await self.db.users.find_one({"_id": ObjectId(user_id)})
            if user:
                user["id"] = str(user.pop("_id"))
            return user
        except Exception:
            return None
    
    async def update_user_password(self, user_id: str, hashed_password: str) -> bool:
        """Update user's password"""
        try:
            result = await self.db.users.update_one(
                {"_id": ObjectId(user_id)},
                {"$set": {"hashed_password": hashed_password}}
            )
            return result.modified_count > 0
        except Exception:
            return False
    
    # ============ Chat Operations ============
    
    async def create_chat(self, title: str, user_id: str) -> str:
        """Create a new chat and return its ID"""
        chat_doc = {
            "title": title,
            "user_id": user_id,
            "created_at": datetime.now(zoneinfo.ZoneInfo("Asia/Kolkata")),
            "updated_at": datetime.now(zoneinfo.ZoneInfo("Asia/Kolkata")),
            "messages": []
        }
        result = await self.db.chats.insert_one(chat_doc)
        return str(result.inserted_id)
    
    async def get_all_chats(self, user_id: str) -> List[dict]:
        """Get all chats for a specific user (without messages for efficiency)"""
        chats = []
        cursor = self.db.chats.find(
            {"user_id": user_id}, 
            {"messages": 0}
        ).sort("updated_at", -1)
        async for chat in cursor:
            chat["id"] = str(chat.pop("_id"))
            chats.append(chat)
        return chats
    
    async def get_chat(self, chat_id: str, user_id: str = None) -> Optional[dict]:
        """Get a specific chat with all messages"""
        try:
            query = {"_id": ObjectId(chat_id)}
            if user_id:
                query["user_id"] = user_id
            chat = await self.db.chats.find_one(query)
            if chat:
                chat["id"] = str(chat.pop("_id"))
            return chat
        except Exception:
            return None
    
    async def delete_chat(self, chat_id: str, user_id: str) -> bool:
        """Delete a chat (only if owned by user)"""
        try:
            result = await self.db.chats.delete_one({
                "_id": ObjectId(chat_id),
                "user_id": user_id
            })
            return result.deleted_count > 0
        except Exception:
            return False
    
    async def add_message(self, chat_id: str, role: str, content: str) -> bool:
        """Add a message to a chat"""
        try:
            message = {
                "role": role,
                "content": content,
                "timestamp": datetime.now(zoneinfo.ZoneInfo("Asia/Kolkata"))
            }
            result = await self.db.chats.update_one(
                {"_id": ObjectId(chat_id)},
                {
                    "$push": {"messages": message},
                    "$set": {"updated_at": datetime.now(zoneinfo.ZoneInfo("Asia/Kolkata"))}
                }
            )
            return result.modified_count > 0
        except Exception:
            return False
    
    async def update_chat_title(self, chat_id: str, title: str) -> bool:
        """Update the title of a chat"""
        try:
            result = await self.db.chats.update_one(
                {"_id": ObjectId(chat_id)},
                {"$set": {"title": title, "updated_at": datetime.now(zoneinfo.ZoneInfo("Asia/Kolkata"))}}
            )
            return result.modified_count > 0
        except Exception:
            return False
    
    async def get_recent_messages(self, chat_id: str, count: int = 4) -> List[dict]:
        """Get the last N messages from a chat"""
        try:
            chat = await self.db.chats.find_one(
                {"_id": ObjectId(chat_id)},
                {"messages": {"$slice": -count}}
            )
            return chat.get("messages", []) if chat else []
        except Exception:
            return []
    
    # ============ User Update Operations ============
    
    async def update_user(self, user_id: str, update_data: dict) -> bool:
        """Update user information"""
        try:
            result = await self.db.users.update_one(
                {"_id": ObjectId(user_id)},
                {"$set": update_data}
            )
            return result.modified_count > 0
        except Exception:
            return False
    
    # ============ Appointment Operations ============
    
    async def create_appointment(
        self, 
        user_id: str, 
        doctor_id: str, 
        doctor_name: str,
        specialization: str,
        appointment_date: str, 
        appointment_time: str,
        reason: str = None,
        hospital_name: str = None
    ) -> str:
        """Create a new appointment and return its ID"""
        appointment_doc = {
            "user_id": user_id,
            "doctor_id": doctor_id,
            "doctor_name": doctor_name,
            "specialization": specialization,
            "hospital_name": hospital_name,
            "appointment_date": appointment_date,
            "appointment_time": appointment_time,
            "reason": reason,
            "status": "scheduled",
            "created_at": datetime.now(zoneinfo.ZoneInfo("Asia/Kolkata")),
            "updated_at": datetime.now(zoneinfo.ZoneInfo("Asia/Kolkata"))
        }
        result = await self.db.appointments.insert_one(appointment_doc)
        return str(result.inserted_id)
    
    async def get_appointment_by_id(self, appointment_id: str) -> Optional[dict]:
        """Get an appointment by ID"""
        try:
            appointment = await self.db.appointments.find_one({"_id": ObjectId(appointment_id)})
            if appointment:
                appointment["id"] = str(appointment.pop("_id"))
            return appointment
        except Exception:
            return None
    
    async def get_user_appointments(self, user_id: str, status_filter: str = None) -> List[dict]:
        """Get all appointments for a user"""
        query = {"user_id": user_id}
        if status_filter:
            query["status"] = status_filter
        
        appointments = []
        cursor = self.db.appointments.find(query).sort("appointment_date", -1)
        async for apt in cursor:
            apt["id"] = str(apt.pop("_id"))
            appointments.append(apt)
        return appointments
    
    async def update_appointment(self, appointment_id: str, update_data: dict) -> bool:
        """Update an appointment"""
        try:
            update_data["updated_at"] = datetime.now(zoneinfo.ZoneInfo("Asia/Kolkata"))
            result = await self.db.appointments.update_one(
                {"_id": ObjectId(appointment_id)},
                {"$set": update_data}
            )
            return result.modified_count > 0
        except Exception:
            return False
    
    async def check_appointment_conflict(
        self, 
        doctor_id: str, 
        appointment_date: str, 
        appointment_time: str
    ) -> bool:
        """Check if there's an existing appointment at the same time"""
        try:
            existing = await self.db.appointments.find_one({
                "doctor_id": doctor_id,
                "appointment_date": appointment_date,
                "appointment_time": appointment_time,
                "status": {"$ne": "cancelled"}
            })
            return existing is not None
        except Exception:
            return False
    
    async def delete_appointment(self, appointment_id: str, user_id: str) -> bool:
        """Delete an appointment (only if owned by user)"""
        try:
            result = await self.db.appointments.delete_one({
                "_id": ObjectId(appointment_id),
                "user_id": user_id
            })
            return result.deleted_count > 0
        except Exception:
            return False

    # ============ Doctor Operations ============
    
    async def get_all_doctors(self, specialization: str = None) -> List[dict]:
        """Get all doctors, optionally filtered by specialization"""
        query = {}
        if specialization:
            # Case-insensitive partial match
            query["specialization"] = {"$regex": specialization, "$options": "i"}
        
        doctors = []
        cursor = self.db.doctors.find(query)
        async for doc in cursor:
            doc["id"] = doc.get("id", str(doc.pop("_id", "")))
            if "_id" in doc:
                del doc["_id"]
            doctors.append(doc)
        return doctors
    
    async def get_doctor_by_id(self, doctor_id: str) -> Optional[dict]:
        """Get a doctor by ID"""
        try:
            doctor = await self.db.doctors.find_one({"id": doctor_id})
            if doctor:
                doctor["id"] = doctor.get("id", str(doctor.pop("_id", "")))
                if "_id" in doctor:
                    del doctor["_id"]
            return doctor
        except Exception:
            return None
    
    async def get_doctor_specializations(self) -> List[str]:
        """Get all unique doctor specializations"""
        specializations = await self.db.doctors.distinct("specialization")
        return sorted(specializations)
    
    async def insert_doctor(self, doctor_data: dict) -> bool:
        """Insert a doctor into the database"""
        try:
            await self.db.doctors.insert_one(doctor_data)
            return True
        except Exception as e:
            print(f"Error inserting doctor: {e}")
            return False
    
    async def insert_many_doctors(self, doctors: List[dict]) -> bool:
        """Insert multiple doctors into the database"""
        try:
            if doctors:
                await self.db.doctors.insert_many(doctors)
            return True
        except Exception as e:
            print(f"Error inserting doctors: {e}")
            return False
    
    async def get_doctors_count(self) -> int:
        """Get the count of doctors in the database"""
        return await self.db.doctors.count_documents({})
    
    # ============ Hospital Operations ============
    
    async def get_all_hospitals(self, city: str = None, specialization: str = None, emergency_only: bool = False) -> List[dict]:
        """Get all hospitals with optional filters"""
        query = {}
        
        if city:
            query["city"] = {"$regex": f"^{city}$", "$options": "i"}
        
        if specialization:
            query["specializations"] = {"$elemMatch": {"$regex": specialization, "$options": "i"}}
        
        if emergency_only:
            query["emergency_available"] = True
        
        hospitals = []
        cursor = self.db.hospitals.find(query)
        async for hosp in cursor:
            hosp["id"] = hosp.get("id", str(hosp.pop("_id", "")))
            if "_id" in hosp:
                del hosp["_id"]
            hospitals.append(hosp)
        return hospitals
    
    async def get_hospital_by_id(self, hospital_id: str) -> Optional[dict]:
        """Get a hospital by ID"""
        try:
            hospital = await self.db.hospitals.find_one({"id": hospital_id})
            if hospital:
                hospital["id"] = hospital.get("id", str(hospital.pop("_id", "")))
                if "_id" in hospital:
                    del hospital["_id"]
            return hospital
        except Exception:
            return None
    
    async def get_hospital_cities(self) -> List[str]:
        """Get all unique hospital cities"""
        cities = await self.db.hospitals.distinct("city")
        return sorted(cities)
    
    async def get_hospital_specializations(self) -> List[str]:
        """Get all unique hospital specializations"""
        pipeline = [
            {"$unwind": "$specializations"},
            {"$group": {"_id": "$specializations"}},
            {"$sort": {"_id": 1}}
        ]
        specializations = []
        async for doc in self.db.hospitals.aggregate(pipeline):
            specializations.append(doc["_id"])
        return specializations
    
    async def insert_hospital(self, hospital_data: dict) -> bool:
        """Insert a hospital into the database"""
        try:
            await self.db.hospitals.insert_one(hospital_data)
            return True
        except Exception as e:
            print(f"Error inserting hospital: {e}")
            return False
    
    async def insert_many_hospitals(self, hospitals: List[dict]) -> bool:
        """Insert multiple hospitals into the database"""
        try:
            if hospitals:
                await self.db.hospitals.insert_many(hospitals)
            return True
        except Exception as e:
            print(f"Error inserting hospitals: {e}")
            return False
    
    async def get_hospitals_count(self) -> int:
        """Get the count of hospitals in the database"""
        return await self.db.hospitals.count_documents({})

db_service = DatabaseService()
