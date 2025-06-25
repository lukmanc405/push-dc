# 🚀 push-dc Bot

![Visitors](https://visitor-badge.laobi.icu/badge?page_id=lukmanc405.push-dc)
![GitHub Repo stars](https://img.shields.io/github/stars/lukmanc405/push-dc?style=social)
![GitHub All Releases](https://img.shields.io/github/downloads/lukmanc405/push-dc/total?label=Download)



Bot **Discord** asynchronous untuk mengirim pesan otomatis ke banyak channel dengan berbagai mode: teks biasa, auto delete, AI Chat GPT, dan emoticon custom. Dapat digunakan di **Termux (Android)** maupun **VSCode (PC)**.

---

## ⚙️ Persiapan

Siapkan file berikut di folder project:

- `.env` → Token Discord & API Key OpenAI
- `channel.txt` → daftar channel (format: `nama,channel_id`)
- `pesan.txt` → list pesan teks yang akan dikirim
- `emote.txt` → list emoticon custom Discord

**Contoh `.env`:**

TOKEN=isi_token_discord_anda
OPENAI_KEY=isi_api_key_openai_anda

---

## 💻 Instalasi

### **1. Termux (Android)**

```bash
pkg update && pkg upgrade -y
pkg install git python openssl -y
pip install aiohttp python-dotenv

git clone https://github.com/lukmanc405/push-dc.git
cd push-dc

python main.py
```
2. VSCode / PC
```bash
git clone https://github.com/lukmanc405/push-dc.git
cd push-dc

pip install aiohttp python-dotenv

python main.py
```
Jika ingin lebih rapi, aktifkan virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
.\.venv\Scripts\activate   # Windows
```
▶️ Cara Jalankan Bot
```bash
python main.py
```
Ikuti instruksi di terminal:

Pilih Mode:

1 = Kirim biasa (tidak dihapus)

2 = Kirim lalu hapus otomatis

3 = AI Chat (respon dari GPT-3.5)

4 = Kirim emoticon dari list

Atur delay minimal & maksimal antar pesan

Bot akan berjalan otomatis sesuai pengaturan

📋 Fitur Utama
- Kirim pesan otomatis ke banyak channel
-  Mode auto-delete pesan setelah delay
- AI Chat dengan OpenAI GPT-3.5
- Kirim emoticon custom dari list
- Log otomatis per channel di folder log/
- Penanganan rate-limit Discord (429)
- Rotasi pesan otomatis

🤝 Lisensi
MIT License © 2025

Bebas digunakan, dimodifikasi, dan didistribusikan. Gunakan dengan bijak, segala risiko ditanggung pengguna.