import streamlit as st
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import json

def save_dates(start_date, end_date):
    with open("config.json", "w") as f:
        json.dump({"start_date": str(start_date), "end_date": str(end_date)}, f)

def load_dates():
    try:
        with open("config.json", "r") as f:
            data = json.load(f)
            return data.get("start_date"), data.get("end_date")
    except FileNotFoundError:
        return None, None

def calculate_progress(start_date, end_date, current_date=None):
    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")

    if current_date:
        current = datetime.strptime(current_date, "%Y-%m-%d")
    else:
        current = datetime.today()

    total_days = (end - start).days
    elapsed_days = (current - start).days

    elapsed_days = max(0, min(elapsed_days, total_days))
    progress = (elapsed_days / total_days) * 100 if total_days > 0 else 100

    return round(progress, 2), end - current

st.set_page_config(page_title="Progress Tracker", page_icon="📊", layout="wide")

st.title("📊 Progress Tracker")

saved_start, saved_end = load_dates()

with st.sidebar:
    st.header("📅 Ange datum")
    start_date = st.date_input("Välj startdatum", value=datetime.strptime(saved_start, "%Y-%m-%d") if saved_start else datetime.today())
    end_date = st.date_input("Välj slutdatum", value=datetime.strptime(saved_end, "%Y-%m-%d") if saved_end else datetime.today())
    save_dates(start_date, end_date)

if start_date and end_date:
    progress, time_left = calculate_progress(str(start_date), str(end_date))

    col1, col2 = st.columns([1, 2])

    with col1:
        st.metric(label="🔹 Framsteg", value=f"{progress}%")
        st.progress(progress / 100)

        days, seconds = time_left.days, time_left.seconds
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        seconds = seconds % 60

        def format_time(value, singular, plural):
            return f"{value} {singular if value == 1 else plural}"

        st.write("⏳ **Tid kvar till slutdatumet:**")
        timer_placeholder = st.empty()

        if days >= 0:
            timer_placeholder.write(
                f"{format_time(days, 'dag', 'dagar')}, "
                f"{format_time(hours, 'timma', 'timmar')}, "
                f"{format_time(minutes, 'minut', 'minuter')}, "
                f"{format_time(seconds, 'sekund', 'sekunder')} kvar"
            )
        else:
            timer_placeholder.write("✅ **Tiden har gått ut!**")

    with col2:
        st.write("📊 **Framstegsgraf**")
        fig, ax = plt.subplots(figsize=(3, 3))
        labels = ["Klar", "Kvar"]
        sizes = [progress, 100 - progress]
        colors = ["#4CAF50", "#FF5733"]
        ax.pie(sizes, labels=labels, autopct="%1.1f%%", colors=colors, startangle=90)
        ax.axis("equal")

        try:
            st.pyplot(fig, clear_figure=True)
        except Exception as e:
            st.error(f"Fel vid generering av grafen: {e}")
