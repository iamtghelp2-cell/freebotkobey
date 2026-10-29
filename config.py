# ========================================================
# IamTGHelp - Save Restricted & Smart Topic Router Bot
# Powered & Maintained by: @iamtghelp
# ========================================================

import os

# ==============================
# Telegram Bot Credentials
# ==============================

BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
API_ID = int(os.environ.get("API_ID", "0"))
API_HASH = os.environ.get("API_HASH", "")

# ==============================
# Admin Configuration
# ==============================

ADMINS = [int(admin) for admin in os.environ.get("ADMINS", "").split(",") if admin]

# ==============================
# Database Configuration
# ==============================

DB_URI = os.environ.get("DB_URI", "")
DB_NAME = os.environ.get("DB_NAME", "iamtghelp_bot")

# ==============================
# Logging Configuration
# ==============================

LOG_CHANNEL = int(os.environ.get("LOG_CHANNEL", "-1003506524877"))

# ==============================
# Error Handling & Settings
# ==============================

ERROR_MESSAGE = os.environ.get("ERROR_MESSAGE", "True").lower() == "true"
