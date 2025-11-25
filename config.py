import os

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))

# رسالة الترحيب في الخاص
WELCOME_MSG = """
🎉 أهلاً بك في دعم SUPPORT TV  
اختر من القائمة التالية:

1️⃣ اشتراك جديد  
2️⃣ تجديد الاشتراك  
3️⃣ دعم فني  
4️⃣ تحميل ملف القنوات  
5️⃣ التواصل مع خدمة العملاء  
"""

WHATSAPP_LINK = "https://wa.me/message/2JZ4HHC5JOSFC1"

LATEST_CHANNELS_FILE = "https://www.mediafire.com/file/2x3zvhbrg0pz8lh"  # ملف القنوات
