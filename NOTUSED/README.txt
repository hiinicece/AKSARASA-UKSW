════════════════════════════════════════════════════════════════════════════════
                    📁 FOLDER NOTUSED - File Tidak Terpakai
════════════════════════════════════════════════════════════════════════════════

File di folder ini TIDAK DIGUNAKAN atau SUDAH DIGANTI dengan solusi yang lebih baik.
Disimpan di sini sebagai backup/referensi.

════════════════════════════════════════════════════════════════════════════════
📋 DAFTAR FILE & ALASAN
════════════════════════════════════════════════════════════════════════════════

📂 scripts/ (Folder lama - sudah diganti)
   ├── setup_server.bat
   ├── start_server.bat
   └── start_server.ps1
   
   ❌ Alasan: Diganti dengan script yang lebih baik
   ✅ Gunakan: launch.bat (lebih interaktif & mudah)

---

📄 backend/coba.py
   ❌ Alasan: File testing/eksperimen, tidak digunakan di production
   ✅ Hapus: Atau simpan jika ada poin penting

---

📄 backend/chatbot_gui.log
   ❌ Alasan: Log file lama yang sudah tidak relevan
   ✅ Hapus: Log files dapat dihapus aman

---

📄 backend/.env.example
   ⚠️  Status: Tidak jelas apakah masih dipakai
   ✓ Saran: Opsional - bisa disimpan sebagai template

---

📄 backend/chatbot_config.json
   ⚠️  Status: Konfigurasi lama/tidak aktif
   ✓ Saran: Opsional - bisa disimpan sebagai referensi

---

📄 CHANGELOG.txt (di root)
   ⚠️  Status: File changelog/history
   ✓ Saran: Opsional - bisa disimpan untuk dokumentasi


════════════════════════════════════════════════════════════════════════════════
✅ FILE YANG HARUS TETAP (KEEP)
════════════════════════════════════════════════════════════════════════════════

🔴 PENTING - JANGAN HAPUS:

Backend:
  ✓ server.py (MAIN backend server)
  ✓ requirements.txt (dependencies)
  ✓ .env (API keys)

Frontend:
  ✓ index.html (main UI)
  ✓ script.js (logic)
  ✓ style.css (styling)

Static:
  ✓ static/audio/ (generated audio files)

Root:
  ✓ launch.bat (main launcher)


════════════════════════════════════════════════════════════════════════════════
🧹 PEMBERSIHAN YANG SUDAH DILAKUKAN
════════════════════════════════════════════════════════════════════════════════

Folder NOTUSED dibuat untuk menyimpan:

1. Folder scripts/ (setup_server.bat, start_server.bat, start_server.ps1)
   Alasan: Diganti dengan launch.bat yang lebih baik

2. backend/coba.py
   Alasan: File testing, tidak dipakai

3. backend/chatbot_gui.log
   Alasan: Log file lama

4. Dokumentasi publish (jika ingin bersih - optional)


════════════════════════════════════════════════════════════════════════════════
📊 STRUKTUR FOLDER BERSIH
════════════════════════════════════════════════════════════════════════════════

d:\BUDAYA GO\
├── 📂 backend/
│   ├── server.py ⭐
│   ├── requirements.txt ⭐
│   ├── .env ⭐
│   └── 📂 static/
│       └── audio/
│
├── 📂 frontend/
│   ├── index.html ⭐
│   ├── script.js ⭐
│   └── style.css ⭐
│
├── 📂 NOTUSED/ (File tidak digunakan disimpan di sini)
│   ├── 📂 scripts/
│   ├── coba.py
│   └── README.txt (file ini)
│
├── launch.bat ⭐ (Main launcher)
└── [Dokumentasi & setup files]


════════════════════════════════════════════════════════════════════════════════
🎯 NEXT STEPS
════════════════════════════════════════════════════════════════════════════════

Jika ingin lebih bersih lagi:

1. Hapus publish documentation jika tidak perlu (opsional):
   - ANSWER_PUBLISH.txt
   - START_PUBLISH.txt
   - PUBLISH_*.txt (semua file publish)
   
   Atau simpan di: NOTUSED/docs_publish/

2. Hapus log files jika sudah tidak perlu:
   - *.log files

3. Backup ke cloud/external drive:
   Sebelum menghapus anything, backup dulu!


════════════════════════════════════════════════════════════════════════════════
⚠️  PENTING - JANGAN LUPA
════════════════════════════════════════════════════════════════════════════════

✓ Backup project sebelum menghapus file apa pun
✓ .env file berisi API key - jangan di-share/upload ke GitHub
✓ static/audio/ folder otomatis generate - jangan dihapus
✓ requirements.txt sangat penting - jangan dihapus


════════════════════════════════════════════════════════════════════════════════
