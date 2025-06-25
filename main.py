import aiohttp
import asyncio
import random
import os
import time
import json
from datetime import datetime
from dotenv import load_dotenv

# Load .env
load_dotenv()

# ANSI Color
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RESET = "\033[0m"

# BACA KONFIGURASI DARI .env
token = os.getenv("TOKEN")
openai_key = os.getenv("OPENAI_KEY")

# BACA FILE LAIN
with open("pesan.txt") as f:
    messages = [line.strip() for line in f if line.strip()]

with open("channel.txt") as f:
    channels = [line.strip().split(",") for line in f if "," in line]

with open("emote.txt") as f:
    emotes = [line.strip() for line in f if line.strip()]

# INPUT USER
print("\nPILIH MODE:\n1. No Delete\n2. Delete\n3. AI Chat (GPT)\n4. Emot Only")
mode_pilihan = input("Pilih Mode (1/2/3/4): ")

min_delay = int(input("SET DELAY MINIMAL KIRIM PESAN (DETIK): "))
max_delay = int(input("SET DELAY MAKSIMAL KIRIM PESAN (DETIK): "))
rotasi_durasi = int(input("ROTASI PESAN SETIAP BERAPA DETIK?: "))

# STATE
pesan_index = 0
total_terkirim = 0
mode_verbose = True

headers = {
    'Authorization': token,
    'Content-Type': 'application/json'
}

# Countdown
print(f"{YELLOW}[INFO]{RESET} MULAI DALAM:")
for i in range(3, 0, -1):
    print(i)
    time.sleep(1)

os.system('cls' if os.name == 'nt' else 'clear')
print(f"{YELLOW}[INFO]{RESET} BOT AKTIF. TEKAN CTRL+C UNTUK BERHENTI.\n")

# Fungsi Log Per Channel
async def log(channel_name, text):
    now = datetime.now().strftime("%H:%M:%S")
    log_path = f"log_{channel_name}.txt"
    with open(log_path, "a") as f:
        f.write(f"[{now}] {text}\n")

# Fungsi Ambil Respon AI dari OpenAI
async def ai_response():
    prompt = random.choice(messages)
    url = "https://api.openai.com/v1/chat/completions"
    headers_ai = {
        "Authorization": f"Bearer {openai_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "gpt-3.5-turbo",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 50,
        "temperature": 0.7
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers_ai, json=payload) as res:
            if res.status == 200:
                data = await res.json()
                reply = data["choices"][0]["message"]["content"]
                return reply.strip()
            else:
                return "Error from AI"

# Fungsi Kirim Pesan
async def kirim_pesan(session, channel_name, channel_id, content, delete_after=False):
    global total_terkirim
    try:
        payload = {'content': content}
        async with session.post(f'https://discord.com/api/v9/channels/{channel_id}/messages',
                                json=payload, headers=headers) as res:
            now = datetime.now().strftime("%H:%M:%S")
            if res.status in [200, 201]:
                data = await res.json()
                msg_id = data['id']
                total_terkirim += 1
                print(f"{GREEN}[✓]{RESET} {now} | {channel_name} | {content}")
                print(f"{YELLOW}    TOTAL TERKIRIM: {total_terkirim}{RESET}")
                await log(channel_name, f">> {content}")

                if delete_after:
                    async with session.delete(
                        f'https://discord.com/api/v9/channels/{channel_id}/messages/{msg_id}',
                        headers=headers
                    ) as del_res:
                        if del_res.status == 204:
                            print(f"{RED}[-]{RESET} {now} | PESAN DIHAPUS DI {channel_name}")
            elif res.status == 429:
                retry = (await res.json()).get("retry_after", 5)
                print(f"{YELLOW}[RATE LIMIT]{RESET} Menunggu {retry} detik...")
                await asyncio.sleep(retry)
            else:
                print(f"{RED}[ERROR]{RESET} {res.status} | {await res.text()}")

    except Exception as e:
        print(f"{RED}[EXCEPTION]{RESET} {e}")
        await log(channel_name, f"[ERROR] {e}")

# Main Loop
async def main():
    global pesan_index
    async with aiohttp.ClientSession() as session:
        while True:
            pesan_index = (pesan_index + 1) % len(messages)
            
            if mode_pilihan == '1':  # No Delete
                content = messages[pesan_index]
                tasks = [kirim_pesan(session, name.strip(), cid.strip(), content, delete_after=False)
                         for name, cid in channels]
            
            elif mode_pilihan == '2':  # Delete
                content = messages[pesan_index]
                tasks = [kirim_pesan(session, name.strip(), cid.strip(), content, delete_after=True)
                         for name, cid in channels]

            elif mode_pilihan == '3':  # AI Chat
                content = await ai_response()
                tasks = [kirim_pesan(session, name.strip(), cid.strip(), content, delete_after=False)
                         for name, cid in channels]

            elif mode_pilihan == '4':  # Emot Only
                content = random.choice(emotes)
                tasks = [kirim_pesan(session, name.strip(), cid.strip(), content, delete_after=False)
                         for name, cid in channels]

            else:
                print(f"{RED}[ERROR]{RESET} Mode tidak dikenali!")
                break

            await asyncio.gather(*tasks)
            delay = random.randint(min_delay, max_delay)
            print(f"{YELLOW}[INFO]{RESET} Delay berikutnya: {delay} detik\n")
            await asyncio.sleep(delay)

# Run Program
try:
    asyncio.run(main())
except KeyboardInterrupt:
    print(f"{YELLOW}[INFO]{RESET} PROGRAM DIHENTIKAN.")
