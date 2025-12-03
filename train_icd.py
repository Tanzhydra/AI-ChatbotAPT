import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import Pipeline
import joblib

# --- PENGATURAN ---
FILE_DATA = 'data_latih_icd10.csv'
FILE_MODEL = 'model_icd10.joblib'
# --------------------

print(f"Melatih AI dari {FILE_DATA}...")
try:
    data = pd.read_csv(FILE_DATA).dropna(subset=['Gejala_Lengkap'])
except FileNotFoundError:
    print("Error: File data latih tidak ditemukan. Jalankan augment_icd.py dulu.")
    exit()

X = data['Gejala_Lengkap']
y = data['Kode_ICD10'] 

print("Membangun pipeline AI (Random Forest)...")
pipeline = Pipeline([
    ('vectorizer', TfidfVectorizer(ngram_range=(1, 2))),
    ('model', RandomForestClassifier(n_estimators=100, random_state=42))
])

print("Sedang melatih model...")
pipeline.fit(X, y)

joblib.dump(pipeline, FILE_MODEL)
print(f"Selesai! Model Cerdas tersimpan di {FILE_MODEL}")