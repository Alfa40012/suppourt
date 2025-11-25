from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import re
from config import BOT_TOKEN, ADMIN_ID, WELCOME_MSG, WHATSAPP_LINK, LATEST_CHANNELS_FILE

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

# =========================
# 1) MENUS
# =========================

def main_menu():
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton("📡 اشتراك جديد", callback_data="new_sub"),
        InlineKeyboardButton("♻️ تجديد الاشتراك", callback_data="renew"),
    )
    kb.add(
        InlineKeyboardButton("🛠 دعم فني", callback_data="support"),
        InlineKeyboardButton("📥 تحميل ملف القنوات", callback_data="channels"),
    )
    kb.add(
        InlineKeyboardButton("📞 تواصل مع خدمة العملاء", url=WHATSAPP_LINK)
    )
    return kb


def support_menu():
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton("📝 إرسال المشكلة هنا", callback_data="write_issue"),
        InlineKeyboardButton("📞 واتساب الدعم", url=WHATSAPP_LINK),
    )
    return kb


# =========================
# 2) START / ADMIN
# =========================

@dp.message_handler(commands=["start"])
async def start_message(msg: types.Message):
    # في الخاص
    if msg.chat.type == "private":
        await msg.answer("🎬 SUPPORT TV\n" + WELCOME_MSG, reply_markup=main_menu())
    else:
        await msg.reply("✅ البوت شغال، ابعتلي /start في الخاص للمنيو.")


@dp.message_handler(commands=["admin", "Admin"])
async def admin_panel(msg: types.Message):
    if msg.from_user.id != ADMIN_ID:
        return
    chat = msg.chat
    await msg.answer(
        f"📊 لوحة ADMIN\n"
        f"👥 Chat: {chat.title if chat.title else chat.id}\n"
        f"💬 ID: {chat.id}\n"
        f"✅ البوت شغال بدون مشاكل ظاهرًا."
    )


# =========================
# 3) CALLBACK BUTTONS
# =========================

@dp.callback_query_handler(lambda c: True)
async def callbacks(call: types.CallbackQuery):

    if call.data == "new_sub":
        await call.message.answer(
            "💳 لعمل اشتراك جديد:\n\n"
            "• اكتب نوع الجهاز\n"
            "• الدولة / المدينة\n"
            "• عدد الشهور المطلوبة\n\n"
            "وهيتم الرد عليك من الدعم."
        )

    elif call.data == "renew":
        await call.message.answer(
            "♻️ لتجديد الاشتراك:\n\n"
            "أرسل رقم الـ MAC أو الـ Username الخاص بحسابك، "
            "وهنرد عليك بقيمة التجديد وطريقة الدفع."
        )

    elif call.data == "support":
        await call.message.answer(
            "🛠 دعم فني SUPPORT TV\n"
            "اكتب مشكلتك بالتفصيل أو ابعت صورة/فيديو قصير للمشكلة.\n"
            "هيتم تحويل رسالتك للدعم الفني.",
            reply_markup=support_menu()
        )

    elif call.data == "write_issue":
        await call.message.answer("📝 تمام، اكتب مشكلتك هنا في رسالة جديدة.")

    elif call.data == "channels":
        await call.message.answer("📥 أحدث ملف قنوات عربي:\n👇")
        await call.message.answer(LATEST_CHANNELS_FILE)

    await call.answer()


# =========================
# 4) WELCOME MESSAGE IN GROUPS
# =========================

@dp.message_handler(content_types=types.ContentTypes.NEW_CHAT_MEMBERS)
async def welcome_new_members(msg: types.Message):
    for user in msg.new_chat_members:
        if user.is_bot:
            continue
        await msg.reply(
            f"🎉 أهلاً بك يا {user.first_name} في مجموعة SUPPORT TV\n"
            "للاشتراك أو التجديد أو الدعم الفني:\n"
            "• اكتب كلمة (اشتراك) أو (تجديد) أو (دعم)\n"
            "أو راسلنا في الخاص عن طريق فتح البوت ثم /start."
        )


# =========================
# 5) SIMPLE ANTI-SPAM + KEYWORD AUTO REPLIES
# =========================

# كلمات ممنوعة (تقدر تزود براحتك)
BLOCKED_WORDS = ["بوت مجاني", "قنوات ببلاش", "اشترك معايا مش معاهم"]
LINK_REGEX = re.compile(r"(https?://|t\.me/|telegram\.me/)")

def looks_like_mac(text: str) -> str:
    """
    يحاول يكتشف لو الرسالة فيها MAC
    أمثلة: 00:11:22:AA:BB:CC أو 001122AABBCC
    """
    mac_pattern = re.compile(r"([0-9A-Fa-f]{2}[:\-]){5}[0-9A-Fa-f]{2}")
    mac_pattern2 = re.compile(r"[0-9A-Fa-f]{12}")
    m1 = mac_pattern.search(text)
    if m1:
        return m1.group(0)
    m2 = mac_pattern2.search(text.replace(" ", ""))
    if m2:
        return m2.group(0)
    return ""


@dp.message_handler(content_types=types.ContentTypes.TEXT)
async def handle_messages(msg: types.Message):
    text = msg.text or ""

    # ========== داخل الجروبات ==========
    if msg.chat.type in ["group", "supergroup"]:

        lower = text.lower()

        # 1) مكافحة سبام بسيط
        links = len(LINK_REGEX.findall(text))
        if links >= 3 or any(w in lower for w in [w.lower() for w in BLOCKED_WORDS]):
            try:
                await msg.delete()
                await msg.answer(
                    "⚠️ تم حذف رسالة يُشتبه أنها سبام.\n"
                    "من فضلك التزم بقواعد المجموعة."
                )
            except Exception:
                pass
            return

        # 2) ردود تلقائية على كلمات مفتاحية
        if "سعر" in lower or "الاسعار" in lower:
            await msg.reply("💰 الأسعار بالتفصيل على الخاص، افتح البوت SUPPORT TV ثم اكتب /start.")
            return

        if "اشتراك" in lower:
            await msg.reply("📡 للاشتراك الجديد: اكتب نوع جهازك + بلدك + عدد الشهور المطلوبة.")
            return

        if "تجديد" in lower:
            await msg.reply("♻️ لتجديد الاشتراك: ابعت الـ MAC أو الـ Username وسيتم الرد عليك.")
            return

        if "ملف قنوات" in lower or "ملف القنوات" in lower:
            await msg.reply(f"📥 أحدث ملف قنوات عربي:\n{LATEST_CHANNELS_FILE}")
            return

        if "دعم" in lower or "مشكلة" in lower:
            await msg.reply("🛠 اكتب مشكلتك بالتفصيل، وسيتم تحويلها للدعم الفني.")
            # نرسل إشعار للأدمن
            try:
                await bot.send_message(
                    ADMIN_ID,
                    f"⚠️ طلب دعم جديد في الجروب {msg.chat.title} من @{msg.from_user.username} ({msg.from_user.id})\n"
                    f"الرسالة:\n{text}"
                )
            except Exception:
                pass
            return

        # 3) كشف MAC تلقائي
        mac = looks_like_mac(text)
        if mac:
            await msg.reply("✅ تم استلام كود الجهاز، سيتم فحصه من الدعم الفني.")
            if ADMIN_ID:
                try:
                    await bot.send_message(
                        ADMIN_ID,
                            f"📡 تم إرسال MAC في الجروب {msg.chat.title}:\n"
                            f"👤 المستخدم: @{msg.from_user.username} ({msg.from_user.id})\n"
                            f"🔢 MAC: {mac}"
                    )
                except Exception:
                    pass
            return

    # ========== في الخاص ==========
    else:
        # أي رسالة في الخاص لو مش أمر /start نخليها دعم فني
        if not text.startswith("/"):
            await msg.answer(
                "📝 تم استلام رسالتك، وسيتم مراجعتها من الدعم الفني.\n"
                "لو تحتاج اشتراك
