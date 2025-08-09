# app.py
from datetime import datetime, date
from zoneinfo import ZoneInfo
from babel.dates import format_date
import streamlit as st

# =========================
# Core data (anchor only)
# =========================
ANCHOR_CARDS = {
    1: "The Magician",
    2: "The High Priestess",
    3: "The Empress",
    4: "The Emperor",
    5: "The Hierophant",
    6: "The Lovers",
    7: "The Chariot",
    8: "Strength",
    9: "The Hermit",
}

# Nuansa overlay (10..22) — DIPAKAI DI BELAKANG LAYAR SAJA
OVERLAY_NUANCE = {
    10: "perputaran momentum dan timing yang pas",
    11: "penyelarasan yang jujur dan keputusan seimbang",
    12: "jeda sadar untuk melihat dari sudut pandang baru",
    13: "transformasi tuntas—menutup yang usang agar yang sehat tumbuh",
    14: "meracik porsi yang pas; moderasi dan harmonisasi",
    15: "kesadaran batas & negosiasi atas dorongan yang mengikat",
    16: "koreksi mendadak yang menyadarkan inti masalah",
    17: "harapan jangka panjang dan pemulihan yang tenang",
    18: "kabut yang minta kejernihan—validasi rasa dan fakta",
    19: "kejelasan, vitalitas, dan afirmasi pada hal yang hidup",
    20: "panggilan batin & evaluasi besar untuk naik kelas",
    21: "penyelesaian siklus dan integrasi yang utuh",
    22: "awal segar yang menuntut keberanian ringan dan keluwesan",
}

# Ringkasan makna anchor untuk narasi
ANCHOR_CORE = {
    1: "memulai dan mewujudkan hal yang kamu niatkan dengan fokus",
    2: "menenangkan diri agar intuisi terdengar jernih sebelum bertindak",
    3: "menumbuhkan ide dan relasi dengan kehangatan yang kreatif",
    4: "menegaskan struktur, batas sehat, dan arah kepemimpinan",
    5: "berpegang pada nilai yang bijak sambil berbagi pengetahuan",
    6: "membuat pilihan yang selaras antara hati dan akal",
    7: "menjaga kendali arah dan konsisten menuju tujuan",
    8: "menguat lewat ketenangan, kesabaran, dan pengendalian diri",
    9: "merenungi makna agar keputusan lahir dari kejernihan",
}

ANCHOR_STRENGTHS = {
    1: ["inisiatif tinggi", "resourceful", "cepat eksekusi saat tujuan jelas"],
    2: ["intuisi tajam", "pendengar yang baik", "membaca tanda-tanda halus"],
    3: ["hangat dan suportif", "ide subur", "membuat suasana hidup"],
    4: ["tegas terarah", "disiplin", "pandai membangun sistem"],
    5: ["berpegang nilai", "suka belajar–mengajar", "jadi rujukan orang"],
    6: ["harmonis", "empatik", "adil menimbang pilihan"],
    7: ["fokus", "tahan gangguan", "dorongan maju konsisten"],
    8: ["tenang namun kuat", "berani berkata 'cukup'", "stamina batin baik"],
    9: ["reflektif", "jernih menyaring informasi", "bijak berjarak"],
}
ANCHOR_CHALLENGES = {
    1: ["mulai banyak hal tapi kurang menutup loop", "mudah terdistraksi ide baru"],
    2: ["terlalu berhati-hati hingga pasif", "ragu saat sinyalnya samar"],
    3: ["mencari validasi luar", "energi tercecer ke banyak arah"],
    4: ["kaku pada aturan", "defensif terhadap perubahan"],
    5: ["terlalu textbook", "enggan mengubah pakem yang tak relevan"],
    6: ["menunda keputusan agar semua senang", "menghindari konflik penting"],
    7: ["terlalu ngotot pada rute sendiri", "sulit melihat opsi alternatif"],
    8: ["memendam sampai meledak", "terlalu keras pada diri sendiri"],
    9: ["kelamaan di mode analisis", "terkesan menjauh dari orang"],
}

# =========================
# Math helpers (BACKSTAGE)
# =========================
def digit_sum_once(n: int) -> int:
    return sum(int(d) for d in str(abs(int(n))))

def reduce_with_overlay(total: int):
    """
    Return (anchor_single, overlay_phrase_or_None)
    - Overlay terdeteksi dari penjumlahan digit PERTAMA (10..22).
    - Aturan khusus 22 -> anchor 4 (BUKAN 0).
    """
    first = digit_sum_once(total)
    overlay = OVERLAY_NUANCE.get(first) if 10 <= first <= 22 else None
    # Anchor final (1..9)
    if first == 22:
        anchor = 4
    else:
        anchor = first
        while anchor > 9:
            anchor = digit_sum_once(anchor)
    return anchor, overlay

def effective_year_for_running(dob: date, today: date) -> int:
    dob_this_year = date(today.year, dob.month, dob.day)
    return today.year if today >= dob_this_year else today.year - 1

# =========================
# Computations (BACKSTAGE)
# =========================
def compute_tp(dob: date):
    total = dob.day + dob.month + dob.year
    anchor, overlay = reduce_with_overlay(total)
    return anchor, overlay, ANCHOR_CARDS[anchor]

def compute_life_value(dob: date, tp_anchor: int):
    total = dob.year + tp_anchor
    anchor, overlay = reduce_with_overlay(total)
    return anchor, overlay, ANCHOR_CARDS[anchor]

def compute_running_year(dob: date, tp_anchor: int, today: date):
    yr = effective_year_for_running(dob, today)
    total = yr + tp_anchor
    anchor, overlay = reduce_with_overlay(total)
    return yr, anchor, overlay, ANCHOR_CARDS[anchor]

# =========================
# Narrative builders
# =========================
def join_list(items):
    if not items: return ""
    if len(items) == 1: return items[0]
    return ", ".join(items[:-1]) + ", dan " + items[-1]

DISCLAIMER = (
    "Disclaimer: Tarot numerology bukan ramalan masa depan. Ini peta simbolik untuk membantu "
    "refleksi arah, pola, potensi, dan tantangan. Kamu tetap memegang kemudi keputusanmu."
)

def make_character_para(anchor: int, card: str):
    core = ANCHOR_CORE[anchor]
    plus = join_list(ANCHOR_STRENGTHS[anchor][:3])
    minus = join_list(ANCHOR_CHALLENGES[anchor][:2])
    return (
        f"Karakter — *{card}*. Energi dasarnya mengajakmu untuk {core}. "
        f"Kamu cenderung {plus}. Waspadai kecenderungan {minus}."
    )

def make_lv_para(anchor: int, card: str, overlay: str | None):
    core = ANCHOR_CORE[anchor]
    base = f"Life Value — *{card}*. Nilai hidupmu menguat ketika kamu {core}."
    # Sisipkan overlay sebagai frasa umum TANPA menyebut kartu/angka/istilah
    if overlay:
        base += f" Ada kalanya fase penting ditandai oleh {overlay}."
    return base

def make_potency_para(tp_anchor: int, lv_anchor: int):
    tpc = ANCHOR_CARDS[tp_anchor]; lvc = ANCHOR_CARDS[lv_anchor]
    return (
        f"Potensi ke depan. Perpaduan {tpc} dan {lvc} membuatmu selaras saat memadukan "
        f"niat yang jernih dengan langkah yang disiplin. Pilih arena yang butuh kepekaan arah "
        f"dan eksekusi rapi agar daya dorongmu terasa."
    )

def make_year_para(year_label: int, anchor: int, card: str, overlay: str | None):
    core = ANCHOR_CORE[anchor]
    line = (
        f"Tantangan di tahun {year_label}. Fasenya condong ke *{card}*: "
        f"fokus untuk {core} sepanjang tahun ini."
    )
    if overlay:
        line += f" Jaga keluwesan ritme—akan ada momen {overlay} yang mengajakmu menyelaraskan prioritas."
    return line

# =========================
# UI (Streamlit)
# =========================
st.set_page_config(page_title="LiaOS Tarot Numerology", page_icon="🔮", layout="centered")

st.title("LiaOS Tarot Numerology")
st.caption("Semua perhitungan di belakang layar. Hasil disajikan sebagai narasi ringkas.")

name = st.text_input("Nama (opsional)", "")
dob_in = st.text_input("Tanggal lahir (DD/MM/YYYY)", "")

if st.button("Baca Profil"):
    try:
        tz = ZoneInfo("Asia/Jakarta")
        today = datetime.now(tz).date()

        dob = datetime.strptime(dob_in.strip(), "%d/%m/%Y").date()
        dob_human = format_date(dob, format="d MMMM yyyy", locale="id_ID")

        # Hitung (BACKSTAGE)
        tp_anchor, tp_overlay, tp_card = compute_tp(dob)
        lv_anchor, lv_overlay, lv_card = compute_life_value(dob, tp_anchor)
        eff_year, ty_anchor, ty_overlay, ty_card = compute_running_year(dob, tp_anchor, today)

        # Narasi (NO BRIDGE MENTION)
        header = f"{name.strip() or '—'}\n{dob_human}"
        para_character = make_character_para(tp_anchor, tp_card)
        para_lv = make_lv_para(lv_anchor, lv_card, lv_overlay)
        para_potency = make_potency_para(tp_anchor, lv_anchor)
        para_year = make_year_para(eff_year, ty_anchor, ty_card, ty_overlay)

        st.markdown(f"**{header}**")
        st.write(para_character)
        st.write(para_lv)
        st.write(para_potency)
        st.write(para_year)
        st.markdown(f"—\n{DISCLAIMER}")

    except Exception as e:
        st.error(f"Input tidak valid. Pastikan format tanggal: DD/MM/YYYY. Detail: {e}")
def make_paragraph_life_value(anchor: int, name_card: str, overlay_text: str | None):
    core = ANCHOR_CORE[anchor]
    base = f"Life Value — *{name_card}*. Nilai hidupmu menguat ketika kamu {core}."
    if overlay_text:
        base += f" Tahun-tahun penting sering ditandai oleh {overlay_text}."
    return base

def make_paragraph_potency(tp_anchor: int, lv_anchor: int):
    # Ringkas: padukan karakter + LV jadi arah kekuatan
    tp_word = ANCHOR_CARDS[tp_anchor]
    lv_word = ANCHOR_CARDS[lv_anchor]
    return (
        f"Potensi ke depan. Perpaduan {tp_word} dan {lv_word} membuatmu selaras saat "
        f"memadukan niat yang jernih dengan langkah yang disiplin. Pilih arena yang "
        f"membutuhkan dua hal itu: kepekaan arah dan eksekusi yang rapi."
    )

def make_paragraph_year(year_label: int, anchor: int, name_card: str, overlay_text: str | None):
    core = ANCHOR_CORE[anchor]
    line = (
        f"Tantangan di tahun {year_label}. Fasenya condong ke *{name_card}*: "
        f"fokus untuk {core} sepanjang tahun ini."
    )
    if overlay_text:
        line += f" Di baliknya, ada nuansa {overlay_text}, jadi gunakan momen ini untuk menyelaraskan ritme dan prioritas."
    return line

DISCLAIMER = (
    "Disclaimer: Tarot numerology bukan ramalan masa depan. Ini peta simbolik untuk membantu "
    "refleksi arah, pola, potensi, dan tantangan. Kamu tetap memegang kemudi keputusanmu."
)

def build_full_profile(name: str, dob_str: str, today: date | None = None) -> str:
    """
    Format final:
    Nama & DOB
    Karakter (narasi)
    Life Value (narasi)
    Potensi ke depan (narasi)
    Tantangan Tahun Berjalan (narasi)
    Disclaimer
    """
    if today is None:
        today = date.today()
    dob = datetime.strptime(dob_str, "%d/%m/%Y").date()

    # Hitungan belakang layar
    tp_anchor, tp_overlay, tp_card = compute_tp(dob)
    lv_anchor, lv_overlay, lv_card = compute_life_value(dob, tp_anchor)
    eff_year, ty_anchor, ty_overlay, ty_card = compute_running_year(dob, tp_anchor, today)

    # Narasi
    header = f"{name}\n{dob.strftime('%d %B %Y')}"
    para_character = make_paragraph_character(tp_anchor, tp_card)
    para_lv = make_paragraph_life_value(lv_anchor, lv_card, lv_overlay)
    para_potency = make_paragraph_potency(tp_anchor, lv_anchor)
    para_year = make_paragraph_year(eff_year, ty_anchor, ty_card, ty_overlay)

    return (
        f"{header}\n\n"
        f"{para_character}\n\n"
        f"{para_lv}\n\n"
        f"{para_potency}\n\n"
        f"{para_year}\n\n"
        f"{DISCLAIMER}"
    )

# =========================
# Contoh penggunaan
# =========================
if __name__ == "__main__":
    # Contoh test: ganti sesuai kebutuhanmu
    print(build_full_profile("Bapak Andalas", "21/06/1961"))
