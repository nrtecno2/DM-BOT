import telebot
from telebot import types
from flask import Flask, request

import config
import database as db
import instagram_api as ig

bot = telebot.TeleBot(config.BOT_TOKEN, threaded=True)
app = Flask(__name__)

db.init_db()


# ---------------- Helper functions ----------------

def is_admin(user_id):
    return user_id == config.ADMIN_ID


def require_admin(func):
    def wrapper(call_or_msg):
        user_id = call_or_msg.from_user.id
        if not is_admin(user_id):
            bot.send_message(user_id, "❌ Ye bot sirf personal use ke liye hai. Tumhe access nahi hai.")
            return
        return func(call_or_msg)
    return wrapper


def main_menu_markup():
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("🔗 Connect Instagram", callback_data="connect_ig"),
        types.InlineKeyboardButton("🔑 Add Keyword", callback_data="add_keyword"),
    )
    markup.add(
        types.InlineKeyboardButton("✉️ Add Template", callback_data="add_template"),
        types.InlineKeyboardButton("📊 My Stats", callback_data="view_stats"),
    )
    return markup


# ---------------- Telegram Handlers ----------------

@bot.message_handler(commands=["start"])
def start_handler(message):
    user_id = message.from_user.id
    username = message.from_user.username

    if not is_admin(user_id):
        bot.send_message(message.chat.id, "❌ Ye bot sirf personal use ke liye hai. Tumhe access nahi hai.")
        return

    db.upsert_user(user_id, username)
    bot.send_message(
        message.chat.id,
        "✅ Welcome! Apna Instagram account connect karke DM automation set karo.\n\n"
        "Neeche menu se shuru karo:",
        reply_markup=main_menu_markup()
    )


@bot.callback_query_handler(func=lambda call: call.data == "connect_ig")
@require_admin
def connect_instagram(call):
    user_id = call.from_user.id
    oauth_url = ig.get_oauth_url(state=str(user_id))
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🔗 Connect Instagram Account", url=oauth_url))
    bot.send_message(
        user_id,
        "Neeche button dabao aur apna Instagram Business/Creator account authorize karo.\n\n"
        "⚠️ Note: Account Facebook Page se linked Business/Creator account hona chahiye.",
        reply_markup=markup
    )


@bot.callback_query_handler(func=lambda call: call.data == "add_template")
@require_admin
def add_template_start(call):
    msg = bot.send_message(call.from_user.id, "Template ka naam bhejo (e.g. 'Free Guide'):")
    bot.register_next_step_handler(msg, add_template_name)


def add_template_name(message):
    if not is_admin(message.from_user.id):
        return
    name = message.text.strip()
    msg = bot.send_message(message.chat.id, "Ab DM message text bhejo (jo user ko milega):")
    bot.register_next_step_handler(msg, add_template_message, name)


def add_template_message(message, name):
    text = message.text.strip()
    msg = bot.send_message(message.chat.id, "Button URL bhejo (ya 'skip' agar button nahi chahiye):")
    bot.register_next_step_handler(msg, add_template_url, name, text)


def add_template_url(message, name, text):
    url = message.text.strip()
    button_url = None if url.lower() == "skip" else url
    button_text = "Open Link" if button_url else None

    tid = db.add_template(message.from_user.id, name, text, button_text, button_url)
    bot.send_message(message.chat.id, f"✅ Template '{name}' ban gaya (ID: {tid}).\nAb /start se menu me 'Add Keyword' se ise link karo.")


@bot.callback_query_handler(func=lambda call: call.data == "add_keyword")
@require_admin
def add_keyword_start(call):
    user_id = call.from_user.id
    templates = db.get_templates(user_id)
    if not templates:
        bot.send_message(user_id, "❌ Pehle ek template banao ('Add Template' se).")
        return

    text = "Available templates:\n" + "\n".join([f"ID {t['id']}: {t['name']}" for t in templates])
    msg = bot.send_message(user_id, f"{text}\n\nKeyword bhejo jispe ye trigger hoga:")
    bot.register_next_step_handler(msg, add_keyword_word)


def add_keyword_word(message):
    if not is_admin(message.from_user.id):
        return
    keyword = message.text.strip()
    msg = bot.send_message(message.chat.id, "Ab template ID bhejo jo is keyword se link karna hai:")
    bot.register_next_step_handler(msg, add_keyword_template, keyword)


def add_keyword_template(message, keyword):
    try:
        template_id = int(message.text.strip())
    except ValueError:
        bot.send_message(message.chat.id, "❌ Invalid ID. Dobara /start karo.")
        return

    db.add_keyword(message.from_user.id, keyword, template_id)
    bot.send_message(message.chat.id, f"✅ Keyword '{keyword}' set ho gaya! Ab jab bhi koi comment me ye word likhega, DM chala jayega.")


@bot.callback_query_handler(func=lambda call: call.data == "view_stats")
@require_admin
def view_stats(call):
    user_id = call.from_user.id
    stats = db.get_stats(user_id)
    keywords = db.get_keywords(user_id)
    user = db.get_user(user_id)

    ig_status = f"✅ Connected (@{user['ig_username']})" if user and user.get("ig_username") else "❌ Not connected"

    bot.send_message(
        user_id,
        f"📊 <b>Stats</b>\n\n"
        f"Instagram: {ig_status}\n"
        f"Active Keywords: {len(keywords)}\n"
        f"Total DMs Sent: {stats['total_dms_sent']}",
        parse_mode="HTML"
    )


# ---------------- Flask Routes: Telegram Webhook ----------------

@app.route(config.WEBHOOK_PATH, methods=["POST"])
def telegram_webhook():
    json_str = request.get_data().decode("utf-8")
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return "OK", 200


# ---------------- Flask Routes: Instagram OAuth ----------------

@app.route("/oauth/instagram/callback")
def instagram_oauth_callback():
    code = request.args.get("code")
    state = request.args.get("state")  # Telegram user_id

    if not code or not state:
        return "Missing code or state", 400

    telegram_id = int(state)
    if not is_admin(telegram_id):
        return "Unauthorized", 403

    token_data = ig.exchange_code_for_token(code)
    short_token = token_data.get("access_token")
    if not short_token:
        bot.send_message(telegram_id, "❌ Instagram connect fail ho gaya. Dobara try karo.")
        return "Token exchange failed", 400

    long_token_data = ig.get_long_lived_token(short_token)
    long_token = long_token_data.get("access_token", short_token)

    pages = ig.get_user_pages(long_token)
    if not pages:
        bot.send_message(telegram_id, "❌ Koi Facebook Page nahi mili. Pehle apna Instagram ko ek Facebook Page se link karo.")
        return "No pages found", 400

    page = pages[0]
    page_access_token = page["access_token"]
    ig_business_id = ig.get_ig_business_account(page["id"], page_access_token)

    if not ig_business_id:
        bot.send_message(telegram_id, "❌ Is Page se koi Instagram Business account linked nahi hai.")
        return "No IG business account", 400

    ig_username = ig.get_ig_username(ig_business_id, page_access_token)
    db.save_instagram_connection(telegram_id, ig_business_id, page_access_token, ig_username)

    bot.send_message(telegram_id, f"✅ Instagram account @{ig_username} connect ho gaya! Ab keywords set karo.")
    return "Instagram connected! Wapas Telegram pe jaao.", 200


# ---------------- Flask Routes: Instagram Webhook (comment events) ----------------

@app.route(config.IG_WEBHOOK_PATH, methods=["GET"])
def instagram_webhook_verify():
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    if mode == "subscribe" and token == config.IG_VERIFY_TOKEN:
        return challenge, 200
    return "Verification failed", 403


@app.route(config.IG_WEBHOOK_PATH, methods=["POST"])
def instagram_webhook_events():
    data = request.get_json()

    for entry in data.get("entry", []):
        ig_business_id = entry.get("id")
        owner = db.get_user_by_ig_business_id(ig_business_id)
        if not owner:
            continue

        for change in entry.get("changes", []):
            if change.get("field") != "comments":
                continue

            value = change.get("value", {})
            comment_text = value.get("text", "")
            commenter_igsid = value.get("from", {}).get("id")
            commenter_username = value.get("from", {}).get("username", "unknown")

            keyword_match = db.find_keyword_match(owner["telegram_id"], comment_text)
            if not keyword_match:
                continue

            templates = db.get_templates(owner["telegram_id"])
            template = next((t for t in templates if t["id"] == keyword_match["template_id"]), None)
            if not template:
                continue

            ig.send_dm(
                ig_business_id,
                owner["ig_access_token"],
                commenter_igsid,
                template["message"],
                template.get("button_text"),
                template.get("button_url")
            )

            db.record_sent_dm(owner["telegram_id"], commenter_username, keyword_match["keyword"])

    return "OK", 200


@app.route("/")
def health_check():
    return "Bot is running", 200


# ---------------- Startup ----------------

if __name__ == "__main__":
    import os
    bot.remove_webhook()
    if config.WEBHOOK_URL:
        bot.set_webhook(url=config.WEBHOOK_URL)
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
