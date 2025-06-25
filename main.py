import aiohttp
import asyncio
import random
import os
from datetime import datetime
from dotenv import load_dotenv

# Load .env
load_dotenv()

TOKEN = os.getenv("TOKEN")
OPENAI_KEY = os.getenv("OPENAI_KEY")

if not TOKEN:
    raise Exception("Token Discord tidak ditemukan! Cek file .env")

if not OPENAI_KEY:
    raise Exception("API Key OpenAI tidak ditemukan! Cek file .env")

# Baca data dari file
with open("pesan.txt") as f:
    messages = [line.strip() for line in f if line.strip()]

with open("channel.txt") as f:
    channels = [line.strip().split(",") for line in f if "," in line]

with open("emote.txt") as f:
    emotes = [line.strip() for line in f if line.strip()]

# Konfigurasi Header
headers_dc = {
    "Authorization": TOKEN,
    "Content-Type": "application/json"
}

headers_ai = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {OPENAI_KEY}"
}

url_ai = "https://api.openai.com/v1/chat/completions"

# Log
os.makedirs("log", exist_ok=True)

# Input User
print("\nPILIH MODE:")
print("1. Kirim biasa (tidak dihapus)")
print("2. Kirim lalu hapus otomatis")
print("3. AI Chat (pesan dari GPT-3.5)")
print("4. Kirim emoticon random")
mode = input("Mode: ").strip()

min_delay = int(input("Delay minimal antar pesan (detik): "))
max_delay = int(input("Delay maksimal antar pesan (detik): "))

hapus_delay = 0
if mode == "2":
    hapus_delay = int(input("Delay hapus pesan (detik): "))


async def log(channel_name, content):
    now = datetime.now().strftime("%H:%M:%S")
    with open(f"log/{channel_name}.txt", "a") as f:
        f.write(f"[{now}] {content}\n")


async def chat_ai(prompt):
    payload = {
        "model": "gpt-3.5-turbo",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 100
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(url_ai, headers=headers_ai, json=payload) as res:
            print(f"[DEBUG AI] Status: {res.status}")
            response_text = await res.text()
            print(f"[DEBUG AI] Respon: {response_text}")

            if res.status in [200, 201]:
                data = await res.json()
                return data["choices"][0]["message"]["content"]
            else:
                return "[ERROR AI] Gagal ambil respon"


async def kirim_pesan(session, channel_name, channel_id, content):
    try:
        payload = {"content": content}
        async with session.post(f"https://discord.com/api/v9/channels/{channel_id}/messages",
                                json=payload, headers=headers_dc) as res:
            now = datetime.now().strftime("%H:%M:%S")
            if res.status in [200, 201]:
                data = await res.json()
                msg_id = data["id"]
                print(f"[✓] {now} | {channel_name} | {content}")
                await log(channel_name, content)

                if mode == "2":
                    await asyncio.sleep(hapus_delay)
                    async with session.delete(
                        f"https://discord.com/api/v9/channels/{channel_id}/messages/{msg_id}",
                        headers=headers_dc
                    ) as del_res:
                        if del_res.status == 204:
                            print(f"[-] {now} | Pesan dihapus di {channel_name}")

            elif res.status == 429:
                retry = (await res.json()).get("retry_after", 5)
                print(f"[RATE LIMIT] Tunggu {retry} detik...")
                await asyncio.sleep(retry)

            else:
                print(f"[ERROR] {res.status} | {await res.text()}")

    except Exception as e:
        print(f"[EXCEPTION] {e}")


async def main():
    async with aiohttp.ClientSession() as session:
        while True:
            if mode == "3":
                content = await chat_ai("Berikan pesan singkat untuk Discord.")
            elif mode == "4":
                content = random.choice(emotes)
            else:
                content = random.choice(messages)

            tasks = [
                kirim_pesan(session, name.strip(), cid.strip(), content)
                for name, cid in channels
            ]
            await asyncio.gather(*tasks)

            delay = random.randint(min_delay, max_delay)
            await asyncio.sleep(delay)


try:
    print("\nBOT AKTIF. Tekan CTRL+C untuk berhenti.\n")
    asyncio.run(main())
except KeyboardInterrupt:
    print("\nBot dihentikan.")
