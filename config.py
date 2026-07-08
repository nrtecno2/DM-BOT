import os

# ---- Telegram Config ----
BOT_TOKEN = os.environ.get("BOT_TOKEN")                      # Telegram bot token (@BotFather)
ADMIN_ID = int(os.environ.get("ADMIN_ID", "0"))                # tera Telegram user ID -- sirf yehi bot use kar sakta hai

# ---- Webhook Config (Render) ----
WEBHOOK_HOST = os.environ.get("WEBHOOK_HOST")                 # e.g. https://your-app.onrender.com
WEBHOOK_PATH = f"/telegram/{BOT_TOKEN}"
WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}" if WEBHOOK_HOST else None

# ---- Meta App Config ----
FB_APP_ID = os.environ.get("FB_APP_ID")                       # Meta Developer App ID
FB_APP_SECRET = os.environ.get("FB_APP_SECRET")                # Meta Developer App Secret
FB_OAUTH_REDIRECT_URI = f"{WEBHOOK_HOST}/oauth/instagram/callback" if WEBHOOK_HOST else None
IG_VERIFY_TOKEN = os.environ.get("IG_VERIFY_TOKEN", "changeme")  # Meta webhook verify token
IG_WEBHOOK_PATH = "/instagram/webhook"

IG_OAUTH_SCOPES = "instagram_basic,instagram_manage_comments,instagram_manage_messages,pages_show_list,pages_manage_metadata"

# ---- Database ----
DB_PATH = os.environ.get("DB_PATH", "bot_data.db")
