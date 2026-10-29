# ========================================================
# IamTGHelp - Advanced Settings & User Dashboard
# Powered & Maintained by: @iamtghelp
# ========================================================

import os
from pyrogram import Client, filters, enums
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from database.db import db
from Rexbots.strings import COMMANDS_TXT

# ======================================================
# /settings - Enhanced Professional Settings Menu
# ======================================================
@Client.on_message(filters.command(["setting", "settings"]) & filters.private)
async def settings_menu(client: Client, message: Message):
    user_id = message.from_user.id
    if not await db.is_user_exist(user_id):
        await db.add_user(user_id, message.from_user.first_name)

    is_premium = await db.check_premium(user_id)
    premium_badge = "💎 Premium Member (Unlimited)" if is_premium else "👤 Free User"

    buttons = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("📜 Commands List", callback_data="cmd_list_btn"),
            InlineKeyboardButton("📊 My Usage Stats", callback_data="user_stats_btn")
        ],
        [
            InlineKeyboardButton("🎯 Topic Setup", callback_data="topic_setup_btn"),
            InlineKeyboardButton("🗑 Dump Chat", callback_data="dump_chat_btn")
        ],
        [
            InlineKeyboardButton("🖼 Thumbnail", callback_data="thumb_btn"),
            InlineKeyboardButton("📝 Caption", callback_data="caption_btn")
        ],
        [
            InlineKeyboardButton("📢 Official Channel", url="https://t.me/iamtghelp"),
            InlineKeyboardButton("❌ Close Menu", callback_data="close_btn")
        ]
    ])

    text = (
        f"<b>⚙️ IamTGHelp Settings Dashboard</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"<b>खाता प्रकार:</b> {premium_badge}\n"
        f"<b>यूज़र ID:</b> <code>{user_id}</code>\n"
        f"<b>इंजन:</b> <code>Ultra-Fast Direct Server Cloner ⚡</code>\n\n"
        f"<i>अपने बॉट को कस्टमाइज़ करने के लिए नीचे दिए गए बटन्स का उपयोग करें।</i>"
    )
    await message.reply_text(text, reply_markup=buttons, parse_mode=enums.ParseMode.HTML)

# ======================================================
# /commands - Direct Access to Commands List
# ======================================================
@Client.on_message(filters.command("commands") & filters.private)
async def direct_commands(client: Client, message: Message):
    buttons = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("⚙️ Open Settings", callback_data="settings_back_btn"),
            InlineKeyboardButton("❌ Close", callback_data="close_btn")
        ]
    ])
    await message.reply_text(
        COMMANDS_TXT,
        reply_markup=buttons,
        parse_mode=enums.ParseMode.HTML,
        disable_web_page_preview=True
    )

# ======================================================
# Callbacks - Settings Navigation
# ======================================================
@Client.on_callback_query(filters.regex("^(cmd_list_btn|dump_chat_btn|thumb_btn|caption_btn|user_stats_btn|topic_setup_btn|settings_back_btn|close_btn)$"))
async def settings_callbacks(client: Client, callback_query: CallbackQuery):
    data = callback_query.data
    user_id = callback_query.from_user.id
   
    back_close = [[
        InlineKeyboardButton("⬅️ Back", callback_data="settings_back_btn"),
        InlineKeyboardButton("❌ Close", callback_data="close_btn")
    ]]

    if data == "cmd_list_btn":
        await callback_query.edit_message_text(
            COMMANDS_TXT,
            reply_markup=InlineKeyboardMarkup(back_close),
            parse_mode=enums.ParseMode.HTML,
            disable_web_page_preview=True
        )

    elif data == "dump_chat_btn":
        current = await db.get_dump_chat(user_id)
        if current:
            try:
                chat = await client.get_chat(current)
                title = chat.title or "Private Group"
            except:
                title = "Unknown (Inaccessible)"
            text = (
                f"<b>🗑 वर्तमान टारगेट ग्रुप (Dump Chat):</b>\n\n"
                f"• <b>Chat ID:</b> <code>{current}</code>\n"
                f"• <b>Title:</b> {title}\n\n"
                "<i>सेव की गई सभी फ़ाइलें सीधे इस ग्रुप में जा रही हैं।</i>\n"
                "<i>हटाने के लिए /clearchat या बदलने के लिए /setchat भेजें।</i>"
            )
        else:
            text = (
                "<b>🗑 कोई Dump Chat सेट नहीं है</b>\n\n"
                "<i>फ़ाइलें केवल इस पर्सनल बॉट चैट में आएँगी।</i>\n"
                "<i>ग्रुप में ऑटो-फॉरवर्ड करने के लिए <code>/setchat &lt;chat_id&gt;</code> का उपयोग करें।</i>"
            )
        await callback_query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(back_close), parse_mode=enums.ParseMode.HTML)

    elif data == "topic_setup_btn":
        text = (
            "<b>🎯 फोरम टॉपिक ऑटो-रूटिंग गाइड:</b>\n\n"
            "विषय-वार ग्रुप टॉपिक्स में फ़ाइलें भेजने के लिए:\n"
            "<code>/set_topics\n"
            "Maths: https://t.me/c/123456789/5\n"
            "Reasoning: https://t.me/c/123456789/8\n"
            "English: https://t.me/c/123456789/12</code>\n\n"
            "• सक्रिय टॉपिक देखने के लिए: <code>/show_topics</code>\n"
            "• सभी टॉपिक हटाने के लिए: <code>/reset_topics</code>"
        )
        await callback_query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(back_close), parse_mode=enums.ParseMode.HTML)

    elif data == "thumb_btn":
        try:
            thumb = await db.get_thumbnail(user_id)
        except:
            thumb = None

        if thumb and os.path.exists(thumb):
            await callback_query.message.reply_photo(
                thumb,
                caption="<b>🖼 आपका कस्टम थंबनेल</b>\n\n<i>बदलने के लिए नई फ़ोटो भेजें • हटाने के लिए /del_thumb</i>",
                parse_mode=enums.ParseMode.HTML
            )
            await callback_query.answer("थंबनेल प्रीव्यू नीचे भेज दिया गया है!")
        else:
            await callback_query.edit_message_text(
                "<b>🖼 कोई कस्टम थंबनेल सेट नहीं है</b>\n\n"
                "<i>वीडियो और फ़ाइलों पर अपना थंबनेल लगाने के लिए चैट में कोई भी फ़ोटो भेजें।</i>",
                reply_markup=InlineKeyboardMarkup(back_close),
                parse_mode=enums.ParseMode.HTML
            )

    elif data == "caption_btn":
        caption = await db.get_caption(user_id)
        if caption:
            preview = caption.format(filename="Sample_Lecture_2026.mp4", size="420 MB")
            text = (
                f"<b>📝 आपका कस्टम कैप्शन:</b>\n\n"
                f"<code>{caption}</code>\n\n"
                f"<b>Preview:</b>\n{preview}\n\n"
                "<i>बदलने के लिए: /set_caption &lt;टेक्स्ट&gt;</i>\n"
                "<i>हटाने के लिए: /del_caption</i>"
            )
        else:
            text = (
                "<b>📝 कोई कस्टम कैप्शन सेट नहीं है</b>\n\n"
                "<i>कस्टम कैप्शन सेट करने के लिए <code>/set_caption &lt;टेक्स्ट&gt;</code> भेजें।</i>\n"
                "<i>प्लेसहोल्डर्स: {filename}, {size}</i>"
            )
        await callback_query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(back_close), parse_mode=enums.ParseMode.HTML)

    elif data == "user_stats_btn":
        is_premium = await db.check_premium(user_id)
        limit_text = "♾️ Unlimited (No Limits)" if is_premium else "10 Files / 24h"
        usage_text = "Ignored (Pro User)" if is_premium else "0 / 10"

        text = (
            f"<b>📊 उपयोगकर्ता सांख्यिकी (Stats):</b>\n\n"
            f"• <b>प्लान:</b> {'💎 Premium Mode' if is_premium else '👤 Free User'}\n"
            f"• <b>दैनिक लिमिट:</b> <code>{limit_text}</code>\n"
            f"• <b>आज का उपयोग:</b> <code>{usage_text}</code>\n"
            f"• <b>बॉट इंजन:</b> <code>IamTGHelp Super-Cloner v2.0</code>"
        )
        await callback_query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(back_close), parse_mode=enums.ParseMode.HTML)

    elif data == "settings_back_btn":
        is_premium = await db.check_premium(user_id)
        premium_badge = "💎 Premium Member (Unlimited)" if is_premium else "👤 Free User"

        buttons = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("📜 Commands List", callback_data="cmd_list_btn"),
                InlineKeyboardButton("📊 My Usage Stats", callback_data="user_stats_btn")
            ],
            [
                InlineKeyboardButton("🎯 Topic Setup", callback_data="topic_setup_btn"),
                InlineKeyboardButton("🗑 Dump Chat", callback_data="dump_chat_btn")
            ],
            [
                InlineKeyboardButton("🖼 Thumbnail", callback_data="thumb_btn"),
                InlineKeyboardButton("📝 Caption", callback_data="caption_btn")
            ],
            [
                InlineKeyboardButton("📢 Official Channel", url="https://t.me/iamtghelp"),
                InlineKeyboardButton("❌ Close Menu", callback_data="close_btn")
            ]
        ])

        text = (
            f"<b>⚙️ IamTGHelp Settings Dashboard</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"<b>खाता प्रकार:</b> {premium_badge}\n"
            f"<b>यूज़र ID:</b> <code>{user_id}</code>\n"
            f"<b>इंजन:</b> <code>Ultra-Fast Direct Server Cloner ⚡</code>\n\n"
            f"<i>अपने बॉट को कस्टमाइज़ करने के लिए नीचे दिए गए बटन्स का उपयोग करें।</i>"
        )
        await callback_query.edit_message_text(text, reply_markup=buttons, parse_mode=enums.ParseMode.HTML)

    elif data == "close_btn":
        await callback_query.message.delete()

    await callback_query.answer()
