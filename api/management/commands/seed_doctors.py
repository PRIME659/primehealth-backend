from django.core.management.base import BaseCommand
from api.models import Doctor


class Command(BaseCommand):
    help = "Seed doctors data"

    def handle(self, *args, **kwargs):
        doctors = [
            {
                "name": "Adebayo Okonkwo",
                "specialty": "Cardiologist",
                "hospital": "Lagos University Teaching Hospital",
                "location": "Lagos, Nigeria",
                "bio": "Dr. Adebayo is a highly experienced cardiologist with over 15 years of practice.",
                "rating": 4.8,
                "availability": "available",
                "experience_years": 15,
                "consultation_fee": 15000,
            },
            {
                "name": "Ngozi Chukwu",
                "specialty": "Dermatologist",
                "hospital": "National Hospital Abuja",
                "location": "Abuja, Nigeria",
                "bio": "Dr. Ngozi specializes in skin conditions and cosmetic dermatology.",
                "rating": 4.6,
                "availability": "available",
                "experience_years": 10,
                "consultation_fee": 12000,
            },
            {
                "name": "Ibrahim Musa",
                "specialty": "Neurologist",
                "hospital": "Aminu Kano Teaching Hospital",
                "location": "Kano, Nigeria",
                "bio": "Dr. Ibrahim is a leading neurologist specializing in brain and nervous system disorders.",
                "rating": 4.9,
                "availability": "busy",
                "experience_years": 20,
                "consultation_fee": 20000,
            },
            {
                "name": "Chiamaka Johnson",
                "specialty": "Pediatrician",
                "hospital": "University of Nigeria Teaching Hospital",
                "location": "Enugu, Nigeria",
                "bio": "Dr. Chiamaka is passionate about children health and wellness.",
                "rating": 4.7,
                "availability": "available",
                "experience_years": 8,
                "consultation_fee": 10000,
            },
            {
                "name": "Emeka Obi",
                "specialty": "Orthopedist",
                "hospital": "University College Hospital",
                "location": "Ibadan, Nigeria",
                "bio": "Dr. Emeka specializes in bone and joint conditions.",
                "rating": 4.5,
                "availability": "available",
                "experience_years": 12,
                "consultation_fee": 18000,
            },
            {
                "name": "Fatima Abdullahi",
                "specialty": "Gynecologist",
                "hospital": "Garki Hospital",
                "location": "Abuja, Nigeria",
                "bio": "Dr. Fatima is dedicated to women health and reproductive care.",
                "rating": 4.8,
                "availability": "available",
                "experience_years": 14,
                "consultation_fee": 15000,
            },
            {
                "name": "Tunde Bakare",
                "specialty": "General Practitioner",
                "hospital": "Lagos Island General Hospital",
                "location": "Lagos, Nigeria",
                "bio": "Dr. Tunde provides comprehensive primary healthcare services.",
                "rating": 4.4,
                "availability": "available",
                "experience_years": 7,
                "consultation_fee": 8000,
            },
            {
                "name": "Aisha Yusuf",
                "specialty": "Psychiatrist",
                "hospital": "Federal Neuropsychiatric Hospital",
                "location": "Kaduna, Nigeria",
                "bio": "Dr. Aisha specializes in mental health and psychiatric care.",
                "rating": 4.7,
                "availability": "available",
                "experience_years": 11,
                "consultation_fee": 16000,
            },
        ]

        Doctor.objects.all().delete()

        for doc in doctors:
            Doctor.objects.create(**doc)
            self.stdout.write(self.style.SUCCESS(f"Created doctor: Dr. {doc['name']}"))

        self.stdout.write(self.style.SUCCESS("Doctors seeded successfully!"))
