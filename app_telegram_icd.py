import joblib
import pandas as pd
import logging
import random
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# --- TOKEN ANDA (Pastikan diganti sebelum dijalankan/diupload) ---
TELEGRAM_BOT_TOKEN = "PASTE_TOKEN_ANDA_DISINI" 

# --- PENGATURAN LOGIKA ---
THRESHOLD_SURE = 0.65  
THRESHOLD_LOW = 0.20   

# --- MEMORI BOT ---
USER_SESSIONS = {}

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

print("Memuat sistem...")
try:
    pipeline = joblib.load('model_icd10.joblib')
    db_penyakit = pd.read_csv('data_icd10.csv')
    db_penyakit.set_index('Kode_ICD10', inplace=True)
    print("Sistem Siap.")
except Exception as e:
    print(f"Error Init: {e}")
    # exit() # Commented out for GitHub upload purpose (file model mungkin belum ada di repo)

def get_suggested_symptoms(user_text, full_symptoms_str):
    user_text = user_text.lower()
    db_symptoms = [s.strip() for s in full_symptoms_str.split(',')]
    
    missing_symptoms = []
    for sym in db_symptoms:
        keyword = sym.split()[0].lower() 
        if keyword not in user_text:
            missing_symptoms.append(sym)
    
    if len(missing_symptoms) > 3:
        return random.sample(missing_symptoms, 3)
    return missing_symptoms

def get_diagnosis(gejala, user_id):
    try:
        vectorizer = pipeline.named_steps['vectorizer']
        if vectorizer.transform([gejala]).nnz == 0:
            return "🤔 Maaf, saya tidak mengenali gejala tersebut. Mohon gunakan bahasa medis umum.", None

        probs = pipeline.predict_proba([gejala])[0]
        max_prob = probs.max()
        pred_idx = probs.argmax()
        kode_icd = pipeline.classes_[pred_idx]
        
        info = db_penyakit.loc[kode_icd]
        if isinstance(info, pd.DataFrame): info = info.iloc[0]

        link_who = f"https://icd.who.int/browse10/2019/en#/{kode_icd}"

        if max_prob < THRESHOLD_LOW:
            return (
                f"⚠️ *Analisa Tidak Pasti ({int(max_prob*100)}%)*\n"
                f"Gejala terlalu umum. Kemungkinan kecil: *{info['Nama_Umum']}*.\n"
                f"Mohon sebutkan gejala lain dengan lebih lengkap."
            ), None

        elif max_prob < THRESHOLD_SURE:
            saran_gejala_list = get_suggested_symptoms(gejala, info['Gejala_Lengkap'])
            if not saran_gejala_list:
                 return (
                    f"📋 *HASIL DIAGNOSA (Estimasi)*\n"
                    f"🏥 *Kode ICD-10:* [`{kode_icd}`]({link_who})\n"
                    f"📊 *Kecocokan:* {int(max_prob * 100)}%\n\n"
                    f"🧬 *Medis:* _{info['Penyakit']}_\n"
                    f"🤒 *Umum:* {info['Nama_Umum']}\n\n"
                    f"💡 *Rekomendasi:* {info['Rekomendasi_Awal']}\n"
                    f"💊 *Obat OTC:* {info['Obat_Umum']}\n"
                    f"━━━━━━━━━━━━━━━━━━\n"
                    f"_Disclaimer: Hasil ini berdasarkan pendekatan ICD-10 WHO._"
                ), None

            saran_display = ", ".join([f"_{s}_" for s in saran_gejala_list])
            saran_raw = " ".join(saran_gejala_list)
            
            balasan = (
                f"🧐 *Analisa Lanjutan Diperlukan*\n"
                f"Berdasarkan keluhan Anda, ini mengarah ke suspek: *{info['Nama_Umum']}* (Kecocokan: {int(max_prob*100)}%).\n\n"
                f"Untuk memastikan, apakah Anda juga merasakan gejala ini?\n"
                f"👉 {saran_display}\n\n"
                f"Ketik *'Ya'* jika benar, atau tulis gejala lain jika ada."
            )
            return balasan, saran_raw

        else:
            return (
                f"📋 *HASIL DIAGNOSA AWAL*\n"
                f"━━━━━━━━━━━━━━━━━━\n"
                f"🏥 *Kode ICD-10:* [`{kode_icd}`]({link_who})\n"
                f"📊 *Kecocokan:* {int(max_prob * 100)}%\n\n"
                f"🧬 *Medis:* _{info['Penyakit']}_\n"
                f"🤒 *Umum:* {info['Nama_Umum']}\n\n"
                f"💡 *Rekomendasi:* {info['Rekomendasi_Awal']}\n"
                f"💊 *Obat OTC:* {info['Obat_Umum']}\n"
                f"━━━━━━━━━━━━━━━━━━\n"
                f"_Disclaimer: Hasil ini berdasarkan pendekatan ICD-10 WHO. Tetap konsultasikan dengan dokter._"
            ), None

    except Exception as e:
        logging.error(f"Error prediksi: {e}")
        return "Terjadi kesalahan sistem.", None

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.effective_user.full_name
    await update.message.reply_text(
        f"Halo {user_name}! 👋\n\n"
        "Saya adalah Bot AI Diagnosa ICD-10.\n"
        "Silakan ketik gejala yang Anda rasakan (contoh: 'demam dan batuk')."
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_text = update.message.text.strip()
    
    if user_text.lower() == 'ya' and user_id in USER_SESSIONS:
        session = USER_SESSIONS.pop(user_id)
        gejala_gabungan = f"{session['gejala_awal']} {session['gejala_saran']}"
        logging.info(f"User {user_id} konfirmasi YA. Input baru: {gejala_gabungan}")
        balasan, saran_baru = get_diagnosis(gejala_gabungan, user_id)
        
        if saran_baru:
             USER_SESSIONS[user_id] = {'gejala_awal': gejala_gabungan, 'gejala_saran': saran_baru}
        
        await update.message.reply_text(balasan, parse_mode='Markdown', disable_web_page_preview=True)
        return

    if user_id in USER_SESSIONS:
        session = USER_SESSIONS[user_id]
        user_text = f"{session['gejala_awal']} {user_text}"
        logging.info(f"User {user_id} menambah gejala. Input gabungan: {user_text}")
    
    if user_id in USER_SESSIONS:
        del USER_SESSIONS[user_id]

    balasan, saran = get_diagnosis(user_text, user_id)
    
    if saran:
        USER_SESSIONS[user_id] = {
            'gejala_awal': user_text,
            'gejala_saran': saran
        }
    
    await update.message.reply_text(balasan, parse_mode='Markdown', disable_web_page_preview=True)

if __name__ == '__main__':
    if TELEGRAM_BOT_TOKEN == "PASTE_TOKEN_ANDA_DISINI":
        print("ERROR: Harap masukkan Token Bot Anda di file app_telegram_icd.py")
    else:
        app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
        app.add_handler(CommandHandler("start", start))
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
        print("Bot Interaktif Berjalan...")
        app.run_polling()