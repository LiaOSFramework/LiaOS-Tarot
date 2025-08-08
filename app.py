
import streamlit as st
import pandas as pd
from datetime import datetime, date
import calendar

st.set_page_config(page_title="Numerology Tarot App", page_icon="🔮", layout="wide")

# ---------- Helpers ----------
TAROT = {
    0: "The Fool",
    1: "The Magician",
    2: "The High Priestess",
    3: "The Empress",
    4: "The Emperor",
    5: "The Hierophant",
    6: "The Lovers",
    7: "The Chariot",
    8: "Strength",
    9: "The Hermit",
    10: "Wheel of Fortune",
    11: "Justice",
    12: "The Hanged Man",
    13: "Death",
    14: "Temperance",
    15: "The Devil",
    16: "The Tower",
    17: "The Star",
    18: "The Moon",
    19: "The Sun",
    20: "Judgement",
    21: "The World",
    22: "The Fool (Master Cycle)",
}

PYTHAGOREAN = {ch: val for ch, val in zip(
    list("ABCDEFGHIJKLMNOPQRSTUVWXYZ"),
    [1,2,3,4,5,6,7,8,9,1,2,3,4,5,6,7,8,9,1,2,3,4,5,6,7,8]
)}

def parse_date(text):
    if isinstance(text, date):
        return text
    # try dd/mm/yyyy or d/m/yyyy
    try:
        return datetime.strptime(str(text), "%d/%m/%Y").date()
    except:
        try:
            return datetime.strptime(str(text), "%Y-%m-%d").date()
        except:
            return None

def digit_sum_once(n: int) -> int:
    return sum(int(d) for d in str(abs(int(n))))

def reduce_single(n: int) -> int:
    s = digit_sum_once(n)
    if s < 10:
        return s
    return digit_sum_once(s)

def bridge_of(n: int):
    s = digit_sum_once(n)
    return s if (10 <= s <= 22) else ""

def tarot_name(num: int) -> str:
    return TAROT.get(num, "N/A")

def name_value(name: str) -> int:
    if not name:
        return 0
    total = 0
    for ch in name.upper():
        total += PYTHAGOREAN.get(ch, 0)
    return total

# ---------- Sidebar Inputs ----------
st.title("🔮 Numerology Tarot – Auto Yearly & Calendar")
name = st.text_input("Nama", value="")
dob_text = st.text_input("Tanggal Lahir (dd/mm/yyyy)", value="19/07/1977")
calendar_year = st.number_input("Tahun Kalender (untuk Calendar)", min_value=1900, max_value=2100, value=2025, step=1)
calendar_month = st.number_input("Bulan (1-12)", min_value=1, max_value=12, value=8, step=1)

dob = parse_date(dob_text)

if not dob:
    st.error("Format tanggal tidak dikenali. Gunakan dd/mm/yyyy, misal 19/07/1977.")
    st.stop()

# ---------- Core Numbers ----------
raw_sum = dob.day + dob.month + dob.year
char_digit_sum = digit_sum_once(raw_sum)
char_single = reduce_single(raw_sum)
char_bridge = bridge_of(raw_sum)

life_raw = dob.year + char_single
life_digit_sum = digit_sum_once(life_raw)
life_single = reduce_single(life_raw)
life_bridge = bridge_of(life_raw)

# Name numerology
name_total = name_value(name)
name_digit_sum = digit_sum_once(name_total) if name_total else 0
name_single = reduce_single(name_total) if name_total else 0
name_bridge = bridge_of(name_total) if name_total else ""

# Mapping
def to_tarot(num, bridge=""):
    return tarot_name(num), (tarot_name(int(bridge)) if str(bridge).strip() != "" else "")

char_tarot, char_bridge_tarot = to_tarot(char_single, char_bridge)
life_tarot, life_bridge_tarot = to_tarot(life_single, life_bridge)
name_tarot, name_bridge_tarot = to_tarot(name_single, name_bridge)

col1, col2, col3 = st.columns(3)
with col1:
    st.subheader("Karakter (DOB)")
    st.write({
        "RawSum": raw_sum, "DigitSum": char_digit_sum,
        "Single": char_single, "Bridge": char_bridge,
        "Tarot": char_tarot, "Bridge Tarot": char_bridge_tarot
    })
with col2:
    st.subheader("Life Value")
    st.write({
        "LifeRaw": life_raw, "DigitSum": life_digit_sum,
        "Single": life_single, "Bridge": life_bridge,
        "Tarot": life_tarot, "Bridge Tarot": life_bridge_tarot
    })
with col3:
    st.subheader("Nama")
    st.write({
        "Total": name_total, "DigitSum": name_digit_sum,
        "Single": name_single, "Bridge": name_bridge,
        "Tarot": name_tarot, "Bridge Tarot": name_bridge_tarot
    })

st.markdown("---")

# ---------- Yearly Grid ----------
st.header("Yearly Grid")
max_age = 88
years = [dob.year + a for a in range(max_age)]
year_digit_sums = [digit_sum_once(y) for y in years]
toy_unreduced = [char_single + s for s in year_digit_sums]
toy_single = [reduce_single(v) for v in toy_unreduced]
toy_bridge = [bridge_of(v) for v in toy_unreduced]

# Build dataframe with tarot rows 21..0 as index
rows = list(range(21, -1, -1))
df = pd.DataFrame(index=rows, columns=years)
for idx, y in enumerate(years):
    ts = toy_single[idx]
    tb = toy_bridge[idx]
    # mark ts as 'S' and tb as 'B' (for coloring); keep index number for readability
    df.at[ts, y] = "S"
    if str(tb) != "":
        df.at[int(tb), y] = "B"

df.index.name = "Tarot Num"
# Styler for colors (blue S, red B)
def color_fn(val):
    if val == "S":
        return "background-color: #7EB6FF"
    if val == "B":
        return "background-color: #FF6B6B"
    return ""

st.dataframe(df.style.applymap(color_fn), use_container_width=True)

# ---------- Calendar ----------
st.header("Calendar")
# ToY for selected calendar year
year_sum = digit_sum_once(calendar_year)
toy_selected = char_single + year_sum
toy_selected_single = reduce_single(toy_selected)

# Build month grid 6x7
cal = calendar.Calendar(firstweekday=0)  # Monday=0? (Python uses Monday as 0 by default in some contexts)
month_days = list(cal.itermonthdates(calendar_year, calendar_month))

# Make 6x7 grid mapping days of current month, else empty
grid = [["" for _ in range(7)] for _ in range(6)]
grid_card = [["" for _ in range(7)] for _ in range(6)]
r = c = 0
for d in month_days:
    if d.month != calendar_month and (r == 0 and d.day > 7):
        # skip leading previous month spill
        continue
    if d.month != calendar_month and d.day < 15 and r > 0:
        # trailing next month spill, allow display as empty
        continue
    # compute position
    weekday = d.weekday()  # Monday=0 .. Sunday=6
    if r == 0 and d.day == 1:
        c = weekday
    if d.month == calendar_month:
        grid[r][weekday] = d.day
        daily_unreduced = toy_selected + d.day
        daily_single = reduce_single(daily_unreduced)
        daily_bridge = bridge_of(daily_unreduced)
        grid_card[r][weekday] = f"{daily_single} ({TAROT.get(daily_single,'')})" + (f" | B:{daily_bridge}" if str(daily_bridge) != "" else "")
    if weekday == 6:
        r += 1

df_days = pd.DataFrame(grid, columns=list("Mon Tue Wed Thu Fri Sat Sun".split()))
df_cards = pd.DataFrame(grid_card, columns=list("Mon Tue Wed Thu Fri Sat Sun".split()))

st.subheader("Tanggal")
st.dataframe(df_days, use_container_width=True)
st.subheader("Kartu Harian")
st.dataframe(df_cards, use_container_width=True)
