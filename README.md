
# 🚀 PUSH DC 
![Visitors](https://visitor-badge.laobi.icu/badge?page_id=lukmanc405.push-dc)
![Downloads](https://img.shields.io/github/downloads/lukmanc405/push-dc/total?color=blue&label=Downloads)
![Stars](https://img.shields.io/github/stars/lukmanc405/push-dc?style=social)
[![Join Telegram](https://img.shields.io/badge/Join-Telegram-blue?logo=telegram)](https://t.me/detective_gems)

Bot **Discord** asynchronous untuk mengirim pesan otomatis ke banyak channel dari **banyak akun sekaligus**. Bisa kirim pesan biasa, auto hapus, AI Chat (Gemini), atau emoticon custom — dengan tampilan futuristik dan sistem validasi `.env`.

Dapat digunakan di **Termux (Android)** maupun **VSCode (PC)**.

---

## ⚙️ Persiapan

Siapkan file berikut di folder project:

- `.env` → Token-token akun Discord dan API key
- `channel.txt` → Daftar channel (format: `nama,channel_id`)
- `pesan.txt` → List pesan teks yang akan dikirim
- `emote.txt` → List emoticon custom Discord
- `admin.txt` → (Opsional) ID user admin yang jika mengirim pesan akan menghentikan bot
- `monitor_channel.txt` → (Opsional) ID channel yang dipantau dari pesan admin

📄 Contoh isi `.env`:

```

# Token Discord
TOKEN_1=MTExOTM0NzA1NDYxNDg1MjQz.NjL-lp.xxxxxxxxxxxxxxxxxxxxxxxxxxx
TOKEN_2=OTk4MzI3NzM2MjQ5MTExNjY1.OzR5aP.xxxxxxxxxxxxxxxxxxxxxxxxxxx

# API Key Gemini (WAJIB jika menggunakan Mode 3)
GEMINI_API_KEY=AIzaSyBxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# API Key OpenAI (OPSIONAL, jika digunakan)
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx


````

> 🔒 Jika menggunakan mode AI Chat (nomor 3), pastikan `GEMINI_API_KEY` diisi. Untuk OpenAI, gunakan API key `sk-...` jika ingin kustomisasi lebih lanjut.

---

## 💻 Instalasi

### 1. **Termux (Android)**

```bash
pkg update && pkg upgrade -y
pkg install git python openssl -y
pip install aiohttp python-dotenv

git clone https://github.com/lukmanc405/push-dc.git
cd push-dc

python main.py
````

### 2. **VSCode / PC**

```bash
git clone https://github.com/lukmanc405/push-dc.git
cd push-dc

pip install aiohttp python-dotenv

python main.py
```

> 💡 Rekomendasi: Aktifkan virtual environment

```bash
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
.\.venv\Scripts\activate   # Windows
```

---

## ▶️ Cara Jalankan Bot

```bash
python main.py
```

Ikuti instruksi di terminal:

1. Masukkan **delay minimal & maksimal**
2. Pilih mode untuk masing-masing akun:

   * `1` = Kirim biasa
   * `2` = Kirim lalu hapus otomatis
   * `3` = AI Chat (Gemini)
   * `4` = Emoticon random
3. Bot berjalan otomatis, menampilkan status futuristik per akun

---

## 📋 Fitur Utama

* 🔄 Multi-account otomatis (deteksi dari `.env`)
* 🧠 AI Chat dengan Gemini / OpenAI (mode 3)
* 💬 Emoticon random dari list (mode 4)
* 🧹 Auto-delete pesan (mode 2)
* 📤 Kirim pesan ke banyak channel
* 📁 Log otomatis per channel (opsional)
* ⛔ Monitor pesan admin (akan auto shutdown)
* 🔐 Validasi `.env` dan API key sebelum jalan
* 🌌 Tampilan terminal futuristik dan full-color
* ⏱ Ringkasan jumlah pesan per akun saat berhenti

---

## 📦 Contoh Output Terminal

```
┏━ AKUN #2 | ⏱ 21:23:49 | 📤 LOUNGE
┣━ PESAN : !GM
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

```
┌────────────────────────────────────────────┐
│             🔻 BOT TELAH DIMATIKAN        │
├────────────────────────────────────────────┤
│ DURASI : 1 MENIT 42 DETIK
│ AKUN #1 TELAH MENGIRIM : 12 PESAN
│ AKUN #2 TELAH MENGIRIM : 11 PESAN
└────────────────────────────────────────────┘
```

---

## 🤝 Lisensi

MIT License © 2025

Bebas digunakan, dimodifikasi, dan didistribusikan. Gunakan dengan bijak, segala risiko ditanggung pengguna.
