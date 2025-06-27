# MULTI_ACCOUNT_BOT.PY - AUTO-TABLE WIDTH
import aiohttp
import asyncio
import os
import sys
import time
import random
from datetime import datetime
from itertools import cycle
from dotenv import dotenv_values

# WARNA ANSI
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
MAGENTA = "\033[95m"
RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"

ACCOUNT_COLORS = cycle([RED, GREEN, YELLOW, CYAN, MAGENTA])

# CLEAR TERMINAL
os.system("cls" if os.name == "nt" else "clear")

# LOAD .ENV
config = dotenv_values(".env")
GEMINI_KEY = config.get("GEMINI_API_KEY")
OPENAI_KEY = config.get("OPENAI_API_KEY")

# === FUNGSI UTILITAS ===
def read_lines(filename):
    if not os.path.exists(filename): return []
    with open(filename) as f:
        return [line.strip() for line in f if line.strip()]

def print_header():
    print(f"{BOLD}{CYAN}┌────────────────────────────────────────────┐")
    print(f"│       🤖  MULTI ACCOUNT DISCORD BOT       │")
    print(f"└────────────────────────────────────────────┘{RESET}")

def loading_line(msg, delay=0.03):
    for c in msg:
        sys.stdout.write(c)
        sys.stdout.flush()
        time.sleep(delay)
    print()

def validate_env(aktifkan_ai_chat):
    errors = []

    token_keys = [k for k in config if k.startswith("TOKEN_")]
    if not token_keys:
        errors.append("❌ Tidak ada TOKEN_ ditemukan. Tambahkan seperti TOKEN_1, TOKEN_2, ...")

    for k in token_keys:
        v = config[k].strip()
        if not v or len(v) < 20:
            errors.append(f"❌ {k} FORMAT SALAH.")

    if aktifkan_ai_chat:
        if "GEMINI_API_KEY" not in config or not config["GEMINI_API_KEY"].strip():
            errors.append("❌ GEMINI_API_KEY belum diisi, padahal mode AI Chat dipilih.")

        if config.get("OPENAI_API_KEY", "").strip() and not config["OPENAI_API_KEY"].startswith("sk-"):
            errors.append("⚠️ OPENAI_API_KEY tampak tidak valid (tidak mengandung 'sk-').")

    if errors:
        print(f"\n{RED}[!] TERDAPAT MASALAH DI FILE .env:{RESET}")
        for err in errors:
            print(f"{RED}- {err}{RESET}")
        exit()

# === DATA INPUT ===
TOKENS = [v for k, v in config.items() if k.startswith("TOKEN_") and v]
CHANNELS = [line.split(",") for line in read_lines("channel.txt") if "," in line]
PESAN_POOL = read_lines("pesan.txt")
EMOTES = read_lines("emote.txt")
TARGET_USER_IDS = [int(x) for x in read_lines("admin.txt") if x.isdigit()]
MONITOR_CHANNELS = [x for x in read_lines("monitor_channel.txt") if x.isdigit()]

# === KONFIGURASI DELAY ===
def input_int(prompt):
    while True:
        try:
            val = input(prompt).strip()
            if not val.isdigit():
                raise ValueError("HARUS ANGKA BULAT.")
            return int(val)
        except Exception as e:
            print(f"{RED}[X] INPUT TIDAK VALID: {e}{RESET}")

loading_line(f"{CYAN}▶ MASUKKAN DELAY PENGIRIMAN...{RESET}")
min_delay = input_int("DELAY MINIMAL (DETIK): ")
max_delay = input_int("DELAY MAKSIMAL (DETIK): ")
account_delay = 1  # jeda antar akun dalam detik

# === PEMILIHAN MODE PER AKUN ===
def input_mode(prompt):
    while True:
        val = input(prompt).strip()
        if val in ("1", "2", "3", "4"):
            return val
        print(f"{RED}[!] MASUKKAN HARUS ANTARA 1-4{RESET}")

MODES = {}
SEND_COUNTER = {}
pakai_ai_chat = False

for idx, token in enumerate(TOKENS, 1):
    color = next(ACCOUNT_COLORS)
    print(f"{color}\n╔═ KONFIGURASI AKUN #{idx} ═══════════════════{RESET}")
    print(f"{color}║ 1. KIRIM BIASA\n║ 2. KIRIM & HAPUS STEALTH\n║ 3. AI CHAT GEMINI\n║ 4. EMOTICON RANDOM{RESET}")
    mode = input_mode(f"{color}╚═▶ PILIH MODE (1-4): {RESET}")
    if mode == "3":
        pakai_ai_chat = True
    MODES[token] = (mode, color)
    SEND_COUNTER[token] = 0

# Validasi .env SETELAH user memilih mode
validate_env(pakai_ai_chat)

# === GLOBAL ===
start_time = time.time()

# === FUNGSI ASYNC ===
async def chat_gemini(prompt):
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent"
    headers = {
        "Content-Type": "application/json",
        "x-goog-api-key": GEMINI_KEY
    }
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, json=payload) as res:
            data = await res.json()
            return data.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "(KOSONG)")

async def kirim_pesan(session, token, channel_name, channel_id, content, color, akun_id):
    headers = {"Authorization": token, "Content-Type": "application/json"}
    async with session.post(
        f"https://discord.com/api/v9/channels/{channel_id}/messages",
        json={"content": content}, headers=headers
    ) as res:
        now = datetime.now().strftime("%H:%M:%S")
        if res.status in (200, 201):
            SEND_COUNTER[token] += 1
            baris_atas = f"AKUN #{akun_id} | ⏱ {now} | 📤 {channel_name.upper()}"
            baris_pesan = f"PESAN : {content[:60].upper()}"
            lebar = max(len(baris_atas), len(baris_pesan)) + 4
            garis = "━" * lebar
            print(f"{color}┏━ {baris_atas}")
            print(f"┣━ {baris_pesan}")
            print(f"┗{garis}{RESET}")
        elif res.status == 429:
            retry = (await res.json()).get("retry_after", 5)
            print(f"{YELLOW}[AKUN #{akun_id}] ⏳ RATE LIMIT {retry} DETIK{RESET}")
            await asyncio.sleep(retry)
        else:
            print(f"{RED}[AKUN #{akun_id}] [GAGAL] {res.status} | {await res.text()}{RESET}")

async def monitor_admin(session, token, color):
    headers = {"Authorization": token, "Content-Type": "application/json"}
    while True:
        for cid in MONITOR_CHANNELS:
            async with session.get(
                f"https://discord.com/api/v9/channels/{cid}/messages?limit=1",
                headers=headers
            ) as res:
                if res.status == 200:
                    messages = await res.json()
                    if messages:
                        msg = messages[0]
                        author_id = msg.get("author", {}).get("id")
                        timestamp = msg.get("timestamp", "")
                        if int(author_id) in TARGET_USER_IDS:
                            tstr = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            print(f"{color}[✘] BOT DIHENTIKAN KARENA ADMIN MENGIRIM PESAN PADA {tstr}{RESET}")
                            await tampilkan_ringkasan()
                            os._exit(0)
        await asyncio.sleep(5)

async def akun_worker(token, mode, color, akun_id):
    async with aiohttp.ClientSession() as session:
        pesan_queue = PESAN_POOL.copy()
        random.shuffle(pesan_queue)

        if MONITOR_CHANNELS:
            asyncio.create_task(monitor_admin(session, token, color))

        while True:
            if not pesan_queue:
                pesan_queue = PESAN_POOL.copy()
                random.shuffle(pesan_queue)

            if mode == "3":
                content = await chat_gemini("BUAT PESAN PENDEK RAMAH UNTUK DISCORD")
            elif mode == "4":
                content = random.choice(EMOTES)
            else:
                content = pesan_queue.pop(0)

            for name, cid in CHANNELS:
                await kirim_pesan(session, token, name, cid, content, color, akun_id)
                if mode == "2":
                    await asyncio.sleep(0.5)
            await asyncio.sleep(random.randint(min_delay, max_delay))

async def tampilkan_ringkasan():
    elapsed = int(time.time() - start_time)
    print(f"\n{BOLD}{CYAN}┌────────────────────────────────────────────┐")
    print(f"│             🔻 BOT TELAH DIMATIKAN          │")
    print(f"├────────────────────────────────────────────┤")
    print(f"│ DURASI : {elapsed // 60} MENIT {elapsed % 60} DETIK")
    for idx, token in enumerate(SEND_COUNTER, 1):
        jumlah = SEND_COUNTER[token]
        print(f"│ AKUN #{idx} TELAH MENGIRIM : {jumlah} PESAN")
    print(f"└────────────────────────────────────────────┘{RESET}\n")

async def main():
    print_header()
    for idx, (token, (mode, color)) in enumerate(MODES.items()):
        asyncio.create_task(akun_worker(token, mode, color, idx + 1))
        await asyncio.sleep(account_delay)
    while True:
        await asyncio.sleep(3600)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        asyncio.run(tampilkan_ringkasan())
