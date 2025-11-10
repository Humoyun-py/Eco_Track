import requests
import json

class NewsAPI:
    def __init__(self):
        self.base_url = "https://newsapi.org/v2"
        self.api_key = "YOUR_NEWS_API_KEY"  # Iltimos, haqiqiy API key oling
    
    def get_eco_news(self):
        """Get environmental news"""
        try:
            # Demo ma'lumotlar (haqiqiy API ishlamaganda)
            demo_news = [
                {
                    "title": "Yangi qayta ishlash loyihasi ishga tushirildi",
                    "description": "Shaharda yangi qayta ishlash markazi ochildi",
                    "source": "EcoNews"
                },
                {
                    "title": "Quyosh energiyasidan foydalanish oshdi",
                    "description": "Quyosh panelari narxlari 20% kamaydi",
                    "source": "GreenTech"
                },
                {
                    "title": "Suv tejash bo'yicha yangi texnologiya",
                    "description": "Smart suv hisoblagichlari joriy etildi",
                    "source": "WaterSave"
                }
            ]
            
            return demo_news
        
        except Exception as e:
            # Agar API ishlamasa, demo ma'lumotlarni qaytarish
            return [
                {
                    "title": "Ekologik yangiliklar",
                    "description": "Yangiliklar tez orada yangilanadi",
                    "source": "EcoVerse"
                }
            ]