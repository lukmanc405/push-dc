import aiohttp
import asyncio
import random
import os
import time
from datetime import datetime

# ANSI Color
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RESET = "\033[0m"

# BACA KONFIGURASI
with open("token.txt") as f:
    token = f.readline().strip()

with open("pesan.txt") as f:
    messages = [line.strip() for line in f if line.strip()]

with open("channel.txt") as f:
    channels = [line.strip().split(",") for line in f if "," in line]

# INPUT USER
auto_delete = input("AUTO DELETE PESAN? (Y/N): ").lower() == 'y'
kirim_delay = int(input("SET WAKTU KIRIM PESAN (DETIK): "))
mode_verbose = input("VERBOSE MODE? (Y/N): ").lower() == 'y'
rotasi_durasi = int(input("ROTASI PESAN SETIAP BERAPA DETIK?: "))

# STATE
log_file = open("log.txt", "a")
pesan_index = 0  # untuk rotasi pesan
total_terkirim = 0

headers = {
    'Authorization': token,
    'Content-Type': 'application/json'
}

# Countdown
print(f"{YELLOW}[INFO]{RESET} MULAI DALAM:")
for i in range(3, 0, -1):
    print(i)
    time.sleep(1)

# Clear screen sesuai OS
os.system('cls' if os.name == 'nt' else 'clear')
print(f"{YELLOW}[INFO]{RESET} BOT AKTIF. TEKAN CTRL+C UNTUK BERHENTI.\n")

# Fungsi Log
async def log(text):
    now = datetime.now().strftime("%H:%M:%S")
    log_file.write(f"[{now}] {text}\n")
    log_file.flush()

# Fungsi Kirim Pesan
async def kirim_pesan(session, channel_name, channel_id, content):
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
                if mode_verbose:
                    print(f"{GREEN}[✓]{RESET} {now} | {channel_name} | {content}")
                    print(f"{YELLOW}    TOTAL TERKIRIM: {total_terkirim}{RESET}")
                await log(f"{channel_name} >> {content}")

                if auto_delete:
                    async with session.delete(
                        f'https://discord.com/api/v9/channels/{channel_id}/messages/{msg_id}',
                        headers=headers
                    ) as del_res:
                        if del_res.status == 204 and mode_verbose:
                            print(f"{RED}[-]{RESET} {now} | PESAN DIHAPUS DI {channel_name}")
            elif res.status == 429:
                retry = (await res.json()).get("retry_after", 5)
                if mode_verbose:
                    print(f"{YELLOW}[RATE LIMIT]{RESET} Menunggu {retry} detik...")
                await asyncio.sleep(retry)
            else:
                if mode_verbose:
                    print(f"{RED}[ERROR]{RESET} {res.status} | {await res.text()}")

    except Exception as e:
        if mode_verbose:
            print(f"{RED}[EXCEPTION]{RESET} {e}")
        await log(f"[ERROR] {e}")

# Main Loop
async def main():
    global pesan_index
    async with aiohttp.ClientSession() as session:
        while True:
            pesan_index = (pesan_index + 1) % len(messages)
            content = messages[pesan_index]
            tasks = [
                kirim_pesan(session, name.strip(), cid.strip(), content)
                for name, cid in channels
            ]
            await asyncio.gather(*tasks)
            await asyncio.sleep(kirim_delay)

# Run Program
try:
    asyncio.run(main())
except KeyboardInterrupt:
    log_file.close()
    print(f"{YELLOW}[INFO]{RESET} PROGRAM DIHENTIKAN.")
