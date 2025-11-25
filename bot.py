from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import asyncio
from config import BOT_TOKEN, ADMIN_ID, WELCOME_MSG

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)


# زرار المنيو الرئيسية
def main_menu():
    kb = InlineKeyboardMarkup()
    kb.add(
        InlineKeyboardButton("📡 اشتراك جديد", callback_data="new_sub"),
        InlineKeyboardButton("♻️ تجديد الاشتراك", callback_data="renew"),
    )
    kb.add(
        InlineKeyboardButton("🛠 دعم فني", callback_data="support"),
        InlineKeyboardButton("📥 تحميل ملف القنوات", callback_data="channels"),
    )
    kb.add(
        InlineKeyboardButton("📞 تواصل مع خدمة العملاء", url="https://wa.me/message/2JZ4HHC5JOSFC1")
    )
    return kb


# رسالة البداية
@dp.message_handler(commands=["start"])
async def start_message(msg: types.Message):
    await msg.answer(WELCOME_MSG, reply_markup=main_menu())


# استقبال الأزرار
@dp.callback_query_handler(lambda c: True)
async def callbacks(call: types.CallbackQuery):

    if call.data == "new_sub":
        await call.message.answer("💳 لإجراء اشتراك جديد: \n\nارسل اسم جهازك + دولتك.")
    
    elif call.data == "renew":
        await call.message.answer("♻️ لتجديد الاشتراك:\n\nأرسل رقم MAC أو username.")

    elif call.data == "support":
        await call.message.answer("🛠 اكتب مشكلتك وسيتم الرد عليك فورًا.")
        await bot.send_message(ADMIN_ID, f"⚠️ {call.from_user.id} طلب دعم فني.")

    elif call.data == "channels":
        await call.message.answer("📥 أحدث ملف قنوات عربي:\n👇")
        await call.message.answer("https://www.mediafire.com/file/2x3zvhbrg0pz8lh")
    
    await call.answer()


# استقبال رسائل الجروب (لو البوت ادمِن)
@dp.message_handler(content_types=types.ContentTypes.TEXT)
async def group_messages(msg: types.Message):

    # رد تلقائي لو حد كتب "سعر"
    if msg.chat.type in ["group", "supergroup"]:
        text = msg.text.lower()

        if "سعر" in text:
            await msg.reply("💰 الأسعار على الخاص… ابعت /start")


# تشغيل البوت
if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
