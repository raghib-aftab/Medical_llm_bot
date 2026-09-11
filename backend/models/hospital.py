from pydantic import BaseModel
from typing import List, Optional

class Hospital(BaseModel):
    id: str
    name: str
    address: str
    city: str
    phone: str
    email: Optional[str] = None
    specializations: List[str]
    facilities: List[str]
    rating: float = 4.0
    image_url: Optional[str] = None
    emergency_available: bool = True
    bed_count: int = 100

# Sample hospitals data
HOSPITALS_DATA = [
    {
        "id": "hosp_001",
        "name": "Apollo Hospital, Delhi",
        "address": "Sarita Vihar, Delhi Mathura Road",
        "city": "Delhi",
        "phone": "+91-11-26925858",
        "email": "info@apollodelhi.com",
        "specializations": ["Cardiology", "Neurology", "Orthopedics", "Oncology", "Gastroenterology"],
        "facilities": ["ICU", "Emergency", "Pharmacy", "Laboratory", "Radiology", "Cafeteria", "MRI Center"],
        "rating": 4.8,
        "emergency_available": True,
        "bed_count": 710
    },
    {
        "id": "hosp_002",
        "name": "Fortis Hospital, Mumbai",
        "address": "Mulund Goregaon Link Road, Mulund West",
        "city": "Mumbai",
        "phone": "+91-22-67116711",
        "email": "info@fortismumbai.com",
        "specializations": ["Cardiology", "Dermatology", "Nephrology", "Oncology", "Neurology"],
        "facilities": ["Cardiac ICU", "Cath Lab", "Emergency", "Pharmacy", "Dialysis Center"],
        "rating": 4.6,
        "emergency_available": True,
        "bed_count": 300
    },
    {
        "id": "hosp_003",
        "name": "Max Hospital, Delhi",
        "address": "1, 2, Press Enclave Road, Saket",
        "city": "Delhi",
        "phone": "+91-11-26515050",
        "email": "info@maxhealthcare.com",
        "specializations": ["Pediatrics", "Cardiology", "Orthopedics", "Neurology", "Oncology"],
        "facilities": ["NICU", "PICU", "Emergency", "Pharmacy", "Laboratory", "Radiology"],
        "rating": 4.7,
        "emergency_available": True,
        "bed_count": 500
    },
    {
        "id": "hosp_004",
        "name": "AIIMS Hospital, Delhi",
        "address": "Sri Aurobindo Marg, Ansari Nagar",
        "city": "Delhi",
        "phone": "+91-11-26588500",
        "email": "info@aiims.edu",
        "specializations": ["Orthopedics", "Cardiology", "Neurology", "Oncology", "General Medicine"],
        "facilities": ["Operation Theater", "ICU", "Emergency", "Pharmacy", "Radiology", "Research Center"],
        "rating": 4.9,
        "emergency_available": True,
        "bed_count": 2500
    },
    {
        "id": "hosp_005",
        "name": "Medanta Hospital, Gurgaon",
        "address": "CH Baktawar Singh Road, Sector 38",
        "city": "Gurgaon",
        "phone": "+91-124-4141414",
        "email": "info@medanta.org",
        "specializations": ["Neurology", "Cardiology", "Oncology", "Gastroenterology", "Nephrology"],
        "facilities": ["Neuro ICU", "MRI Center", "CT Scan", "Emergency", "Pharmacy", "Rehabilitation"],
        "rating": 4.8,
        "emergency_available": True,
        "bed_count": 1600
    },
    {
        "id": "hosp_006",
        "name": "Kokilaben Hospital, Mumbai",
        "address": "Rao Saheb Achutrao Patwardhan Marg, Four Bunglows",
        "city": "Mumbai",
        "phone": "+91-22-30999999",
        "email": "info@kokilabenhospital.com",
        "specializations": ["Gynecology", "Obstetrics", "Cardiology", "Oncology", "Neurology"],
        "facilities": ["Labor & Delivery", "NICU", "Emergency", "Pharmacy", "IVF Center"],
        "rating": 4.7,
        "emergency_available": True,
        "bed_count": 750
    },
    {
        "id": "hosp_007",
        "name": "Nimhans Hospital, Bangalore",
        "address": "Hosur Road, Lakkasandra",
        "city": "Bangalore",
        "phone": "+91-80-26995000",
        "email": "info@nimhans.ac.in",
        "specializations": ["Psychiatry", "Neurology", "Psychology", "Neurosurgery"],
        "facilities": ["Neuro ICU", "Emergency", "Pharmacy", "Rehabilitation", "Research Center"],
        "rating": 4.8,
        "emergency_available": True,
        "bed_count": 650
    },
    {
        "id": "hosp_008",
        "name": "Fortis Hospital, Delhi",
        "address": "Okhla Road, Sukhdev Vihar Metro Station",
        "city": "Delhi",
        "phone": "+91-11-42776222",
        "email": "info@fortisdelhi.com",
        "specializations": ["Cardiology", "Orthopedics", "Oncology", "Neurology", "Gastroenterology"],
        "facilities": ["Cardiac ICU", "Emergency", "Pharmacy", "Laboratory", "Radiology"],
        "rating": 4.6,
        "emergency_available": True,
        "bed_count": 310
    },
    {
        "id": "hosp_009",
        "name": "Apollo Hospital, Mumbai",
        "address": "Tardeo Road, Mumbai Central",
        "city": "Mumbai",
        "phone": "+91-22-23508000",
        "email": "info@apollomumbai.com",
        "specializations": ["Dermatology", "Cardiology", "Oncology", "Nephrology", "Orthopedics"],
        "facilities": ["ICU", "Emergency", "Pharmacy", "Laboratory", "Radiology", "Skin Care Center"],
        "rating": 4.7,
        "emergency_available": True,
        "bed_count": 400
    },
    {
        "id": "hosp_010",
        "name": "City Hospital, Bangalore",
        "address": "MG Road, Brigade Road Junction",
        "city": "Bangalore",
        "phone": "+91-80-25588000",
        "email": "info@cityhospitalblr.com",
        "specializations": ["General Medicine", "Family Medicine", "Internal Medicine", "Pediatrics"],
        "facilities": ["Emergency", "Laboratory", "Radiology", "Pharmacy", "General OPD"],
        "rating": 4.4,
        "emergency_available": True,
        "bed_count": 200
    }
]
