import pandas as pd
import random

# --- PENGATURAN ---
FILE_INPUT = 'data_icd10.csv'
FILE_OUTPUT = 'data_latih_icd10.csv'
JUMLAH_TARGET_DATA = 700
# --------------------

def augment_gejala(gejala_str):
    if not isinstance(gejala_str, str): return ""
    gejala_list = [g.strip() for g in gejala_str.split(',')]
    random.shuffle(gejala_list)
    if len(gejala_list) > 2 and random.random() < 0.3:
        gejala_list.pop(random.randrange(len(gejala_list)))
    return ", ".join(gejala_list)

print(f"Memuat data asli dari {FILE_INPUT}...")
try:
    data = pd.read_csv(FILE_INPUT)
except FileNotFoundError:
    print("Error: File CSV tidak ditemukan. Pastikan data_icd10.csv ada.")
    exit()

print("Memproses augmentasi...")
data_baru_list = []
baris_asli_count = len(data)

while len(data_baru_list) < JUMLAH_TARGET_DATA:
    idx = len(data_baru_list)
    row_asli = data.iloc[idx % baris_asli_count]
    row_baru = row_asli.copy()
    row_baru['Gejala_Lengkap'] = augment_gejala(row_asli['Gejala_Lengkap'])
    data_baru_list.append(row_baru)

data_baru_df = pd.DataFrame(data_baru_list)
data_baru_df.to_csv(FILE_OUTPUT, index=False, encoding='utf-8')

print(f"Sukses! {len(data_baru_df)} data latih tersimpan di {FILE_OUTPUT}")