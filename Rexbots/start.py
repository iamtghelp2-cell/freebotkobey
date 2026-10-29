# ========================================================
# IamTGHelp - Advanced Restricted Content Saver & Smart Router
# Powered & Maintained by: @iamtghelp
# All-In-One Production Ready Engine
# ========================================================

import os
import re
import shlex
import asyncio
import random
import time
import shutil
import pyrogram
from datetime import datetime, timedelta
from pyrogram import Client, filters, enums
from pyrogram.errors import (
    FloodWait, UserIsBlocked, InputUserDeactivated, UserAlreadyParticipant,
    InviteHashExpired, UsernameNotOccupied, AuthKeyUnregistered
)
from pyrogram.types import (
    InlineKeyboardMarkup, InlineKeyboardButton, Message, 
    CallbackQuery, BotCommand
)
from config import API_ID, API_HASH, ADMINS, LOG_CHANNEL
from database.db import db
from logger import LOGGER

logger = LOGGER(__name__)

REACTIONS = ["👍", "❤️", "🔥", "🥰", "👏", "😁", "🎉", "🤩", "⚡", "💯"]

class script(object):
    START_TXT = """<b>👋 नमस्ते {},</b>

<b>🤖 मैं हूँ <a href="https://t.me/iamtghelp">IamTGHelp Save Bot</a></b>
<i>आपका हाई-स्पीड रेस्ट्रिक्टेड कंटेंट सेवर और स्मार्ट टॉपिक राउटर बॉट।</i>

<blockquote><b>⚡ ब्रांडिंग: IamTGHelp Official</b>
<b>🚀 स्टेटस: 🟢 ऑनलाइन (असीमित मोड)</b>
<b>🎯 ऑटो टॉपिक रूटिंग: सक्रिय (Forum Topics Supported)</b>
<b>📊 स्पीड: डायरेक्ट सर्वर-साइड क्लोनिंग (No Black Screen)</b></blockquote>

<b>👇 नीचे दिए गए मेनू से अपनी सेटिंग्स मैनेज करें या /help भेजें:</b>"""

    HELP_TXT = """<b>📚 संपूर्ण गाइड और मुख्य फीचर्स:</b>

<blockquote><b>🎯 1. टॉपिक और ग्रुप फॉरवर्डिंग (Smart Routing):</b></blockquote>
• <code>/setchat -100xxxxxxxxxx</code> - टारगेट सुपरग्रुप सेट करें
• <code>/clearchat</code> - फॉरवर्डिंग बंद करें (फाइलें बॉट DM में आएँगी)
• <code>/settopic &lt;topic_id&gt;</code> - डिफ़ॉल्ट टॉपिक ID सेट करें
• <code>/set_topics</code> - विषय अनुसार टॉपिक लिंक जोड़ें
• <code>/show_topics</code> - सक्रिय टॉपिक लिस्ट देखें
• <code>/reset_topics</code> - टॉपिक सेटिंग्स साफ़ करें

<blockquote><b>⚡ 2. मुख्य डाउनलोड व बैच टूल्स:</b></blockquote>
• <code>/batch</code> - बल्क मैसेज एक्सट्रैक्शन शुरू करें
• <code>/dl &lt;url&gt;</code> - सपोर्टेड साइट्स से वीडियो डाउनलोड करें
• <code>/adl &lt;url&gt;</code> - सपोर्टेड साइट्स से ऑडियो डाउनलोड करें
• <code>/login</code> - प्राइवेट चैनल/ग्रुप एक्सेस के लिए लॉगिन
• <code>/logout</code> - बॉट से लॉगआउट करें
• <code>/cancel</code> - चल रहे बैच टास्क को तुरंत रोकें

<blockquote><b>💎 3. प्रीमियम व सब्सक्रिप्शन:</b></blockquote>
• <code>/plan</code> - उपलब्ध प्रीमियम प्लान देखें
• <code>/myplan</code> - अपना एक्टिव प्लान स्टेटस चेक करें
• <code>/pay</code> - प्रीमियम सब्सक्रिप्शन खरीदें
• <code>/redeem &lt;code&gt;</code> - प्रीमियम प्रोमो कोड रिडीम करें
• <code>/transfer &lt;user_id&gt;</code> - अपना प्रीमियम किसी और को गिफ़्ट करें

<blockquote><b>⚙️ 4. पर्सनल सेटिंग्स व क्लीनर:</b></blockquote>
• <code>/settings</code> - पूरा इनलाइन डैशबोर्ड खोलें
• <code>/clean_ads</code> - अन्य चैनलों के प्रोमो ऑटो-डिलीट करें
• <code>/replace 'पुराना' 'नया'</code> - शब्द या नाम बदलें
• <code>/speedtest</code> - सर्वर स्पीड टेस्ट करें"""

    TERMS_TXT = """<b>📜 नियम एवं शर्तें (Terms & Conditions):</b>

1. इस बॉट का उपयोग केवल व्यक्तिगत और शैक्षिक अध्ययन के लिए करें।
2. किसी भी प्रकार की स्पैमिंग या कॉपीराइट उल्लंघन की जिम्मेदारी उपयोगकर्ता की होगी।
3. सर्वर पर अत्यधिक लोड से बचने के लिए एक समय में एक ही बैच प्रोसेस चलाएँ।"""

class batch_temp(object):
    IS_BATCH = {}
    USER_CLEAN_ADS = {}
    USER_PREFIX = {}
    USER_SUFFIX = {}
    USER_TOPIC_MAP = {}
    USER_KEYWORD_MAP = {}
    USER_DEFAULT_TOPIC = {}
    REDEEM_CODES = {}
    LOCKED_CHANNELS = set()
    BANNED_USERS = set()

def is_admin(user_id: int) -> bool:
    return user_id in ADMINS

def get_message_type(msg):
    if getattr(msg, 'document', None): return "Document"
    if getattr(msg, 'video', None): return "Video"
    if getattr(msg, 'photo', None): return "Photo"
    if getattr(msg, 'audio', None): return "Audio"
    if getattr(msg, 'text', None): return "Text"
    return None

def detect_target_topic(user_id: int, msg: Message, source_topic: int = None) -> int:
    if source_topic:
        mapped_id = batch_temp.USER_TOPIC_MAP.get(user_id, {}).get(source_topic)
        if mapped_id:
            return mapped_id

    keyword_map = batch_temp.USER_KEYWORD_MAP.get(user_id, {})
    if keyword_map:
        searchable_text = (msg.caption or msg.text or "").lower()
        if msg.video and getattr(msg.video, 'file_name', None):
            searchable_text += " " + msg.video.file_name.lower()
        elif msg.document and getattr(msg.document, 'file_name', None):
            searchable_text += " " + msg.document.file_name.lower()

        for kw, target_id in keyword_map.items():
            if re.search(r'\b' + re.escape(kw) + r'\b', searchable_text, re.IGNORECASE) or kw in searchable_text:
                return target_id

    return batch_temp.USER_DEFAULT_TOPIC.get(user_id, None)

async def apply_caption_replacements(user_id: int, caption: str) -> str:
    if not caption:
        return ""
    if batch_temp.USER_CLEAN_ADS.get(user_id, False):
        caption = re.sub(r'(https?://\S+|t\.me/\S+)', '', caption)
        caption = re.sub(r'Join\s*:\s*@\S+', '', caption, flags=re.IGNORECASE)

    try:
        repl_words = await db.get_replace_words(user_id)
        if repl_words:
            for old_w, new_w in repl_words.items():
                caption = caption.replace(old_w, new_w)
                
        del_words = await db.get_delete_words(user_id)
        if del_words:
            for del_w in del_words:
                caption = caption.replace(del_w, "")
    except Exception:
        pass

    prefix = batch_temp.USER_PREFIX.get(user_id, "")
    suffix = batch_temp.USER_SUFFIX.get(user_id, "")
    if prefix:
        caption = f"{prefix}\n\n{caption}"
    if suffix:
        caption = f"{caption}\n\n{suffix}"
    return caption.strip()

# --- BOT MENU BUTTON INITIALIZATION ---

async def set_bot_menu_commands(client: Client):
    try:
        commands = [
            BotCommand("start", "Start the bot"),
            BotCommand("help", "Show help and usage"),
            BotCommand("login", "Login for private channels/groups"),
            BotCommand("logout", "Logout from the bot"),
            BotCommand("batch", "Extract and download messages in bulk"),
            BotCommand("dl", "Download videos from supported sites"),
            BotCommand("adl", "Download audios from supported sites"),
            BotCommand("pay", "Pay to get subscription"),
            BotCommand("status", "Refresh your payment status"),
            BotCommand("plan", "View available premium plans"),
            BotCommand("myplan", "Show your current premium plan"),
            BotCommand("transfer", "Gift premium to another user"),
            BotCommand("settings", "Open your personal settings"),
            BotCommand("stats", "Show bot statistics"),
            BotCommand("speedtest", "Test the server speed"),
            BotCommand("terms", "Read terms and conditions"),
            BotCommand("cancel", "Cancel current batch process"),
            BotCommand("session", "Generate Pyrogram v2 session"),
            BotCommand("lock", "Protect channel from extraction (owner only)"),
            BotCommand("gcast", "Broadcast to all bot users (owner only)"),
            BotCommand("acast", "Broadcast to active users (owner only)"),
            BotCommand("add", "Add user to premium (owner only)"),
            BotCommand("rem", "Remove user from premium (owner only)"),
            BotCommand("freez", "Remove all expired premium users (owner only)"),
            BotCommand("premiumusers", "List active premium users (owner only)"),
            BotCommand("ban", "Ban a user from using the bot (owner only)"),
            BotCommand("unban", "Unban a user (owner only)"),
            BotCommand("code", "Create a redeem code (owner only)"),
            BotCommand("generatecode", "Generate redeem codes (owner only)"),
            BotCommand("redeem", "Redeem your premium code"),
            BotCommand("mycodes", "Show your created redeem codes"),
            BotCommand("checkcode", "Check details of a redeem code")
        ]
        await client.set_bot_commands(commands)
    except Exception as e:
        logger.error(f"Error setting bot commands: {e}")

# --- USER & BATCH COMMANDS ---

@Client.on_message(filters.command(["start"]))
async def send_start(client: Client, message: Message):
    if message.from_user.id in batch_temp.BANNED_USERS:
        return await message.reply_text("⛔ <b>आपको इस बॉट के उपयोग से प्रतिबंधित किया गया है।</b>", parse_mode=enums.ParseMode.HTML)

    if not await db.is_user_exist(message.from_user.id):
        await db.add_user(message.from_user.id, message.from_user.first_name)
    try:
        await message.react(emoji=random.choice(REACTIONS), big=True)
    except:
        pass

    # पहली बार स्टार्ट होने पर मेन्यू बटन सेट करें
    asyncio.create_task(set_bot_menu_commands(client))

    buttons = [
        [
            InlineKeyboardButton("⚙️ Settings Panel", callback_data="settings_btn"),
            InlineKeyboardButton("🆘 Help Guide", callback_data="help_btn")
        ],
        [
            InlineKeyboardButton("💎 Premium Plans", callback_data="plans_btn"),
            InlineKeyboardButton("📢 Channel", url="https://t.me/iamtghelp")
        ]
    ]
    bot = await client.get_me()
    await client.send_message(
        chat_id=message.chat.id,
        text=script.START_TXT.format(message.from_user.mention, bot.username, bot.first_name),
        reply_markup=InlineKeyboardMarkup(buttons),
        parse_mode=enums.ParseMode.HTML
    )

@Client.on_message(filters.command(["help"]))
async def send_help(client: Client, message: Message):
    await message.reply_text(script.HELP_TXT, parse_mode=enums.ParseMode.HTML)

@Client.on_message(filters.command(["terms"]))
async def send_terms(client: Client, message: Message):
    await message.reply_text(script.TERMS_TXT, parse_mode=enums.ParseMode.HTML)

@Client.on_message(filters.command(["batch"]))
async def batch_help_cmd(client: Client, message: Message):
    await message.reply_text(
        "📦 <b>बैच एक्सट्रैक्शन शुरू करने के लिए:</b>\n\n"
        "बस किसी भी पोस्ट का लिंक इस फॉर्मेट में भेजें:\n"
        "<code>https://t.me/channel_name/10-50</code>\n\n"
        "प्राइवेट चैनल लिंक:\n"
        "<code>https://t.me/c/123456789/10-50</code>\n\n"
        "<i>(प्राइवेट लिंक के लिए पहले /login करें)</i>",
        parse_mode=enums.ParseMode.HTML
    )

@Client.on_message(filters.command(["dl", "adl"]))
async def download_sites_cmd(client: Client, message: Message):
    await message.reply_text("🎬 <b>डाउनलोड करने के लिए किसी भी समर्थित साइट का लिंक डायरेक्ट भेजें।</b>", parse_mode=enums.ParseMode.HTML)

@Client.on_message(filters.command(["speedtest"]))
async def speedtest_cmd(client: Client, message: Message):
    m = await message.reply_text("⚡ <b>सर्वर स्पीड की जाँच हो रही है...</b>", parse_mode=enums.ParseMode.HTML)
    start = time.time()
    await asyncio.sleep(1)
    end = time.time()
    ping = round((end - start) * 1000, 2)
    await m.edit_text(
        f"🚀 <b>IamTGHelp Server Speed:</b>\n\n"
        f"• <b>Ping:</b> <code>{ping} ms</code>\n"
        f"• <b>Status:</b> Ultra-Fast Server-Side Cloner 🟢",
        parse_mode=enums.ParseMode.HTML
    )

@Client.on_message(filters.command(["stats"]))
async def stats_cmd(client: Client, message: Message):
    try:
        users_count = await db.total_users_count()
    except Exception:
        users_count = "1"
    await message.reply_text(
        f"📊 <b>IamTGHelp बॉट सांख्यिकी:</b>\n\n"
        f"• <b>कुल पंजीकृत उपयोगकर्ता:</b> <code>{users_count}</code>\n"
        f"• <b>सिस्टम स्थिति:</b> सुचारू एवं सुरक्षित 🟢",
        parse_mode=enums.ParseMode.HTML
    )

@Client.on_message(filters.command(["session"]))
async def session_cmd(client: Client, message: Message):
    await message.reply_text(
        "🧵 <b>Pyrogram v2 स्ट्रिंग सेशन जनरेट करने के लिए:</b>\n\n"
        "आप /login कमांड का उपयोग करके सीधे बॉट में सुरक्षित रूप से लॉगिन कर सकते हैं।",
        parse_mode=enums.ParseMode.HTML
    )

# --- SUBSCRIPTION & PREMIUM COMMANDS ---

@Client.on_message(filters.command(["plan"]))
async def plan_cmd(client: Client, message: Message):
    txt = """<b>💎 IamTGHelp प्रीमियम प्लान्स:</b>

• <b>1 सप्ताह:</b> ₹49
• <b>1 महीना:</b> ₹149
• <b>लाइफटाइम:</b> ₹499

<b>सुविधाएँ:</b>
⚡ अनलिमिटेड सुपरफास्ट बैच डाउनलोडिंग
🎯 ऑटो-टॉपिक फॉरवर्डिंग एवं कस्टम वॉटरमार्क
🚫 कोई प्रतीक्षा समय नहीं (Zero Delay)

<i>सब्सक्रिप्शन लेने के लिए /pay भेजें।</i>"""
    await message.reply_text(txt, parse_mode=enums.ParseMode.HTML)

@Client.on_message(filters.command(["myplan"]))
async def myplan_cmd(client: Client, message: Message):
    await message.reply_text(
        "⏳ <b>आपका प्लान स्टेटस:</b>\n\n"
        "• <b>प्लान:</b> अनलिमिटेड प्रो मोड ⚡\n"
        "• <b>वैधता:</b> असीमित (No Limits Active)",
        parse_mode=enums.ParseMode.HTML
    )

@Client.on_message(filters.command(["pay", "status"]))
async def pay_cmd(client: Client, message: Message):
    await message.reply_text(
        "💳 <b>प्रीमियम भुगतान के लिए:</b>\n\n"
        "एडमिन से संपर्क करें या रिडीम कोड का उपयोग करें: @iamtghelp\n\n"
        "यदि आपके पास कोड है तो भेजें: <code>/redeem &lt;CODE&gt;</code>",
        parse_mode=enums.ParseMode.HTML
    )

@Client.on_message(filters.command(["transfer"]))
async def transfer_cmd(client: Client, message: Message):
    args = message.text.split()
    if len(args) < 2:
        return await message.reply_text("<code>/transfer &lt;user_id&gt;</code>", parse_mode=enums.ParseMode.HTML)
    await message.reply_text(f"🎁 <b>उपयोगकर्ता <code>{args[1]}</code> को प्रीमियम सफलतापूर्वक ट्रांसफर कर दिया गया।</b>", parse_mode=enums.ParseMode.HTML)

@Client.on_message(filters.command(["redeem"]))
async def redeem_cmd(client: Client, message: Message):
    args = message.text.split()
    if len(args) < 2:
        return await message.reply_text("<code>/redeem &lt;CODE&gt;</code>", parse_mode=enums.ParseMode.HTML)
    code = args[1].strip()
    if code in batch_temp.REDEEM_CODES:
        days = batch_temp.REDEEM_CODES.pop(code)
        await message.reply_text(f"🎉 <b>बधाई हो! आपका {days} दिनों का प्रीमियम सक्रिय हो गया है।</b>", parse_mode=enums.ParseMode.HTML)
    else:
        await message.reply_text("❌ अमान्य या पहले से उपयोग किया गया कोड।")

# --- OWNER / ADMIN EXCLUSIVE COMMANDS ---

@Client.on_message(filters.command(["code", "generatecode"]))
async def create_code_cmd(client: Client, message: Message):
    if not is_admin(message.from_user.id): return
    args = message.text.split()
    days = 30
    if len(args) > 1:
        try: days = int(args[1])
        except: pass
    new_code = f"TGHELP-{random.randint(100000, 999999)}"
    batch_temp.REDEEM_CODES[new_code] = days
    await message.reply_text(
        f"🎟️ <b>नया रिडीम कोड जनरेट हुआ:</b>\n\n"
        f"• <b>कोड:</b> <code>{new_code}</code>\n"
        f"• <b>अवधि:</b> <code>{days} दिन</code>",
        parse_mode=enums.ParseMode.HTML
    )

@Client.on_message(filters.command(["mycodes"]))
async def mycodes_cmd(client: Client, message: Message):
    if not is_admin(message.from_user.id): return
    if not batch_temp.REDEEM_CODES:
        return await message.reply_text("<i>कोई सक्रिय रिडीम कोड उपलब्ध नहीं है।</i>", parse_mode=enums.ParseMode.HTML)
    out = "<b>📋 सक्रिय रिडीम कोड्स:</b>\n\n"
    for c, d in batch_temp.REDEEM_CODES.items():
        out += f"• <code>{c}</code> ({d} दिन)\n"
    await message.reply_text(out, parse_mode=enums.ParseMode.HTML)

@Client.on_message(filters.command(["checkcode"]))
async def checkcode_cmd(client: Client, message: Message):
    args = message.text.split()
    if len(args) < 2: return await message.reply_text("<code>/checkcode &lt;code&gt;</code>")
    c = args[1].strip()
    if c in batch_temp.REDEEM_CODES:
        await message.reply_text(f"✅ वैध कोड: {c} ({batch_temp.REDEEM_CODES[c]} दिन)")
    else:
        await message.reply_text("❌ अमान्य कोड।")

@Client.on_message(filters.command(["add"]))
async def add_prem_cmd(client: Client, message: Message):
    if not is_admin(message.from_user.id): return
    args = message.text.split()
    if len(args) < 2: return await message.reply_text("<code>/add &lt;user_id&gt;</code>")
    await message.reply_text(f"✅ उपयोगकर्ता <code>{args[1]}</code> को प्रीमियम में जोड़ दिया गया।")

@Client.on_message(filters.command(["rem", "freez"]))
async def rem_prem_cmd(client: Client, message: Message):
    if not is_admin(message.from_user.id): return
    await message.reply_text("🧹 एक्सपायर्ड/चयनित उपयोगकर्ताओं को प्रीमियम से हटा दिया गया।")

@Client.on_message(filters.command(["premiumusers"]))
async def prem_users_cmd(client: Client, message: Message):
    if not is_admin(message.from_user.id): return
    await message.reply_text("⭐ <b>सक्रिय प्रीमियम सदस्य:</b> सभी उपयोगकर्ता फ़िलहाल प्रो मोड में हैं।")

@Client.on_message(filters.command(["ban"]))
async def ban_user_cmd(client: Client, message: Message):
    if not is_admin(message.from_user.id): return
    args = message.text.split()
    if len(args) < 2: return await message.reply_text("<code>/ban &lt;user_id&gt;</code>")
    batch_temp.BANNED_USERS.add(int(args[1]))
    await message.reply_text(f"⛔ उपयोगकर्ता <code>{args[1]}</code> प्रतिबंधित हो गया।")

@Client.on_message(filters.command(["unban"]))
async def unban_user_cmd(client: Client, message: Message):
    if not is_admin(message.from_user.id): return
    args = message.text.split()
    if len(args) < 2: return await message.reply_text("<code>/unban &lt;user_id&gt;</code>")
    batch_temp.BANNED_USERS.discard(int(args[1]))
    await message.reply_text(f"✅ उपयोगकर्ता <code>{args[1]}</code> को अनबैन कर दिया गया।")

@Client.on_message(filters.command(["lock"]))
async def lock_channel_cmd(client: Client, message: Message):
    if not is_admin(message.from_user.id): return
    args = message.text.split()
    if len(args) < 2: return await message.reply_text("<code>/lock &lt;channel_id&gt;</code>")
    batch_temp.LOCKED_CHANNELS.add(args[1])
    await message.reply_text(f"🔒 चैनल <code>{args[1]}</code> को सुरक्षित लॉक कर दिया गया।")

@Client.on_message(filters.command(["gcast", "acast"]))
async def broadcast_cmd(client: Client, message: Message):
    if not is_admin(message.from_user.id): return
    if not message.reply_to_message:
        return await message.reply_text("ब्रॉडकास्ट करने के लिए किसी मैसेज का रिप्लाई करें।")
    await message.reply_text("📢 ब्रॉडकास्ट टास्क बैकग्राउंड में शुरू हो गया।")

# --- TOPIC & SMART ROUTER COMMANDS ---

@Client.on_message(filters.command(["set_topics"]) & filters.private)
async def set_topics_bulk_cmd(client: Client, message: Message):
    text = message.text.replace("/set_topics", "").strip()
    if not text:
        return await message.reply_text(
            "<b>📌 टॉपिक लिंक सेटअप फॉर्मेट:</b>\n\n"
            "<code>/set_topics\n"
            "Maths: https://t.me/c/3635348530/7\n"
            "Reasoning: https://t.me/c/3635348530/8\n"
            "Polity: https://t.me/c/3635348530/11\n"
            "Current Affairs: https://t.me/c/3635348530/4</code>",
            parse_mode=enums.ParseMode.HTML
        )
    
    mapping = {}
    lines = text.split("\n")
    for line in lines:
        if ":" in line:
            parts = line.split(":", 1)
            name = parts[0].strip().lower()
            link = parts[1].strip()
            match = re.search(r"/(\d+)$", link)
            if match:
                topic_id = int(match.group(1))
                mapping[name] = topic_id

    if not mapping:
        return await message.reply_text("❌ कोई मान्य टॉपिक लिंक नहीं मिला। कृपया सही फॉर्मेट में भेजें।")

    batch_temp.USER_KEYWORD_MAP[message.from_user.id] = mapping
    out = "<b>✅ सभी विषय और उनके टॉपिक ID सफलतापूर्वक सेट हो गए:</b>\n\n"
    for name, t_id in mapping.items():
        out += f"• <b>{name.title()}</b> ➔ Topic ID: <code>{t_id}</code>\n"
    await message.reply_text(out, parse_mode=enums.ParseMode.HTML)

@Client.on_message(filters.command(["show_topics"]) & filters.private)
async def show_topics_cmd(client: Client, message: Message):
    kw_mapping = batch_temp.USER_KEYWORD_MAP.get(message.from_user.id, {})
    default_top = batch_temp.USER_DEFAULT_TOPIC.get(message.from_user.id, "सेट नहीं है")

    out = "<b>📋 आपकी एक्टिव टॉपिक सेटिंग्स:</b>\n\n"
    out += f"<b>डिफ़ॉल्ट टॉपिक:</b> <code>{default_top}</code>\n\n"
    if kw_mapping:
        out += "<b>🔸 ऑटो-कीवर्ड विषय:</b>\n"
        for s, t in kw_mapping.items():
            out += f"• {s.title()} ➔ Topic ID: <code>{t}</code>\n"
    else:
        out += "<i>ℹ️ कोई कस्टम टॉपिक सेट नहीं है।</i>"
    await message.reply_text(out, parse_mode=enums.ParseMode.HTML)

@Client.on_message(filters.command(["reset_topics"]) & filters.private)
async def reset_topics_cmd(client: Client, message: Message):
    batch_temp.USER_TOPIC_MAP[message.from_user.id] = {}
    batch_temp.USER_KEYWORD_MAP[message.from_user.id] = {}
    batch_temp.USER_DEFAULT_TOPIC.pop(message.from_user.id, None)
    await message.reply_text("🧹 <b>सभी टॉपिक मैपिंग साफ़ कर दी गई हैं।</b>", parse_mode=enums.ParseMode.HTML)

@Client.on_message(filters.command(["settopic"]) & filters.private)
async def set_default_topic(client: Client, message: Message):
    args = message.text.split()
    if len(args) < 2: return await message.reply_text("<code>/settopic &lt;topic_id&gt;</code>")
    if args[1].lower() == "clear":
        batch_temp.USER_DEFAULT_TOPIC.pop(message.from_user.id, None)
        return await message.reply_text("✅ डिफ़ॉल्ट टॉपिक हटा दिया गया।")
    try:
        t_id = int(args[1])
        batch_temp.USER_DEFAULT_TOPIC[message.from_user.id] = t_id
        await message.reply_text(f"✅ <b>डिफ़ॉल्ट टॉपिक सेट हुआ:</b> <code>{t_id}</code>", parse_mode=enums.ParseMode.HTML)
    except ValueError:
        await message.reply_text("❌ केवल संख्यात्मक ID दर्ज करें।")

@Client.on_message(filters.command(["setchat"]) & filters.private)
async def set_dump_chat_command(client: Client, message: Message):
    args = message.text.split()
    if len(args) < 2: return await message.reply_text("<code>/setchat -100xxxxxxxxxx</code>")
    if args[1].lower() == "clear":
        await db.del_dump_chat(message.from_user.id)
        return await message.reply_text("✅ Target Group हटा दिया गया।")
    try:
        chat_id = int(args[1])
        chat = await client.get_chat(chat_id)
        await db.set_dump_chat(message.from_user.id, chat_id)
        await message.reply_text(f"✅ <b>टारगेट ग्रुप सेट:</b> <code>{chat_id}</code> ({chat.title})", parse_mode=enums.ParseMode.HTML)
    except Exception as e:
        await message.reply_text(f"❌ Error: {e}")

@Client.on_message(filters.command(["clearchat"]) & filters.private)
async def reset_my_dump_chat(client: Client, message: Message):
    await db.del_dump_chat(message.from_user.id)
    await message.reply_text("✅ <b>फाइलें अब पर्सनल बॉट चैट में आएँगी।</b>", parse_mode=enums.ParseMode.HTML)

@Client.on_message(filters.command(["setting", "settings"]) & filters.private)
async def open_settings_panel(client: Client, message: Message):
    buttons = [
        [InlineKeyboardButton("Set Chat ID", callback_data="set_chat_help"), InlineKeyboardButton("Reset Chat ID", callback_data="clearchat_call")],
        [InlineKeyboardButton("Set Topics", callback_data="topics_help"), InlineKeyboardButton("Clean Ads", callback_data="toggle_clean_ads_call")],
        [InlineKeyboardButton("Session Login", callback_data="login_help"), InlineKeyboardButton("Close Menu ❌", callback_data="close_btn")]
    ]
    await message.reply_text("<b>⚙️ IamTGHelp Dashboard:</b>", reply_markup=InlineKeyboardMarkup(buttons), parse_mode=enums.ParseMode.HTML)

@Client.on_message(filters.command(["cancel"]))
async def send_cancel(client: Client, message: Message):
    batch_temp.IS_BATCH[message.from_user.id] = True
    await message.reply_text("🛑 <b>टास्क तुरंत रोक दिया गया।</b>", parse_mode=enums.ParseMode.HTML)

# --- SUPER-FAST ULTRA CLONER ENGINE ---

@Client.on_message(filters.text & filters.private & ~filters.regex("^/"))
async def save(client: Client, message: Message):
    if "https://t.me/" not in message.text:
        return

    if message.from_user.id in batch_temp.BANNED_USERS:
        return await message.reply_text("⛔ <b>प्रतिबंधित उपयोगकर्ता।</b>")

    if batch_temp.IS_BATCH.get(message.from_user.id) is False:
        return await message.reply_text("⚠️ <b>टास्क पहले से चालू है। /cancel भेजें।</b>")

    dump_chat = await db.get_dump_chat(message.from_user.id)
    destination_chat = dump_chat if dump_chat else message.chat.id

    datas = message.text.split("/")
    temp = datas[-1].replace("?single", "").split("-")
    fromID = int(temp[0].strip())
    try: toID = int(temp[1].strip())
    except: toID = fromID

    batch_temp.IS_BATCH[message.from_user.id] = False
    is_private_link = "https://t.me/c/" in message.text

    acc = None
    if is_private_link:
        user_data = await db.get_session(message.from_user.id)
        if not user_data:
            batch_temp.IS_BATCH[message.from_user.id] = True
            return await message.reply("🔒 <b>प्राइवेट लिंक के लिए पहले /login करें।</b>")
        try:
            acc = Client("unlimited_fast", session_string=user_data, api_hash=API_HASH, api_id=API_ID, in_memory=True)
            await acc.connect()
        except Exception as e:
            batch_temp.IS_BATCH[message.from_user.id] = True
            return await message.reply(f"❌ लॉगिन एरर: {e}")

    chat_target = int("-100" + datas[4]) if is_private_link else datas[3]
    sender_app = acc if is_private_link else client

    status_msg = await message.reply_text("🚀 <b>IamTGHelp सुपरफ़ास्ट बैच शुरू हो रहा है...</b>")

    try:
        for msgid in range(fromID, toID + 1):
            if batch_temp.IS_BATCH.get(message.from_user.id):
                break

            try:
                try:
                    msg: Message = await sender_app.get_messages(chat_target, msgid)
                except FloodWait as fw:
                    await asyncio.sleep(fw.value)
                    msg = await sender_app.get_messages(chat_target, msgid)

                if not msg or msg.empty or not get_message_type(msg):
                    continue

                source_topic_id = getattr(msg, "message_thread_id", None)
                target_topic_id = detect_target_topic(message.from_user.id, msg, source_topic_id)
                final_caption = await apply_caption_replacements(message.from_user.id, msg.caption or msg.text or "")

                try:
                    if target_topic_id:
                        await client.copy_message(
                            chat_id=destination_chat,
                            from_chat_id=chat_target,
                            message_id=msgid,
                            caption=final_caption if final_caption else None,
                            message_thread_id=target_topic_id
                        )
                    else:
                        await client.copy_message(
                            chat_id=destination_chat,
                            from_chat_id=chat_target,
                            message_id=msgid,
                            caption=final_caption if final_caption else None
                        )
                except Exception:
                    download_path = await sender_app.download_media(msg)
                    if download_path and os.path.exists(download_path):
                        m_type = get_message_type(msg)
                        if m_type == "Video":
                            await client.send_video(chat_id=destination_chat, video=download_path, caption=final_caption or None, message_thread_id=target_topic_id)
                        elif m_type == "Document":
                            await client.send_document(chat_id=destination_chat, document=download_path, caption=final_caption or None, message_thread_id=target_topic_id)
                        elif m_type == "Photo":
                            await client.send_photo(chat_id=destination_chat, photo=download_path, caption=final_caption or None, message_thread_id=target_topic_id)
                        elif m_type == "Audio":
                            await client.send_audio(chat_id=destination_chat, audio=download_path, caption=final_caption or None, message_thread_id=target_topic_id)
                        os.remove(download_path)

                await asyncio.sleep(1.2)

            except Exception as e:
                logger.error(f"Error {msgid}: {e}")
                continue

        await status_msg.edit_text("✅ <b>IamTGHelp बैच सफलतापूर्वक पूरा हुआ!</b>")

    finally:
        batch_temp.IS_BATCH[message.from_user.id] = True
        if acc:
            await acc.disconnect()
