## 🚀 push-dc Bot

Sebuah bot **Discord** asynchronous untuk mengirim pesan otomatis dengan opsi delete dan log di Termux maupun VSCode.

---

### 🔧 Prerequisites

* Termux (Android) atau VSCode (Windows/Linux/macOS)
* Python ≥ 3.7
* Akses internet

---

### ⚙️ Setup di Termux

1. **Update & Install**

   ```bash
   pkg update && pkg upgrade -y
   pkg install git python openssl -y
   ```
2. **Clone Repo**

   ```bash
   git clone https://github.com/lukmanc405/push-dc.git
   cd push-dc
   ```
3. **Install Dependencies**

   ```bash
   pip install requests colorama aiohttp
   ```

---

### ⚙️ Setup di VSCode

1. **Clone Repo**

   ```bash
   git clone https://github.com/lukmanc405/push-dc.git
   cd push-dc
   code .
   ```
2. **Virtualenv (opsional)**

   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Linux/macOS
   .\.venv\Scripts\activate  # Windows
   ```
3. **Install Dependencies**

   ```bash
   pip install requests colorama aiohttp
   ```

---

### 🔑 Konfigurasi

1. **Token Discord**: simpan di `token.txt` (baris pertama).
2. **Pesan**: tambahkan kata/kalimat di `pesan.txt` (per baris).
3. **Channel**: format `nama,channel_id` di `channel.txt`.

---

### ▶️ Menjalankan Bot

```bash
python main.py
```

1. Pilih **AUTO DELETE**? (Y/N)
2. Jika Y: masukkan **delete delay (detik)**
3. Masukkan **kirim delay (detik)**
4. Pilih **VERBOSE MODE**? (Y/N)
5. Masukkan **rotasi pesan (detik)**

---

### 📋 Fitur Utama

* ✅ Kirim pesan secara Async ke banyak channel
* 🗑️ Auto-delete pesan setelah delay
* 📄 Logging ke `log.txt`
* 🐌 Penanganan rate-limit (429)
* 🔄 Rotasi pesan otomatis

---

### 🤝 Lisensi

MIT License © 2025
