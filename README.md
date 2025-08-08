
# Numerology Tarot App

## Cara Jalankan (lokal)
1. Pastikan Python 3.10+ terpasang.
2. Buat virtual env (opsional) lalu install:
   ```bash
   pip install -r requirements.txt
   ```
3. Jalankan:
   ```bash
   streamlit run app.py
   ```

## Aturan Perhitungan (default)
- TP (Tarot Personality) = single dari (hari + bulan + tahun lahir).
- ToY (Tarot of the Year) = TP + digit-sum tahun kalender.
- Daily = ToY(selected year) + nomor hari.
- Bridge aktif untuk 10–22 sebelum reduksi.

Warna:
- Biru = Single (S)
- Merah = Bridge (B)

Anda bisa mengubah aturan dengan mengedit fungsi di `app.py`.
