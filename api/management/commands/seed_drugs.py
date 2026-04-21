from django.core.management.base import BaseCommand
from api.models import Drug


class Command(BaseCommand):
    help = "Seed drugs data"

    def handle(self, *args, **kwargs):
        drugs = [
            {
                "name": "Coartem",
                "category": "antimalaria",
                "description": "Used for treatment of acute uncomplicated malaria.",
                "dosage": "Adults: 4 tablets twice daily for 3 days. Children: dose based on weight.",
                "price": 3500,
                "stock": 100,
                "manufacturer": "Novartis",
            },
            {
                "name": "Amoxicillin",
                "category": "antibiotics",
                "description": "A penicillin antibiotic used to treat bacterial infections.",
                "dosage": "Adults: 250-500mg every 8 hours. Children: 25mg/kg/day in divided doses.",
                "price": 1500,
                "stock": 200,
                "manufacturer": "GSK",
            },
            {
                "name": "Paracetamol",
                "category": "analgesics",
                "description": "Used to treat pain and fever.",
                "dosage": "Adults: 500-1000mg every 4-6 hours. Max 4g per day.",
                "price": 500,
                "stock": 500,
                "manufacturer": "May & Baker",
            },
            {
                "name": "Lisinopril",
                "category": "antihypertensive",
                "description": "Used to treat high blood pressure and heart failure.",
                "dosage": "Adults: 10mg once daily. May increase to 40mg.",
                "price": 2500,
                "stock": 150,
                "manufacturer": "Emzor",
            },
            {
                "name": "Metformin",
                "category": "antidiabetic",
                "description": "Used to treat type 2 diabetes.",
                "dosage": "Adults: 500mg twice daily with meals. Max 2550mg per day.",
                "price": 2000,
                "stock": 120,
                "manufacturer": "Fidson",
            },
            {
                "name": "Vitamin C",
                "category": "vitamins",
                "description": "Essential vitamin for immune system support.",
                "dosage": "Adults: 500-1000mg daily.",
                "price": 800,
                "stock": 300,
                "manufacturer": "Health Aid",
            },
            {
                "name": "Azithromycin",
                "category": "antibiotics",
                "description": "Antibiotic used to treat various bacterial infections.",
                "dosage": "Adults: 500mg on day 1, then 250mg daily for 4 days.",
                "price": 3000,
                "stock": 80,
                "manufacturer": "Pfizer",
            },
            {
                "name": "Ibuprofen",
                "category": "analgesics",
                "description": "Used to treat pain, fever and inflammation.",
                "dosage": "Adults: 200-400mg every 4-6 hours. Max 1200mg per day.",
                "price": 700,
                "stock": 400,
                "manufacturer": "Sterling",
            },
            {
                "name": "Amlodipine",
                "category": "antihypertensive",
                "description": "Calcium channel blocker for high blood pressure.",
                "dosage": "Adults: 5mg once daily. May increase to 10mg.",
                "price": 1800,
                "stock": 100,
                "manufacturer": "Emzor",
            },
            {
                "name": "Vitamin D3",
                "category": "vitamins",
                "description": "Supports bone health and immune function.",
                "dosage": "Adults: 1000-2000 IU daily.",
                "price": 1200,
                "stock": 250,
                "manufacturer": "Health Aid",
            },
        ]

        Drug.objects.all().delete()

        for drug in drugs:
            Drug.objects.create(**drug)
            self.stdout.write(self.style.SUCCESS(f"Created drug: {drug['name']}"))

        self.stdout.write(self.style.SUCCESS("Drugs seeded successfully!"))
