import requests
import random
import time
import os

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
    words = f.readlines()

# Baca daftar channel (pakai koma)
with open("channel.txt", "r") as f:
    channels = [line.strip().split(",") for line in f if "," in line]

# Input konfigurasi
auto_delete = input("AUTO DELETE PESAN? (Y/N): ").strip().lower()
if auto_delete == 'y':
    waktu_hapus = int(input("SET WAKTU HAPUS PESAN (DETIK): "))
else:
    waktu_hapus = 0

waktu_kirim = int(input("SET WAKTU KIRIM PESAN (DETIK): "))

# Countdown
print(f"\n{YELLOW}[INFO]{RESET} MULAI DALAM:")
for i in range(3, 0, -1):
    print(f"{i}")
    time.sleep(1)

# Bersihkan terminal
os.system("clear")

print(f"\n{YELLOW}[INFO]{RESET} MENJALANKAN BOT...")
print(f"{YELLOW}[INFO]{RESET} JIKA INGIN BERHENTI, TEKAN CTRL+C\n")

total_terkirim = 0

try:
    while True:
        for channel_name, channel_id in channels:
            payload = {
                'content': random.choice(words).strip()
            }

            headers = {
                'Authorization': authorization
            }

            # Kirim pesan
            r = requests.post(
                f"https://discord.com/api/v9/channels/{channel_id.strip()}/messages",
                data=payload,
                headers=headers
            )

            if r.status_code in [200, 201]:
                total_terkirim += 1
                print(f"{GREEN}[✓]{RESET} CHANNEL: {channel_name.strip()} | PESAN: {payload['content']}")
                print(f"{YELLOW}    TOTAL TERKIRIM: {total_terkirim}{RESET}")
            elif r.status_code == 403:
                print(f"{RED}[!] AKSES DITOLAK KE CHANNEL '{channel_name.strip()}' (403 FORBIDDEN){RESET}")
            elif "ban" in r.text.lower() or "warn" in r.text.lower():
                print(f"{RED}[!!] PERINGATAN: MUNGKIN AKUN INI MENDAPAT PERINGATAN ATAU TERKENA BANNED!{RESET}")
                print(f"{RED}     RESPON: {r.text}{RESET}")
            else:
                print(f"{RED}[!] GAGAL KIRIM KE {channel_name.strip()}: {r.status_code} - {r.text}{RESET}")

            # Auto delete
            if auto_delete == 'y':
                time.sleep(waktu_hapus)
                get_res = requests.get(f'https://discord.com/api/v9/channels/{channel_id.strip()}/messages', headers=headers)
                if get_res.status_code == 200:
                    messages = get_res.json()
                    if messages:
                        message_id = messages[0]['id']
                        del_res = requests.delete(
                            f'https://discord.com/api/v9/channels/{channel_id.strip()}/messages/{message_id}',
                            headers=headers
                        )
                        if del_res.status_code == 204:
                            print(f"{RED}[-] PESAN BERHASIL DIHAPUS DARI CHANNEL '{channel_name.strip()}'{RESET}")
                        else:
                            print(f"{RED}[!] GAGAL MENGHAPUS PESAN: {del_res.status_code}{RESET}")
                    else:
                        print(f"{RED}[!] TIDAK ADA PESAN UNTUK DIHAPUS DI CHANNEL '{channel_name.strip()}'{RESET}")
                else:
                    print(f"{RED}[!] GAGAL MENGAMBIL PESAN DARI {channel_name.strip()}: {get_res.status_code}{RESET}")

            time.sleep(waktu_kirim)

except KeyboardInterrupt:
    print(f"\n{YELLOW}[STOP]{RESET} PROGRAM DIHENTIKAN OLEH PENGGUNA (CTRL+C)")
    print(f"{YELLOW}[INFO]{RESET} TOTAL PESAN TERKIRIM SEBELUM BERHENTI: {total_terkirim}")
