# MULTI_ACCOUNT_BOT.PY - FINAL FIX MONITOR ADMIN TIMESTAMP
import aiohttp
import asyncio
import os
import sys
import time
import random
from datetime import datetime
from itertools import cycle
from dotenv import dotenv_values

# WARNA ANSI
RED = "\033[91m"; GREEN = "\033[92m"; YELLOW = "\033[93m"
CYAN = "\033[96m"; MAGENTA = "\033[95m"; RESET = "\033[0m"; BOLD = "\033[1m"

ACCOUNT_COLORS = cycle([RED, GREEN, YELLOW, CYAN, MAGENTA])
os.system("cls" if os.name == "nt" else "clear")

# LOAD ENV
config = dotenv_values(".env")
GEMINI_KEY = config.get("GEMINI_API_KEY")
OPENAI_KEY = config.get("OPENAI_API_KEY")

# === FUNGSI ===
def read_lines(file): return [l.strip() for l in open(file) if l.strip()] if os.path.exists(file) else []
def print_header():
    print(f"{BOLD}{CYAN}┌────────────────────────────────────────────┐")
    print(f"│       🤖  MULTI ACCOUNT DISCORD BOT       │")
    print(f"└────────────────────────────────────────────┘{RESET}")

def loading_line(msg):
    for c in msg: sys.stdout.write(c); sys.stdout.flush(); time.sleep(0.02)
    print()

def validate_env(ai_chat):
    errors=[]; tokens=[k for k in config if k.startswith("TOKEN_")]
    if not tokens: errors.append("❌ Tidak ada TOKEN_ ditemukan.")
    for k in tokens:
        if not config[k].strip() or len(config[k].strip()) < 20:
            errors.append(f"❌ {k} terlalu pendek atau kosong.")
    if ai_chat:
        if not GEMINI_KEY: errors.append("❌ GEMINI_API_KEY belum diisi untuk mode AI.")
        if OPENAI_KEY and not OPENAI_KEY.startswith("sk-"):
            errors.append("⚠️ OPENAI_API_KEY tampak tidak valid.")
    if errors:
        print(f"{RED}\n[!] ERROR DI FILE .env:{RESET}")
        for e in errors: print(f"{RED}- {e}{RESET}")
        exit()

# === DATA ===
TOKENS = [v for k,v in config.items() if k.startswith("TOKEN_") and v]
CHANNELS = [l.split(",") for l in read_lines("channel.txt") if "," in l]
PESAN_POOL = read_lines("pesan.txt")
EMOTES = read_lines("emote.txt")
ADMINS = [int(x) for x in read_lines("admin.txt") if x.isdigit()]
MONITOR = [x for x in read_lines("monitor_channel.txt") if x.isdigit()]

# === INPUT ===
def input_int(msg):
    while True:
        try:
            v=input(msg).strip()
            if not v.isdigit(): raise ValueError("HARUS ANGKA.")
            return int(v)
        except Exception as e: print(f"{RED}[X] {e}{RESET}")

loading_line(f"{CYAN}▶ MASUKKAN DELAY PENGIRIMAN...{RESET}")
min_delay = input_int("DELAY MINIMAL (DETIK): ")
max_delay = input_int("DELAY MAKSIMAL (DETIK): ")
account_delay = 1

def input_mode(msg):
    while True:
        v=input(msg).strip()
        if v in ("1","2","3","4"): return v
        print(f"{RED}[!] PILIH 1-4{RESET}")

MODES={}; COUNTER={}; pakai_ai=False
for idx,t in enumerate(TOKENS,1):
    c=next(ACCOUNT_COLORS)
    print(f"{c}\n╔═ KONFIGURASI AKUN #{idx}")
    print(f"║ 1. KIRIM BIASA\n║ 2. HAPUS (SUPER CEPAT)\n║ 3. AI CHAT GEMINI\n║ 4. EMOTICON RANDOM{RESET}")
    m=input_mode(f"{c}╚═▶ PILIH MODE (1-4): {RESET}")
    if m=="3": pakai_ai=True
    MODES[t]=(m,c)
    COUNTER[t]=0

validate_env(pakai_ai)
start_time = time.time()

# === FUNGSI ASYNC ===
async def chat_gemini(prompt):
    async with aiohttp.ClientSession() as s:
        async with s.post(
            "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent",
            headers={"Content-Type":"application/json","x-goog-api-key":GEMINI_KEY},
            json={"contents":[{"parts":[{"text":prompt}]}]}
        ) as r:
            d=await r.json()
            return d.get("candidates",[{}])[0].get("content",{}).get("parts",[{}])[0].get("text","(KOSONG)")

async def hapus_pesan(session, token, cid, mid, color, aid):
    h={"Authorization":token,"Content-Type":"application/json"}
    async with session.delete(f"https://discord.com/api/v9/channels/{cid}/messages/{mid}",headers=h) as r:
        now=datetime.now().strftime("%H:%M:%S")
        if r.status==204:
            print(f"{YELLOW}┏━ AKUN #{aid} | ⏱ {now} | 🗑 PESAN DIHAPUS\n┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{RESET}")
        else:
            print(f"{RED}[AKUN #{aid}] GAGAL HAPUS: {r.status}{RESET}")

async def kirim_pesan(session, token, cname, cid, konten, color, aid):
    h={"Authorization":token,"Content-Type":"application/json"}
    async with session.post(
        f"https://discord.com/api/v9/channels/{cid}/messages",
        json={"content":konten},headers=h
    ) as r:
        now=datetime.now().strftime("%H:%M:%S")
        if r.status in (200,201):
            data=await r.json(); mid=data.get("id")
            COUNTER[token]+=1
            atas=f"AKUN #{aid} | ⏱ {now} | 📤 {cname.upper()}"
            pesan=f"PESAN : {konten[:60].upper()}"
            lebar=max(len(atas),len(pesan))+4
            garis="━"*lebar
            print(f"{color}┏━ {atas}\n┣━ {pesan}\n┗{garis}{RESET}")
            return mid
        elif r.status==429:
            retry=(await r.json()).get("retry_after",5)
            print(f"{YELLOW}[AKUN #{aid}] RATE LIMIT {retry} DETIK{RESET}")
            await asyncio.sleep(retry)
        else:
            print(f"{RED}[AKUN #{aid}] GAGAL {r.status} | {await r.text()}{RESET}")
    return None

async def monitor_admin(session, token, color):
    h={"Authorization":token,"Content-Type":"application/json"}
    last_message_ids = {}

    # Inisialisasi
    for cid in MONITOR:
        async with session.get(f"https://discord.com/api/v9/channels/{cid}/messages?limit=1", headers=h) as r:
            if r.status==200:
                m=await r.json()
                if m: last_message_ids[cid] = m[0].get("id")

    while True:
        for cid in MONITOR:
            async with session.get(f"https://discord.com/api/v9/channels/{cid}/messages?limit=1", headers=h) as r:
                if r.status==200:
                    m=await r.json()
                    if m:
                        msg=m[0]
                        msg_id=msg.get("id")
                        author_id=msg.get("author",{}).get("id")
                        msg_time=msg.get("timestamp")
                        msg_dt=datetime.fromisoformat(msg_time.replace('Z', '+00:00')).timestamp() if msg_time else 0

                        if (last_message_ids.get(cid) != msg_id and 
                            int(author_id) in ADMINS and 
                            msg_dt > start_time):
                            tstr=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            print(f"{color}[✘] BOT MATI KRN ADMIN KIRIM MSG BARU PADA {tstr}{RESET}")
                            await tampilkan_ringkasan()
                            os._exit(0)
                        last_message_ids[cid] = msg_id
        await asyncio.sleep(5)

async def akun_worker(token, mode, color, aid):
    async with aiohttp.ClientSession() as s:
        q = PESAN_POOL.copy(); random.shuffle(q)
        if MONITOR: asyncio.create_task(monitor_admin(s, token, color))
        while True:
            if not q: q = PESAN_POOL.copy(); random.shuffle(q)
            konten = await chat_gemini("Buat pesan pendek ramah.") if mode=="3" else random.choice(EMOTES) if mode=="4" else q.pop(0)
            for name, cid in CHANNELS:
                mid=await kirim_pesan(s,token,name,cid,konten,color,aid)
                if mode=="2" and mid:
                    await asyncio.sleep(0.1)
                    await hapus_pesan(s,token,cid,mid,color,aid)
            await asyncio.sleep(random.randint(min_delay,max_delay))

async def tampilkan_ringkasan():
    e=int(time.time()-start_time)
    print(f"\n{BOLD}{CYAN}┌────────────────────────────────────────────┐")
    print(f"│             🔻 BOT TELAH DIMATIKAN          │")
    print(f"├────────────────────────────────────────────┤")
    print(f"│ DURASI : {e//60} MENIT {e%60} DETIK")
    for i,t in enumerate(COUNTER,1):
        print(f"│ AKUN #{i} TELAH MENGIRIM : {COUNTER[t]} PESAN")
    print(f"└────────────────────────────────────────────┘{RESET}\n")

async def main():
    print_header()
    for i,(t,(m,c)) in enumerate(MODES.items()):
        asyncio.create_task(akun_worker(t,m,c,i+1))
        await asyncio.sleep(account_delay)
    while True: await asyncio.sleep(3600)

if __name__=="__main__":
    try: asyncio.run(main())
    except KeyboardInterrupt: asyncio.run(tampilkan_ringkasan())
