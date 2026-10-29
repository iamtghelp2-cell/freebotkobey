# ========================================================
# IamTGHelp - Custom Caption & Header Management
# Powered & Maintained by: @iamtghelp
# ========================================================

from pyrogram import Client, filters, enums
from pyrogram.types import Message
from database.db import db

# ======================================================
# /set_caption - Set Custom Caption
# ======================================================
@Client.on_message(filters.command("set_caption") & filters.private)
async def set_caption(client: Client, message: Message):
    user_id = message.from_user.id
    
    if not await db.is_user_exist(user_id):
        await db.add_user(user_id, message.from_user.first_name)

    if len(message.command) < 2:
        return await message.reply_text(
            "<b>⚠️ उपयोग का सही तरीका:</b>\n\n"
            "कमांड के बाद अपना कस्टम कैप्शन लिखें।\n\n"
            "<b>फॉर्मेट:</b>\n"
            "<code>/set_caption फ़ाइल: {filename} | साइज: {size} | @iamtghelp</code>\n\n"
            "<b>सपोर्टेड टैग्स:</b>\n"
            "• <code>{filename}</code> : ओरिजिनल फ़ाइल का नाम\n"
            "• <code>{size}</code> : फ़ाइल का साइज\n",
            parse_mode=enums.ParseMode.HTML
        )

    caption = message.text.split(" ", 1)[1].strip()
    await db.set_caption(user_id, caption)

    await message.reply_text(
        "<b>✅ कस्टम कैप्शन सफलतापूर्वक सेव हो गया!</b>\n\n"
        f"<b>Preview:</b>\n<code>{caption}</code>\n\n"
        "<i>यह कैप्शन आपकी आने वाली सभी फाइलों पर लागू होगा।</i>",
        parse_mode=enums.ParseMode.HTML
    )

# ======================================================
# /see_caption - View Current Caption
# ======================================================
@Client.on_message(filters.command("see_caption") & filters.private)
async def see_caption(client: Client, message: Message):
    user_id = message.from_user.id
    
    if not await db.is_user_exist(user_id):
        await db.add_user(user_id, message.from_user.first_name)

    caption = await db.get_caption(user_id)

    if caption:
        await message.reply_text(
            "<b>📝 आपका वर्तमान कस्टम कैप्शन:</b>\n\n"
            f"<code>{caption}</code>\n\n"
            "<i>इसे हटाने के लिए /del_caption भेजें।</i>",
            parse_mode=enums.ParseMode.HTML
        )
    else:
        await message.reply_text(
            "<b>❌ कोई कस्टम कैप्शन सेट नहीं है</b>\n\n"
            "आप अभी डिफ़ॉल्ट बॉट कैप्शन का उपयोग कर रहे हैं।\n"
            "<i>नया जोड़ने के लिए <code>/set_caption &lt;टेक्स्ट&gt;</code> भेजें।</i>",
            parse_mode=enums.ParseMode.HTML
        )

# ======================================================
# /del_caption - Delete Custom Caption
# ======================================================
@Client.on_message(filters.command("del_caption") & filters.private)
async def del_caption(client: Client, message: Message):
    user_id = message.from_user.id
    
    if not await db.is_user_exist(user_id):
        await db.add_user(user_id, message.from_user.first_name)

    caption = await db.get_caption(user_id)

    if not caption:
        return await message.reply_text(
            "<b>⚠️ कोई कस्टम कैप्शन नहीं मिला जिसे हटाया जा सके।</b>",
            parse_mode=enums.ParseMode.HTML
        )

    await db.del_caption(user_id)

    await message.reply_text(
        "<b>🗑 कस्टम कैप्शन हटा दिया गया है।</b>\n\n"
        "<i>अब फ़ाइलें ओरिजिनल कैप्शन के साथ भेजी जाएँगी।</i>",
        parse_mode=enums.ParseMode.HTML
    )
