from django.core.management.base import BaseCommand
from api.models import MedicalTip


class Command(BaseCommand):
    help = "Seed medical tips data"

    def handle(self, *args, **kwargs):
        tips = [
            {
                "title": "Stay Hydrated",
                "content": "Drink at least 8 glasses of water daily. Proper hydration helps maintain body temperature, transport nutrients and remove waste products.",
                "category": "general",
                "icon": "💧",
            },
            {
                "title": "Exercise Regularly",
                "content": "Aim for at least 30 minutes of moderate physical activity most days of the week. Regular exercise reduces the risk of heart disease, diabetes and depression.",
                "category": "fitness",
                "icon": "🏃",
            },
            {
                "title": "Eat More Vegetables",
                "content": "Fill half your plate with vegetables at every meal. Vegetables are rich in vitamins, minerals and fiber that support overall health.",
                "category": "nutrition",
                "icon": "🥦",
            },
            {
                "title": "Get Enough Sleep",
                "content": "Adults need 7-9 hours of sleep per night. Good sleep improves brain function, mood and overall health.",
                "category": "sleep",
                "icon": "😴",
            },
            {
                "title": "Manage Stress",
                "content": "Practice stress management techniques like deep breathing, meditation or yoga. Chronic stress can lead to serious health problems.",
                "category": "mental_health",
                "icon": "🧘",
            },
            {
                "title": "Wash Your Hands",
                "content": "Wash your hands frequently with soap and water for at least 20 seconds. This is one of the most effective ways to prevent the spread of infections.",
                "category": "hygiene",
                "icon": "🧼",
            },
            {
                "title": "Monitor Blood Pressure",
                "content": "Check your blood pressure regularly. High blood pressure often has no symptoms but can lead to heart attack and stroke if untreated.",
                "category": "heart_health",
                "icon": "❤️",
            },
            {
                "title": "Limit Sugar Intake",
                "content": "Reduce consumption of sugary drinks and processed foods. Excess sugar contributes to obesity, diabetes and tooth decay.",
                "category": "diabetes",
                "icon": "🍬",
            },
            {
                "title": "Eat Breakfast Daily",
                "content": "Never skip breakfast. A healthy breakfast provides energy, improves concentration and helps maintain a healthy weight.",
                "category": "nutrition",
                "icon": "🍳",
            },
            {
                "title": "Practice Deep Breathing",
                "content": "Take 5 minutes daily to practice deep breathing exercises. This reduces stress, lowers blood pressure and improves focus.",
                "category": "mental_health",
                "icon": "🌬️",
            },
            {
                "title": "Walk More",
                "content": "Take the stairs instead of the elevator and park farther away. Even small increases in daily walking can significantly improve cardiovascular health.",
                "category": "fitness",
                "icon": "🚶",
            },
            {
                "title": "Reduce Salt Intake",
                "content": "Limit sodium to less than 2300mg per day. Too much salt raises blood pressure and increases the risk of heart disease.",
                "category": "heart_health",
                "icon": "🧂",
            },
        ]

        MedicalTip.objects.all().delete()

        for tip in tips:
            MedicalTip.objects.create(**tip)
            self.stdout.write(self.style.SUCCESS(f"Created tip: {tip['title']}"))

        self.stdout.write(self.style.SUCCESS("Medical tips seeded successfully!"))
