# Push-DC Bot 🚀

**Push-DC** adalah bot Discord asynchronous ringan yang dibuat dengan `aiohttp` dan `asyncio`. Bot ini memudahkan Anda untuk mengirim pesan secara otomatis ke berbagai channel, mendukung rotasi pesan, penghapusan pesan otomatis, serta logging detil.

---

## 📖 Daftar Isi

1. [Fitur Utama](#-fitur-utama)
2. [Prasyarat](#-prasyarat)
3. [Instalasi](#-instalasi)
4. [Konfigurasi](#-konfigurasi)
5. [Penggunaan](#-penggunaan)
6. [Opsi Tambahan](#-opsi-tambahan)
7. [Logging & Debugging](#-logging--debugging)
8. [Deployment di Termux/VPS](#-deployment-di-termuxvps)
9. [Troubleshooting](#-troubleshooting)
10. [Kontribusi](#-kontribusi)
11. [Lisensi](#-lisensi)

---

## ✨ Fitur Utama

* 🔄 **Rotasi Pesan Otomatis**: Pilih dari daftar di `pesan.txt` dan kirim sesuai interval.
* 🗑️ **Auto Delete**: Hapus pesan setelah delay tertentu untuk menjaga kebersihan channel.
* 📝 **Verbose Mode**: Log detail ke console dan file `log.txt`.
* ⏱️ **Delay Configurable**: Atur waktu kirim, waktu hapus, dan durasi rotasi.
* ⚡ **High Performance**: Dibangun dengan `aiohttp` untuk concurrency optimal.

---

## 📋 Prasyarat

* **Python**: Versi 3.7 atau lebih baru
* **Git**: Untuk clone repository
* **Termux / VPS**: Akses terminal (Termux di Android atau Debian/Ubuntu di VPS)

---

## 🛠️ Instalasi

```bash
# 1. Clone repository
git clone https://github.com/lukmanc405/push-dc.git
cd push-dc

# 2. Update sistem
# Termux:
pkg update && pkg upgrade -y
# Debian/Ubuntu:
apt update && apt upgrade -y

# 3. Install dependencies
# Termux:
pkg install python git openssl -y
# Debian/Ubuntu:
apt install python3 git openssl -y

# 4. Install Python packages
pip install --upgrade pip
pip install requests colorama aiohttp
```

---

## ⚙️ Konfigurasi

1. **token.txt**
   Masukkan **Bot Token** Discord (dapat diambil dari Developer Portal).

2. **pesan.txt**
   Tambahkan **satu** pesan per baris. Contoh:

   ```
   ```

Hello, welcome to our server!
Don’t miss our latest update.
Join the event now!

```

3. **channel.txt**  
   Format tiap baris: `nama_channel,channel_id`  
   Contoh:
```

event,123456789012345678
announcements,987654321098765432

````

4. **log.txt**  
   Otomatis dibuat saat bot berjalan untuk menyimpan histori log.

---

## ▶️ Penggunaan

Jalankan skrip utama:

```bash
python main.py
````

Ikuti **prompt** interaktif:

* **AUTO DELETE PESAN?** (Y/N)
* **SET WAKTU HAPUS PESAN (DETIK):** \[jika memilih Y]
* **SET WAKTU KIRIM PESAN (DETIK):**
* **VERBOSE MODE?** (Y/N)
* **ROTASI PESAN SETIAP BERAPA DETIK?:**

**Contoh Output:**

```
[INFO] MULAI DALAM:
3
2
1
[INFO] BOT AKTIF. TEKAN CTRL+C UNTUK BERHENTIKAN.
[✓] 14:30:05 | event | Hello, welcome to our server!
    TOTAL TERKIRIM: 1
[-] 14:30:07 | PESAN DIHAPUS DI event
```

---

## 🔧 Opsi Tambahan

* **Multi-Token Support**: Bisa tambahkan logika rotasi token untuk load balancing.
* **Mode Dry-Run**: Kirim ke console tanpa benar-benar memposting ke Discord.
* **Integration Webhook**: Tambah opsi untuk mengirim lewat Discord Webhook.
* **Notifikasi**: Kirim notifikasi via email atau Telegram saat error/complete.

---

## 🐞 Logging & Debugging

* **Console Output**: Default menampilkan summary. Aktifkan `VERBOSE MODE` untuk detail.
* **File Log**: `log.txt` menyimpan timestamp dan teks log.
* **Rate Limit Handling**: Otomatis tunggu sesuai `retry_after` saat status 429.

---

## 🚀 Deployment di Termux/VPS

1. **Setup Service** (systemd) di VPS:

   ```ini
   [Unit]
   Description=Push-DC Bot

   [Service]
   WorkingDirectory=/path/to/push-dc
   ExecStart=/usr/bin/python3 main.py
   Restart=always

   [Install]
   WantedBy=multi-user.target
   ```

   ```bash
   sudo mv push-dc.service /etc/systemd/system/
   sudo systemctl daemon-reload
   sudo systemctl enable push-dc
   sudo systemctl start push-dc
   ```

2. **Background di Termux**: pakai `tmux` atau `nohup`:

   ```bash
   pkg install tmux
   tmux new -s pushdc
   python main.py
   # tekan Ctrl+B, lalu D untuk detach.
   ```

---

## 🤔 Troubleshooting

* **403 Forbidden**: Pastikan Bot punya permission `Send Messages` & `Manage Messages`. Gunakan Bot Token, bukan user token.
* **No Permission**: Cek role Bot di Discord, tambahkan scope `bot` dengan izin sesuai.
* **404 / Channel Not Found**: Verifikasi `channel_id` benar dan Bot diundang ke server.
* **Rate Limit**: Biarkan bot auto-handle, atau atur `kirim_delay` lebih besar.

---

## 🤝 Kontribusi

1. Fork repository
2. Buat branch fitur (`git checkout -b fitur-xyz`)
3. Commit perubahan (`git commit -am 'Tambah fitur xyz'`)
4. Push ke branch (`git push origin fitur-xyz`)
5. Buat Pull Request

Harap patuhi **Code of Conduct**.

---

## 📜 Lisensi

MIT © 2025 LUKE

---

## 📬 Hubungi

* GitHub: [lukmanc405](https://github.com/lukmanc405)
