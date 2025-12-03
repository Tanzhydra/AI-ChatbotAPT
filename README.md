AI Diagnosa Penyakit (ICD-10) via Telegram Bot

Project ini adalah implementasi Kecerdasan Buatan (AI) sederhana untuk membantu diagnosa awal penyakit berdasarkan gejala yang diinputkan pengguna melalui Telegram.

Fitur Utama

Standar ICD-10: Menggunakan kode dan nama penyakit sesuai standar WHO.

Machine Learning: Menggunakan algoritma Random Forest dan TF-IDF Vectorizer untuk klasifikasi teks.

Bot Cerdas (Interaktif): Bot dapat bertanya balik (konfirmasi gejala) jika tingkat keyakinan (confidence) prediksi rendah.

Rekomendasi Medis: Memberikan saran awal dan obat OTC (Over The Counter) yang relevan.

Struktur File

app_telegram_icd.py: Script utama bot Telegram.

train_icd.py: Script untuk melatih model AI.

augment_icd.py: Script untuk memperbanyak data latih (Data Augmentation).

data_icd10.csv: Database penyakit, gejala, dan rekomendasi.

Cara Menjalankan (Lokal/Server)

Install dependencies:

pip install -r requirements.txt


Generate data latih:

python augment_icd.py


Latih model AI:

python train_icd.py


Jalankan bot (Pastikan Token Telegram sudah diisi di script):

python app_telegram_icd.py


Disclaimer

Sistem ini hanya alat bantu diagnosa awal dan bukan pengganti konsultasi medis profesional.