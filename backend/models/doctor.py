from pydantic import BaseModel
from typing import List, Optional

class Doctor(BaseModel):
    id: str
    name: str
    specialization: str
    experience_years: int
    consultation_fee: float
    available_days: List[str]
    available_time_slots: List[str]
    hospital: str
    image_url: Optional[str] = None
    rating: Optional[float] = 4.5
    patients_count: Optional[int] = 0

# Sample doctors data
DOCTORS_DATA = [
    {
        "id": "doc_001",
        "name": "Dr. Sarah Johnson",
        "specialization": "Cardiologist",
        "experience_years": 15,
        "consultation_fee": 150.00,
        "available_days": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"],
        "available_time_slots": ["09:00 AM", "10:00 AM", "11:00 AM", "12:00 PM", "01:00 PM", "02:00 PM", "03:00 PM"],
        "hospital": "Apollo Hospital, Delhi",
        "image_url": None,
        "rating": 4.8,
        "patients_count": 1250
    },
    {
        "id": "doc_002",
        "name": "Dr. Michael Chen",
        "specialization": "Dermatologist",
        "experience_years": 10,
        "consultation_fee": 120.00,
        "available_days": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"],
        "available_time_slots": ["09:00 AM", "10:00 AM", "11:00 AM", "12:00 PM", "01:00 PM", "02:00 PM", "03:00 PM"],
        "hospital": "Fortis Hospital, Mumbai",
        "image_url": None,
        "rating": 4.6,
        "patients_count": 890
    },
    {
        "id": "doc_003",
        "name": "Dr. Emily Williams",
        "specialization": "Pediatrician",
        "experience_years": 12,
        "consultation_fee": 100.00,
        "available_days": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"],
        "available_time_slots": ["09:00 AM", "10:00 AM", "11:00 AM", "12:00 PM", "01:00 PM", "02:00 PM", "03:00 PM"],
        "hospital": "Max Hospital, Delhi",
        "image_url": None,
        "rating": 4.9,
        "patients_count": 2100
    },
    {
        "id": "doc_004",
        "name": "Dr. James Brown",
        "specialization": "Orthopedic Surgeon",
        "experience_years": 20,
        "consultation_fee": 200.00,
        "available_days": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"],
        "available_time_slots": ["09:00 AM", "10:00 AM", "11:00 AM", "12:00 PM", "01:00 PM", "02:00 PM", "03:00 PM"],
        "hospital": "AIIMS Hospital, Delhi",
        "image_url": None,
        "rating": 4.7,
        "patients_count": 980
    },
    {
        "id": "doc_005",
        "name": "Dr. Lisa Anderson",
        "specialization": "Neurologist",
        "experience_years": 18,
        "consultation_fee": 180.00,
        "available_days": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"],
        "available_time_slots": ["09:00 AM", "10:00 AM", "11:00 AM", "12:00 PM", "01:00 PM", "02:00 PM", "03:00 PM"],
        "hospital": "Medanta Hospital, Gurgaon",
        "image_url": None,
        "rating": 4.8,
        "patients_count": 750
    },
    {
        "id": "doc_006",
        "name": "Dr. Robert Martinez",
        "specialization": "General Physician",
        "experience_years": 8,
        "consultation_fee": 80.00,
        "available_days": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"],
        "available_time_slots": ["09:00 AM", "10:00 AM", "11:00 AM", "12:00 PM", "01:00 PM", "02:00 PM", "03:00 PM"],
        "hospital": "City Hospital, Bangalore",
        "image_url": None,
        "rating": 4.5,
        "patients_count": 3200
    },
    {
        "id": "doc_007",
        "name": "Dr. Amanda Thompson",
        "specialization": "Gynecologist",
        "experience_years": 14,
        "consultation_fee": 140.00,
        "available_days": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"],
        "available_time_slots": ["09:00 AM", "10:00 AM", "11:00 AM", "12:00 PM", "01:00 PM", "02:00 PM", "03:00 PM"],
        "hospital": "Kokilaben Hospital, Mumbai",
        "image_url": None,
        "rating": 4.9,
        "patients_count": 1800
    },
    {
        "id": "doc_008",
        "name": "Dr. David Wilson",
        "specialization": "Psychiatrist",
        "experience_years": 16,
        "consultation_fee": 160.00,
        "available_days": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"],
        "available_time_slots": ["09:00 AM", "10:00 AM", "11:00 AM", "12:00 PM", "01:00 PM", "02:00 PM", "03:00 PM"],
        "hospital": "Nimhans Hospital, Bangalore",
        "image_url": None,
        "rating": 4.7,
        "patients_count": 620
    },
    {
        "id": "doc_009",
        "name": "Dr. Priya Sharma",
        "specialization": "Cardiologist",
        "experience_years": 12,
        "consultation_fee": 140.00,
        "available_days": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"],
        "available_time_slots": ["09:00 AM", "10:00 AM", "11:00 AM", "12:00 PM", "01:00 PM", "02:00 PM", "03:00 PM"],
        "hospital": "Fortis Hospital, Delhi",
        "image_url": None,
        "rating": 4.7,
        "patients_count": 920
    },
    {
        "id": "doc_010",
        "name": "Dr. Rahul Gupta",
        "specialization": "Dermatologist",
        "experience_years": 8,
        "consultation_fee": 110.00,
        "available_days": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"],
        "available_time_slots": ["09:00 AM", "10:00 AM", "11:00 AM", "12:00 PM", "01:00 PM", "02:00 PM", "03:00 PM"],
        "hospital": "Apollo Hospital, Mumbai",
        "image_url": None,
        "rating": 4.5,
        "patients_count": 650
    }
]
