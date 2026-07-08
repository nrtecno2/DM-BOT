<div align="center">

# 📸 Instagram DM Automation Bot

### Telegram se control karo apna Instagram comment-to-DM automation

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-3.0-000000?style=for-the-badge&logo=flask&logoColor=white)
![Telegram](https://img.shields.io/badge/pyTelegramBotAPI-4.14-26A5E4?style=for-the-badge&logo=telegram&logoColor=white)
![Render](https://img.shields.io/badge/Deploy-Render-46E3B7?style=for-the-badge&logo=render&logoColor=white)
![License](https://img.shields.io/badge/Use-Personal-orange?style=for-the-badge)

*Koi bhi Instagram post/reel pe koi keyword comment kare → automatically DM mil jaye. Sab kuch Telegram se manage hota hai.*

</div>

---

## 📖 Kya karta hai ye bot

```
Instagram Comment  ──▶  Keyword Match?  ──▶  Auto-DM Sent
    "SEND"                   ✅                 📩
```

Tum apna Instagram Business/Creator account is bot se connect karte ho.
Fir keywords aur DM templates set karte ho. Jab bhi koi tumhari post pe
wo keyword comment karta hai, Meta ki **official Graph API** ke through
usko automatically DM chala jata hai — koi ban ka risk nahi, kyunki
sab kuch Meta ke rules ke andar hota hai.

> 🔒 **Personal use only** — bot sirf tumhare (`ADMIN_ID`) Telegram
> account se hi respond karega. Koi aur isse use nahi kar sakta.

---

## ✨ Features

| | |
|---|---|
| 🔗 **Instagram OAuth** | Secure Meta login, koi password share nahi hota |
| 🔑 **Multiple Keywords** | Jitne chaho utne trigger words set karo |
| ✉️ **Custom Templates** | Har keyword ka apna DM message + button link |
| 📊 **Live Stats** | Kitne DMs bheje gaye, seedha Telegram me dekho |
| ☁️ **Free Hosting** | GitHub + Render pe deploy, 24/7 chalta rahe |

---

## 🗂️ Project Structure

```
instabot/
├── bot.py               # Main bot + Flask webhooks (Telegram + Instagram)
├── database.py          # SQLite storage layer
├── instagram_api.py     # Meta Graph API wrapper (OAuth, send DM)
├── config.py             # Environment variables loader
├── requirements.txt      # Python dependencies
├── render.yaml           # Render deploy blueprint
└── .env.example           # Environment variables template
```

---

## ⚙️ Environment Variables

| Variable | Kaha se milega | Required |
|---|---|:---:|
| `BOT_TOKEN` | @BotFather se naya bot banate waqt | ✅ |
| `ADMIN_ID` | @userinfobot se apna numeric Telegram ID | ✅ |
| `WEBHOOK_HOST` | Render deploy hone ke baad milega | ✅ |
| `FB_APP_ID` | Meta Developer App → Settings → Basic | ✅ |
| `FB_APP_SECRET` | Meta Developer App → Settings → Basic | ✅ |
| `IG_VERIFY_TOKEN` | Khud koi random string choose karo | ✅ |
| `DB_PATH` | Default: `bot_data.db` | ⬜ optional |
| `PORT` | Render khud set karta hai | ⬜ optional |

---

## 🚀 Setup Guide

### 1️⃣ Telegram Bot banao
- [@BotFather](https://t.me/BotFather) se naya bot banao → `BOT_TOKEN` milega
- [@userinfobot](https://t.me/userinfobot) ko message karo → `ADMIN_ID` milega

### 2️⃣ Meta Developer App banao
1. [developers.facebook.com/apps](https://developers.facebook.com/apps) → **Create App** → type: `Business`
2. **Instagram Graph API** + **Facebook Login** products add karo
3. Settings → Basic se `FB_APP_ID` aur `FB_APP_SECRET` copy karo
4. Valid OAuth Redirect URI:
   ```
   https://your-app.onrender.com/oauth/instagram/callback
   ```
5. Webhooks product add karo → subscribe to `comments` field:
   ```
   Callback URL:  https://your-app.onrender.com/instagram/webhook
   Verify Token:  (apna chosen IG_VERIFY_TOKEN)
   ```
6. App Roles me apna Facebook account **Administrator** add karo — App
   Review ki zarurat nahi kyunki sirf tu use karega (Development mode)

### 3️⃣ GitHub par push karo
```bash
cd instabot
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/<username>/<repo>.git
git push -u origin main
```
> ⚠️ `.env` file kabhi commit mat karna — secrets sirf Render dashboard me

### 4️⃣ Render par deploy karo
1. Render → **New → Web Service** → apna GitHub repo select karo
2. `render.yaml` auto-detect hoga, ya manually:
   | Setting | Value |
   |---|---|
   | Build Command | `pip install -r requirements.txt` |
   | Start Command | `gunicorn bot:app --bind 0.0.0.0:$PORT` |
3. Environment tab me saare variables daalo
4. Deploy hone ke baad mila URL wapas `WEBHOOK_HOST` me daalo aur **restart** karo

### 5️⃣ Test karo
- [ ] Telegram pe `/start` bhejo
- [ ] **Connect Instagram** se account authorize karo
- [ ] Template + keyword add karo
- [ ] Apni post pe wahi keyword comment karke DM check karo

---

## 🧠 Important Notes

- ✅ Official Meta Graph API use hota hai — safe, koi account-ban risk nahi
- 📎 Instagram account **Business/Creator** type + Facebook Page se linked hona zaroori hai
- ⏳ Access token ~60 din chalta hai — expire hone pe "Connect Instagram" dobara karo
- 🔐 App Development mode me hai, isliye sirf tera account connect ho payega

---

<div align="center">

Made for personal Instagram automation • Built with pyTelegramBotAPI + Flask

</div>
