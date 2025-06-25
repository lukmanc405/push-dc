import aiohttp
import asyncio
import random
import os
import time
from datetime import datetime
from dotenv import load_dotenv

# ANSI Colors
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
MAGENTA = "\033[95m"
CYAN = "\033[96m"
RESET = "\033[0m"

# Load .env
load_dotenv()

TOKEN = os.getenv("TOKEN")
GEMINI_KEY = os.getenv("GEMINI_API_KEY")

# Jika TOKEN Discord kosong
if not TOKEN:
    print(f"{MAGENTA}\n[DISCORD] TOKEN TIDAK DITEMUKAN DI .env.{RESET}")
    TOKEN = input("MASUKKAN TOKEN DISCORD BOT KAMU: ").strip()
    with open(".env", "a") as f:
        f.write(f"\nTOKEN={TOKEN}")
    print(f"{GREEN}[✓] TOKEN BERHASIL DISIMPAN KE .env{RESET}")

# Jika API Key Gemini kosong
if not GEMINI_KEY:
    print(f"{MAGENTA}\n[GEMINI] API KEY TIDAK DITEMUKAN DI .env.{RESET}")
    GEMINI_KEY = input("MASUKKAN API KEY GOOGLE GEMINI: ").strip()
    with open(".env", "a") as f:
        f.write(f"\nGEMINI_API_KEY={GEMINI_KEY}")
    print(f"{GREEN}[✓] API KEY BERHASIL DISIMPAN KE .env{RESET}")

# Load file
with open("pesan.txt") as f:
    pesan_pool = [line.strip() for line in f if line.strip()]
with open("channel.txt") as f:
    channels = [line.strip().split(",") for line in f if "," in line]
with open("emote.txt") as f:
    emotes = [line.strip() for line in f if line.strip()]

pesan_queue = list(pesan_pool)
random.shuffle(pesan_queue)

headers_dc = {
    "Authorization": TOKEN,
    "Content-Type": "application/json"
}
headers_gemini = {
    "Content-Type": "application/json",
    "x-goog-api-key": GEMINI_KEY
}
url_gemini = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent"

os.makedirs("log", exist_ok=True)
start_time = time.time()
total_sent = 0

# Mode Input
print(f"{CYAN}\nPILIH MODE:{RESET}")
print(f"{CYAN}1. KIRIM BIASA (TIDAK DIHAPUS){RESET}")
print(f"{CYAN}2. KIRIM & HAPUS STEALTH (SUPER CEPAT){RESET}")
print(f"{CYAN}3. AI CHAT (GEMINI){RESET}")
print(f"{CYAN}4. EMOTICON RANDOM{RESET}")
mode = input("MODE: ").strip()

min_delay = int(input("DELAY MINIMAL (DETIK): "))
max_delay = int(input("DELAY MAKSIMAL (DETIK): "))

hapus_delay = 0
if mode == "2":
    hapus_delay = 0.2

async def log(channel_name, content):
    now = datetime.now().strftime("%H:%M:%S")
    with open(f"log/{channel_name}.txt", "a") as f:
        f.write(f"[{now}] {content}\n")

async def ambil_pesan_rotasi():
    global pesan_queue
    if not pesan_queue:
        pesan_queue = list(pesan_pool)
        random.shuffle(pesan_queue)
    return pesan_queue.pop(0)

async def chat_gemini(prompt):
    print(f"{MAGENTA}[GEMINI] MENGAMBIL PESAN...{RESET}")
    payload = {
        "contents": [{"parts": [{"text": prompt}]}]
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(url_gemini, headers=headers_gemini, json=payload) as res:
            if res.status in [200, 201]:
                data = await res.json()
                candidates = data.get("candidates", [])
                if candidates and "content" in candidates[0]:
                    parts = candidates[0]["content"].get("parts", [])
                    return parts[0]["text"] if parts else "[KOSONG]"
                return "[!] GEMINI TIDAK MEMBERI HASIL"
            else:
                return f"{RED}[GEMINI ERROR] STATUS {res.status}{RESET}"

async def kirim_pesan(session, channel_name, channel_id, content):
    global total_sent
    try:
        payload = {"content": content}
        async with session.post(f"https://discord.com/api/v9/channels/{channel_id}/messages",
                                json=payload, headers=headers_dc) as res:
            now = datetime.now().strftime("%H:%M:%S")
            if res.status in [200, 201]:
                data = await res.json()
                msg_id = data["id"]
                print(f"{GREEN}[✓] {now} | {channel_name.upper()} | {content.upper()}{RESET}")
                await log(channel_name, content)
                total_sent += 1

                if mode == "2":
                    await asyncio.sleep(hapus_delay)
                    async with session.delete(
                        f"https://discord.com/api/v9/channels/{channel_id}/messages/{msg_id}",
                        headers=headers_dc
                    ) as del_res:
                        if del_res.status == 204:
                            print(f"{YELLOW}[-] {now} | PESAN DIHAPUS DI {channel_name.upper()}{RESET}")
                        else:
                            print(f"{RED}[!] GAGAL HAPUS: {del_res.status}{RESET}")

            elif res.status == 429:
                retry = (await res.json()).get("retry_after", 5)
                print(f"{RED}[RATE LIMIT] TUNGGU {retry} DETIK...{RESET}")
                await asyncio.sleep(retry)

            else:
                print(f"{RED}[ERROR] {res.status} | {await res.text()}{RESET}")

    except Exception as e:
        print(f"{RED}[EXCEPTION] {e}{RESET}")

async def main():
    async with aiohttp.ClientSession() as session:
        while True:
            if mode == "3":
                content = await chat_gemini("BUATKAN PESAN PENDEK RAMAH DAN MENARIK UNTUK DISCORD.")
            elif mode == "4":
                content = random.choice(emotes)
            else:
                content = await ambil_pesan_rotasi()

            tasks = [
                kirim_pesan(session, name.strip(), cid.strip(), content)
                for name, cid in channels
            ]
            await asyncio.gather(*tasks)

            delay = random.randint(min_delay, max_delay)
            await asyncio.sleep(delay)

try:
    print(f"{CYAN}\nBOT AKTIF. TEKAN CTRL+C UNTUK BERHENTI.\n{RESET}")
    asyncio.run(main())
except KeyboardInterrupt:
    end_time = time.time()
    elapsed = end_time - start_time
    minutes = int(elapsed // 60)
    seconds = int(elapsed % 60)
    print(f"{RED}\nBOT DIHENTIKAN.{RESET}")
    print(f"{CYAN}⏱ DURASI BERJALAN: {minutes} MENIT {seconds} DETIK{RESET}")
    print(f"{GREEN}📨 TOTAL PESAN TERKIRIM: {total_sent}{RESET}")