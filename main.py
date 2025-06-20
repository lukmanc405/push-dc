import requests
import random
import time
import os
from datetime import datetime

# ANSI Color
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
WHITE = "\033[97m"
RESET = "\033[0m"

# Baca token
with open("token.txt", "r") as f:
    authorization = f.readline().strip()

# Baca pesan
with open("pesan.txt", "r") as f:
    words = [line.strip() for line in f if line.strip()]

# Baca daftar channel
with open("channel.txt", "r") as f:
    channels = [line.strip().split(",") for line in f if "," in line]

# Input konfigurasi
auto_delete = input("AUTO DELETE PESAN? (Y/N): ").strip().lower()
waktu_hapus = int(input("SET WAKTU HAPUS PESAN (DETIK): ")) if auto_delete == 'y' else 0
waktu_kirim = int(input("SET WAKTU KIRIM PESAN (DETIK): "))

# Countdown
print(f"\n{YELLOW}[INFO]{RESET} MULAI DALAM:")
for i in range(3, 0, -1):
    print(f"{i}")
    time.sleep(1)

os.system("clear")

print(f"{YELLOW}[INFO]{RESET} BOT AKTIF. TEKAN CTRL+C UNTUK BERHENTI.\n")

headers = {
    'Authorization': authorization,
    'Content-Type': 'application/json'
}

total_terkirim = 0

try:
    while True:
        for channel_name, channel_id in channels:
            content = random.choice(words)
            payload = {"content": content}
            now = datetime.now().strftime("%H:%M:%S")

            try:
                # Kirim pesan
                res = requests.post(
                    f"https://discord.com/api/v9/channels/{channel_id.strip()}/messages",
                    json=payload,
                    headers=headers
                )

                if res.status_code in [200, 201]:
                    message_id = res.json()['id']
                    total_terkirim += 1
                    print(f"{GREEN}[✓]{RESET} {now} | {channel_name.strip()} | {content}")
                    print(f"{YELLOW}    TOTAL TERKIRIM: {total_terkirim}{RESET}")

                    # Auto delete
                    if auto_delete == 'y':
                        time.sleep(waktu_hapus)
                        del_res = requests.delete(
                            f"https://discord.com/api/v9/channels/{channel_id.strip()}/messages/{message_id}",
                            headers=headers
                        )
                        if del_res.status_code == 204:
                            print(f"{RED}[-] {datetime.now().strftime('%H:%M:%S')} | PESAN DIHAPUS DI '{channel_name.strip()}'{RESET}")
                        else:
                            print(f"{RED}[!] GAGAL HAPUS PESAN: {del_res.status_code} - {del_res.text}{RESET}")

                elif res.status_code == 403:
                    print(f"{RED}[!] {now} | AKSES DITOLAK KE '{channel_name.strip()}' (403){RESET}")
                elif res.status_code == 429:
                    retry_after = res.json().get("retry_after", 5)
                    print(f"{YELLOW}[RATE LIMIT]{RESET} {now} | Menunggu {retry_after} detik...")
                    time.sleep(retry_after)
                else:
                    print(f"{RED}[!] {now} | GAGAL KIRIM KE '{channel_name.strip()}': {res.status_code} - {res.text}{RESET}")

            except Exception as e:
                print(f"{RED}[EXCEPTION]{RESET} {now} | {e}")

            time.sleep(waktu_kirim)

except KeyboardInterrupt:
    print(f"\n{YELLOW}[STOP]{RESET} PROGRAM DIHENTIKAN OLEH PENGGUNA")
    print(f"{YELLOW}[INFO]{RESET} TOTAL PESAN TERKIRIM: {total_terkirim}")