"""
Medical Query Validator Service
Validates that user queries are medical-related and rejects non-medical queries.
Also handles greeting messages.
"""

import re
from typing import Tuple, Optional

class GreetingHandler:
    """Handles user greetings"""
    
    GREETINGS = {
        # Simple greetings
        'hi': 'Hello! 👋 How can I assist you with your medical needs today?',
        'hello': 'Hello! 👋 Welcome to your Medical Assistant. How can I help?',
        'hey': 'Hey there! 👋 What health-related questions do you have?',
        'hiya': 'Hiya! 👋 I\'m here to help with your medical concerns.',
        'greetings': 'Greetings! 👋 I\'m your medical assistant. What can I help you with?',
        
        # Time-based greetings
        'good morning': 'Good morning! ☀️ I hope you\'re having a great day. How can I help you medically?',
        'good afternoon': 'Good afternoon! 🌤️ How can I assist you with your health today?',
        'good evening': 'Good evening! 🌙 What medical questions do you have?',
        'good night': 'Good night! 😴 Sleep well, but feel free to reach out anytime you have health concerns.',
        
        # Casual greetings
        'sup': 'Hey! 👋 What\'s up? How can I help with your health?',
        'whats up': 'Not much! 👋 How can I assist you today?',
        'how are you': 'I\'m doing well, thank you for asking! 😊 How can I help you with your health?',
        'how are you doing': 'I\'m great, thanks for asking! 😊 How can I assist you medically?',
        'how are you doing today': 'I\'m doing wonderfully! 😊 How about you? What brings you here today?',
        'how you doing': 'I\'m doing well, thanks! 😊 How can I help you?',
        'nice to meet you': 'Nice to meet you too! 😊 I\'m here to help with all your medical needs.',
        'thanks': 'You\'re welcome! 😊 Anything else I can help you with?',
        'thank you': 'You\'re welcome! 😊 Happy to help with your health concerns.',
        'thanks for helping': 'Anytime! 😊 That\'s what I\'m here for. Is there anything else you need?',
    }
    
    @staticmethod
    def is_greeting(query: str) -> bool:
        """Check if query is a greeting"""
        if not query or not query.strip():
            return False
        
        query_lower = query.lower().strip()
        # Remove punctuation
        query_cleaned = re.sub(r'[!?.]+', '', query_lower)
        
        return query_cleaned in GreetingHandler.GREETINGS
    
    @staticmethod
    def get_greeting_response(query: str) -> Optional[str]:
        """Get response for greeting query"""
        if not query or not query.strip():
            return None
        
        query_lower = query.lower().strip()
        # Remove punctuation
        query_cleaned = re.sub(r'[!?.]+', '', query_lower)
        
        return GreetingHandler.GREETINGS.get(query_cleaned)


class QueryValidatorService:
    """Validates if a query is medical-related"""
    
    # Non-medical keywords that should be rejected
    NON_MEDICAL_KEYWORDS = {
        # Programming/Development
        'python', 'javascript', 'java', 'code', 'programming', 'coding', 'debug', 'function',
        'variable', 'algorithm', 'database', 'sql', 'api', 'framework', 'library', 'react',
        'node.js', 'npm', 'html', 'css', 'typescript', 'git', 'github', 'repo', 'commit',
        
        # Math/Academic
        'calculus', 'algebra', 'geometry', 'trigonometry', 'integral', 'derivative', 'matrix',
        'equation', 'theorem', 'proof', 'solve', 'equation', 'math homework', 'physics homework',
        'chemistry homework', 'biology homework', 'statistics', 'probability', 'permutation',
        'combination', 'formula', 'arithmetic', 'factorize', 'prime number',
        
        # General Knowledge/Non-medical
        'write my essay', 'help with homework', 'translate', 'weather', 'sports', 'movie',
        'game', 'restaurant', 'cooking recipe', 'travel', 'politics', 'news', 'stock',
        'cryptocurrency', 'joke', 'riddle', 'story', 'song lyrics', 'write poem',
        
        # Non-medical tech
        'how to hack', 'how to crack', 'password reset', 'wifi password', 'how to cheat',
        'pirate', 'torrent', 'download movie', 'download music',
    }
    
    # Medical-related keywords that should always be allowed
    MEDICAL_KEYWORDS = {
        'symptom', 'disease', 'illness', 'treatment', 'medicine', 'drug', 'medication',
        'doctor', 'hospital', 'appointment', 'health', 'medical', 'patient', 'diagnosis',
        'blood', 'pressure', 'sugar', 'heart', 'pain', 'fever', 'cough', 'cold',
        'vaccine', 'infection', 'virus', 'bacteria', 'allergy', 'asthma', 'diabetes',
        'cancer', 'surgery', 'therapy', 'rehabilitation', 'physical', 'mental',
        'consultation', 'prescription', 'test', 'scan', 'xray', 'ultrasound', 'mri',
        'lab', 'examination', 'check-up', 'checkup', 'clinic', 'medical record',
        'emergency', 'first aid', 'wound', 'fracture', 'sprain', 'burn', 'poison',
        'pregnancy', 'pregnancy test', 'prenatal', 'postnatal', 'delivery',
        'pediatrics', 'pediatrician', 'dermatology', 'dermatologist', 'cardiology',
        'psychiatry', 'orthopedic', 'neurology', 'oncology', 'ophthalmology',
        'specialist', 'specialization', 'available days', 'time slots', 'fee',
        'book', 'appointment', 'schedule', 'reschedule', 'cancel', 'rating',
    }
    
    # Patterns that indicate appointment/hospital/doctor related queries (allowed)
    APPOINTMENT_PATTERNS = [
        r'book.*appointment',
        r'schedule.*appointment',
        r'show.*doctor',
        r'list.*doctor',
        r'available.*doctor',
        r'find.*doctor',
        r'show.*hospital',
        r'list.*hospital',
        r'find.*hospital',
        r'my.*appointment',
        r'my.*booking',
        r'cancel.*appointment',
        r'reschedule.*appointment',
        r'view.*appointment',
        r'change password',
        r'profile',
    ]
    
    @staticmethod
    def is_medical_query(query: str) -> Tuple[bool, Optional[str]]:
        """
        Validate if a query is medical-related.
        
        Returns:
            Tuple of (is_medical: bool, rejection_message: Optional[str])
            - If medical query: (True, None)
            - If non-medical: (False, rejection_message)
        """
        if not query or not query.strip():
            return True, None  # Allow empty queries
        
        query_lower = query.lower().strip()
        
        # Check if it matches appointment/hospital/doctor patterns (always allowed)
        for pattern in QueryValidatorService.APPOINTMENT_PATTERNS:
            if re.search(pattern, query_lower):
                return True, None
        
        # Check for medical keywords (positive indicator)
        words = re.findall(r'\b[\w]+\b', query_lower)
        medical_keyword_count = sum(1 for word in words if word in QueryValidatorService.MEDICAL_KEYWORDS)
        
        # If it has medical keywords, it's likely a medical query
        if medical_keyword_count > 0:
            return True, None
        
        # Check for non-medical keywords (negative indicator)
        non_medical_keyword_count = sum(1 for word in words if word in QueryValidatorService.NON_MEDICAL_KEYWORDS)
        
        if non_medical_keyword_count > 0:
            return False, QueryValidatorService._get_rejection_message(query)
        
        # Default: Allow the query if we're unsure (be lenient)
        # The LLM system prompt will enforce medical focus anyway
        return True, None
    
    @staticmethod
    def _get_rejection_message(query: str) -> str:
        """Generate a rejection message for non-medical queries"""
        
        # Determine the type of query to provide a more specific message
        query_lower = query.lower()
        
        if any(word in query_lower for word in ['python', 'code', 'javascript', 'java', 'programming', 'function']):
            return (
                "❌ I'm designed specifically for medical assistance. "
                "I can't help with programming or coding questions.\n\n"
                "However, I'm here to help with:\n"
                "✅ Medical symptoms and conditions\n"
                "✅ Health information and treatments\n"
                "✅ Doctor and hospital information\n"
                "✅ Appointment booking\n\n"
                "What medical question can I help you with?"
            )
        
        elif any(word in query_lower for word in ['math', 'algebra', 'calculus', 'homework', 'equation', 'formula']):
            return (
                "❌ I'm specialized in medical assistance, not mathematics or academic subjects.\n\n"
                "I'm here to help with:\n"
                "✅ Medical symptoms and conditions\n"
                "✅ Health information and treatments\n"
                "✅ Doctor and hospital information\n"
                "✅ Appointment booking\n\n"
                "Do you have any medical questions?"
            )
        
        elif any(word in query_lower for word in ['recipe', 'cooking', 'weather', 'sports', 'movie', 'game']):
            return (
                "❌ I specialize in medical assistance, not general information.\n\n"
                "I can help with:\n"
                "✅ Medical symptoms and conditions\n"
                "✅ Health information and treatments\n"
                "✅ Doctor and hospital information\n"
                "✅ Appointment booking\n\n"
                "Do you have a health-related question?"
            )
        
        else:
            return (
                "❌ That question isn't related to medical or health topics.\n\n"
                "I'm your Medical Assistant and can help with:\n"
                "✅ Medical symptoms and conditions\n"
                "✅ Health information and treatments\n"
                "✅ Doctor and hospital information\n"
                "✅ Appointment booking\n"
                "✅ Medical records and profile management\n\n"
                "Please ask me about your health or medical needs!"
            )


# Create singleton instance
query_validator = QueryValidatorService()
