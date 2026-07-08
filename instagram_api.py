import requests
from config import FB_APP_ID, FB_APP_SECRET, FB_OAUTH_REDIRECT_URI, IG_OAUTH_SCOPES

GRAPH_API_BASE = "https://graph.facebook.com/v19.0"


def get_oauth_url(state):
    """
    User ko is URL pe bhejo -- yaha wo apna Instagram Business account
    authorize karega. 'state' me hum uska Telegram ID daalte hain taaki
    callback pe pata chale ye connection kis user ke liye hai.
    """
    return (
        f"https://www.facebook.com/v19.0/dialog/oauth?"
        f"client_id={FB_APP_ID}"
        f"&redirect_uri={FB_OAUTH_REDIRECT_URI}"
        f"&state={state}"
        f"&scope={IG_OAUTH_SCOPES}"
    )


def exchange_code_for_token(code):
    """OAuth 'code' ko short-lived access token se badalta hai"""
    resp = requests.get(f"{GRAPH_API_BASE}/oauth/access_token", params={
        "client_id": FB_APP_ID,
        "client_secret": FB_APP_SECRET,
        "redirect_uri": FB_OAUTH_REDIRECT_URI,
        "code": code
    })
    return resp.json()


def get_long_lived_token(short_token):
    """Short-lived token ko ~60 din wale long-lived token me convert karta hai"""
    resp = requests.get(f"{GRAPH_API_BASE}/oauth/access_token", params={
        "grant_type": "fb_exchange_token",
        "client_id": FB_APP_ID,
        "client_secret": FB_APP_SECRET,
        "fb_exchange_token": short_token
    })
    return resp.json()


def get_user_pages(access_token):
    """User ke saare Facebook Pages list karta hai (jinse IG account linked ho sakta hai)"""
    resp = requests.get(f"{GRAPH_API_BASE}/me/accounts", params={
        "access_token": access_token
    })
    return resp.json().get("data", [])


def get_ig_business_account(page_id, page_access_token):
    """Page se linked Instagram Business Account ID nikalta hai"""
    resp = requests.get(f"{GRAPH_API_BASE}/{page_id}", params={
        "fields": "instagram_business_account",
        "access_token": page_access_token
    })
    data = resp.json()
    ig_account = data.get("instagram_business_account")
    return ig_account.get("id") if ig_account else None


def get_ig_username(ig_business_id, access_token):
    resp = requests.get(f"{GRAPH_API_BASE}/{ig_business_id}", params={
        "fields": "username",
        "access_token": access_token
    })
    return resp.json().get("username")


def send_dm(ig_business_id, access_token, recipient_ig_scoped_id, message_text, button_text=None, button_url=None):
    """
    Instagram DM bhejta hai. recipient_ig_scoped_id woh IGSID hai jo
    comment webhook event ke andar milta hai.
    """
    payload = {
        "recipient": {"id": recipient_ig_scoped_id},
        "message": {"text": message_text}
    }

    if button_url:
        payload["message"] = {
            "attachment": {
                "type": "template",
                "payload": {
                    "template_type": "button",
                    "text": message_text,
                    "buttons": [
                        {"type": "web_url", "url": button_url, "title": button_text or "Open"}
                    ]
                }
            }
        }

    resp = requests.post(
        f"{GRAPH_API_BASE}/{ig_business_id}/messages",
        params={"access_token": access_token},
        json=payload
    )
    return resp.json()
