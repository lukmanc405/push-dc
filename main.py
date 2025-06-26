import aiohttp
import asyncio
import os
import time
import random
from datetime import datetime
from dotenv import load_dotenv

RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
RESET = "\033[0m"

load_dotenv()
TOKEN = os.getenv("TOKEN")
GEMINI_KEY = os.getenv("GEMINI_API_KEY")

print(f"{CYAN}\nPILIH MODE:{RESET}")
print(f"{CYAN}1. KIRIM BIASA{RESET}")
print(f"{CYAN}2. KIRIM & HAPUS STEALTH{RESET}")
print(f"{CYAN}3. AI CHAT (GEMINI){RESET}")
print(f"{CYAN}4. EMOTICON RANDOM{RESET}")
mode = input("MODE: ").strip()

min_delay = int(input("DELAY MINIMAL (DETIK): "))
max_delay = int(input("DELAY MAKSIMAL (DETIK): "))

hapus_delay = 0.2 if mode == "2" else 0

monitor_admin = input("MONITOR ADMIN? (Y/N): ").strip().upper() == "Y"
TARGET_USER_IDS = []
if monitor_admin:
    if not os.path.exists("admin.txt") or os.path.getsize("admin.txt") == 0:
        print(f"{YELLOW}[!] FILE admin.txt KOSONG ATAU BELUM ADA.{RESET}")
        admin_input = input("MASUKKAN ID ADMIN (pisah koma jika banyak): ").strip()
        ids = [id_.strip() for id_ in admin_input.split(",") if id_.strip().isdigit()]
        with open("admin.txt", "w") as f:
            for id_ in ids:
                f.write(f"{id_}\n")
        print(f"{GREEN}[✓] ID ADMIN DISIMPAN KE admin.txt{RESET}")
        TARGET_USER_IDS = [int(id_) for id_ in ids]
    else:
        with open("admin.txt") as f:
            TARGET_USER_IDS = [int(line.strip()) for line in f if line.strip().isdigit()]

start_time = time.time()
total_sent = 0
headers_dc = {"Authorization": TOKEN, "Content-Type": "application/json"}
headers_gemini = {
    "Content-Type": "application/json",
    "x-goog-api-key": GEMINI_KEY
}
url_gemini = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent"

with open("pesan.txt") as f:
    pesan_pool = [line.strip() for line in f if line.strip()]
with open("channel.txt") as f:
    channels = [line.strip().split(",") for line in f if "," in line]
with open("emote.txt") as f:
    emotes = [line.strip() for line in f if line.strip()]

pesan_queue = list(pesan_pool)
random.shuffle(pesan_queue)
os.makedirs("log", exist_ok=True)

async def shutdown_bot(reason):
    print(f"{RED}[!] BOT DIMATIKAN - {reason}{RESET}")
    os._exit(0)

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
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    async with aiohttp.ClientSession() as session:
        async with session.post(url_gemini, headers=headers_gemini, json=payload) as res:
            if res.status in (200, 201):
                data = await res.json()
                cand = data.get("candidates", [])
                if cand and "content" in cand[0]:
                    parts = cand[0]["content"].get("parts", [])
                    return parts[0]["text"] if parts else "[KOSONG]"
                return "[!] GEMINI TIDAK MEMBERI HASIL"
            return f"{RED}[GEMINI ERROR] STATUS {res.status}{RESET}"

async def kirim_pesan(session, channel_name, channel_id, content):
    global total_sent
    try:
        async with session.post(
            f"https://discord.com/api/v9/channels/{channel_id}/messages",
            json={"content": content}, headers=headers_dc
        ) as res:
            now = datetime.now().strftime("%H:%M:%S")
            if res.status in (200, 201):
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
                    ) as dres:
                        if dres.status == 204:
                            print(f"{YELLOW}[-] {now} | PESAN DIHAPUS DI {channel_name.upper()}{RESET}")
                        else:
                            print(f"{RED}[!] GAGAL HAPUS: {dres.status}{RESET}")

            elif res.status == 429:
                retry = (await res.json()).get("retry_after", 5)
                print(f"{RED}[RATE LIMIT] TUNGGU {retry} DETIK...{RESET}")
                await asyncio.sleep(retry)
            else:
                print(f"{RED}[ERROR] {res.status} | {await res.text()}{RESET}")
    except Exception as e:
        print(f"{RED}[EXCEPTION] {e}{RESET}")

async def monitor_admin_status(session):
    while True:
        for admin_id in TARGET_USER_IDS:
            async with session.get(
                f"https://discord.com/api/v9/users/{admin_id}/profile",
                headers=headers_dc
            ) as res:
                if res.status == 200:
                    data = await res.json()
                    status = data.get("user", {}).get("status", "")
                    if status != "offline":
                        print(f"{YELLOW}[!] ADMIN ONLINE TERDETEKSI: {admin_id}{RESET}")
                await asyncio.sleep(1)

            for name, cid in channels:
                async with session.get(
                    f"https://discord.com/api/v9/channels/{cid.strip()}/messages?limit=1",
                    headers=headers_dc
                ) as res:
                    if res.status == 200:
                        messages = await res.json()
                        if messages:
                            msg = messages[0]
                            author_id = msg.get("author", {}).get("id", "")
                            if int(author_id) in TARGET_USER_IDS:
                                print(f"{RED}[!] ADMIN {author_id} MENGIRIM PESAN: {msg.get('content', '')}{RESET}")
                                await shutdown_bot(f"ADMIN {author_id} MENGIRIM PESAN!")
        await asyncio.sleep(10)

async def main():
    print(f"{CYAN}\nBOT AKTIF. TEKAN CTRL+C UNTUK BERHENTI.\n{RESET}")
    async with aiohttp.ClientSession() as session:
        if monitor_admin:
            asyncio.create_task(monitor_admin_status(session))

        while True:
            if mode == "3":
                content = await chat_gemini("Buatkan pesan pendek ramah dan menarik untuk Discord.")
            elif mode == "4":
                content = random.choice(emotes)
            else:
                content = await ambil_pesan_rotasi()

            await asyncio.gather(*[
                kirim_pesan(session, name.strip(), cid.strip(), content)
                for name, cid in channels
            ])
            await asyncio.sleep(random.randint(min_delay, max_delay))

try:
    asyncio.run(main())
except KeyboardInterrupt:
    elapsed = time.time() - start_time
    print(f"{RED}\nBOT DIMATIKAN MANUAL.{RESET}")
    print(f"{CYAN}⏱ DURASI: {int(elapsed//60)}m {int(elapsed%60)}s{RESET}")
    print(f"{GREEN}📨 TOTAL PESAN: {total_sent}{RESET}")
