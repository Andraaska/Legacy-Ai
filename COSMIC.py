#!/data/data/com.termux/files/usr/bin/python3
# -*- coding: utf-8 -*-
# COSMIC AI v18.0 - COMPETITION GRADE (FINAL)
# ============================================================
# SISTEM INI UNTUK LOMBA - TIDAK ADA API KEY TERLIHAT
# ============================================================
# Fitur:
# 1. API Key tersembunyi (environment variable / file eksternal)
# 2. Dual mode: Kompleks (detail) + Singkat (eksekutif)
# 3. Auto-rate limit handling
# 4. Tanpa hardcoded API key
# ============================================================

import json
import time
import requests
import os
import sys
import random
import hashlib
from datetime import datetime

# ================= KONFIGURASI (API KEY TERSEMBUNYI) =================
# API key dibaca dari environment variable (tidak terlihat di code)
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")

# Jika tidak ada environment variable, coba baca dari file tersembunyi
if not GROQ_API_KEY:
    key_paths = [
        "/data/data/com.termux/files/home/.groq_key",
        os.path.expanduser("~/.groq_key"),
        "/tmp/.key"
    ]
    for path in key_paths:
        if os.path.exists(path):
            try:
                with open(path, 'r') as f:
                    GROQ_API_KEY = f.read().strip()
                break
            except:
                pass

# Jika masih tidak ada, tampilkan error (tidak hardcode key di sini!)
if not GROQ_API_KEY:
    print("="*70)
    print("❌ ERROR: GROQ_API_KEY tidak ditemukan!")
    print("   Cara 1: export GROQ_API_KEY='gsk_xxx'")
    print("   Cara 2: echo 'gsk_xxx' > ~/.groq_key")
    print("="*70)
    sys.exit(1)

# ================= MODEL =================
AI_VISION = "llama-3.3-70b-versatile"        # AI 1: Kompleks (panjang, detail)
AI_REALIZER = "llama-3.1-8b-instant"         # AI 2: Singkat (ringkas)

# ================= PROMPT KOMPLEKS =================
PROMPT_COMPLEX = """Anda adalah AI VISION - pencari celah fisika tersembunyi.

TUGAS: Analisis pertanyaan secara MENDALAM dan KOMPLEKS.

FORMAT JAWABAN:
================================================================================
[CELAH FISIKA UTAMA]
- Nama fenomena:
- Penjelasan mekanisme (minimal 150 kata):
- Status: [TERBUKTI]/[TEORETIS]/[SPEKULATIF]

[POTENSI ENERGI]
Jelaskan sumber energi potensial (minimal 100 kata)

[BATASAN TEKNOLOGI SAAT INI]
Jelaskan hambatan yang masih ada (minimal 100 kata)

[KESIMPULAN]
Ringkasan potensi terbesar (minimal 50 kata)
================================================================================

PERTANYAAN: {question}

JAWAB DENGAN DETAIL DAN PANJANG!
"""

# ================= PROMPT SINGKAT =================
PROMPT_SHORT = """Anda adalah AI REALIZER - pemberi solusi ringkas.

TUGAS: Berdasarkan analisis kompleks di bawah, berikan JAWABAN SINGKAT.

ANALISIS KOMPLEKS:
{complex_answer}

PERTANYAAN AWAL: {question}

FORMAT JAWABAN:
[INTI JAWABAN]: (1-2 kalimat)
[CARA KERJA]: (1-2 kalimat)
[KESIMPULAN]: (1 kalimat)

JAWAB SANGAT SINGKAT! MAKSIMAL 3 PARAGRAF.
"""

# ================= API CALL =================
def call_ai(model, prompt, max_tokens=3000, temperature=0.7):
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": max_tokens,
        "temperature": temperature
    }
    
    for attempt in range(3):
        try:
            time.sleep(random.uniform(0.5, 1.0))
            response = requests.post(GROQ_URL, json=payload, headers=headers, timeout=90)
            if response.status_code == 200:
                return response.json()["choices"][0]["message"]["content"]
            elif response.status_code == 429:
                print(f"   ⚠️ Rate limit, retry {attempt+1}/3...")
                time.sleep(5)
            elif response.status_code == 401:
                print("   ❌ API Key tidak valid!")
                sys.exit(1)
        except Exception as e:
            print(f"   ⚠️ Error: {e}, retry {attempt+1}/3...")
            time.sleep(3)
    
    return "[ERROR] Gagal setelah 3 percobaan"

# ================= MAIN =================
def main():
    print("="*70)
    print("🌌 COSMIC AI v18.0 - COMPETITION GRADE")
    print("="*70)
    print("   Mode: Dual (Kompleks + Singkat)")
    print("   Output: 1 jawaban ringkas (eksekutif)")
    print("   Detail: tersedia jika diminta")
    print("="*70)
    
    # Counter
    count_file = "/data/data/com.termux/files/home/.cosmic_counter.txt"
    if os.path.exists(count_file):
        with open(count_file, 'r') as f:
            req_count = int(f.read().strip())
    else:
        req_count = 0
    
    while True:
        print("\n" + "-"*50)
        q = input("\n❓ Pertanyaan (exit untuk keluar): ").strip()
        
        if q.lower() == 'exit':
            break
        if not q:
            continue
        
        req_count += 1
        with open(count_file, 'w') as f:
            f.write(str(req_count))
        
        print("\n" + "="*70)
        print(f"🌟 MEMPROSES (Request #{req_count})")
        print("="*70)
        
        # ===== STEP 1: KOMPLEKS =====
        print("\n📖 Menganalisis secara detail...")
        start1 = time.time()
        complex_answer = call_ai(AI_VISION, PROMPT_COMPLEX.format(question=q), max_tokens=3500, temperature=0.7)
        elapsed1 = time.time() - start1
        print(f"   ✅ Selesai ({elapsed1:.1f}s)")
        
        # ===== STEP 2: SINGKAT =====
        print("\n📝 Merangkum jawaban...")
        start2 = time.time()
        short_answer = call_ai(AI_REALIZER, PROMPT_SHORT.format(complex_answer=complex_answer, question=q), max_tokens=800, temperature=0.3)
        elapsed2 = time.time() - start2
        print(f"   ✅ Selesai ({elapsed2:.1f}s)")
        
        # ===== OUTPUT =====
        total_time = elapsed1 + elapsed2
        
        print("\n" + "="*70)
        print(f"🌌 JAWABAN (Total: {total_time:.1f}s)")
        print("="*70)
        print(short_answer)
        print("\n" + "="*70)
        
        # Detail opsional
        show = input("\n📖 Lihat jawaban detail? (y/n): ").strip().lower()
        if show == 'y':
            print("\n" + "="*70)
            print("📖 JAWABAN DETAIL")
            print("="*70)
            print(complex_answer)
            print("="*70)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n🌌 Selesai.")
    except Exception as e:
        print(f"\n❌ Error: {e}")