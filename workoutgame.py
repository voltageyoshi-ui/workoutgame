import streamlit as st
import json
import os
import random
from datetime import date, datetime, timedelta

st.set_page_config(page_title="Workout → Game Time", layout="centered")
st.title("🎮 Gamified Workout Tracker")

# --- Conversion rates ---
conversion_rates = {
    "Pushups (min)": 10,
    "Sit-ups (min)": 5,
    "Squats (min)": 5,
    "Burpees (min)": 20,
    "Laps (walking/running/jogging)": 40,
    "Plank (seconds)": 1/3,  # 3 sec = 1 gaming minute
    "Lunges (min)": 20
}

# --- File to save progress ---
DATA_FILE = "game_progress.json"

# --- Load or initialize progress ---
if os.path.exists(DATA_FILE):
    with open(DATA_FILE, "r") as f:
        progress = json.load(f)
else:
    progress = {
        "total_xp": 0,
        "level": 1,
        "badges": [],
        "last_date": None,
        "streak": 0,
        "daily_quest": None
    }

def save_progress():
    with open(DATA_FILE, "w") as f:
        json.dump(progress, f)

# --- Daily Quest ---
def generate_daily_quest():
    exercises = list(conversion_rates.keys())
    quest_exercise = random.choice(exercises)
    if "Plank" in quest_exercise:
        amount = random.randint(30, 90)
    else:
        amount = random.randint(5, 20)
    reward = amount * conversion_rates[quest_exercise]
    progress["daily_quest"] = {
        "exercise": quest_exercise,
        "amount": amount,
        "reward": reward,
        "date": str(date.today()),
        "completed": False
    }
    save_progress()

def check_daily_quest(user_inputs):
    quest = progress.get("daily_quest")
    today_str = str(date.today())
    if quest is None or quest["date"] != today_str:
        generate_daily_quest()
        quest = progress["daily_quest"]
    # Check completion
    amount_done = float(user_inputs.get(quest["exercise"], 0))
    if not quest["completed"] and amount_done >= quest["amount"]:
        progress["total_xp"] += quest["reward"]
        quest["completed"] = True
        st.balloons()
        st.success(f"✅ Daily Quest Completed! Bonus {quest['reward']:.1f} XP awarded!")

# --- User Input ---
st.subheader("Enter your workout for today:")
user_inputs = {}
for exercise in conversion_rates:
    if "Plank" in exercise:
        user_inputs[exercise] = st.number_input(f"{exercise}", 0, 300, step=5)
    else:
        user_inputs[exercise] = st.number_input(f"{exercise}", 0, 60, step=1)

if st.button("Calculate Game Time & XP"):
    # Calculate total game time / XP
    total_game_time = 0
    for exercise, rate in conversion_rates.items():
        amount = float(user_inputs.get(exercise, 0))
        total_game_time += amount * rate

    earned_xp = total_game_time

    # --- Random loot ---
    loot_chance = random.random()
    loot_message = ""
    if loot_chance < 0.2:
        multiplier = random.choice([1.5, 2, 2.5])
        earned_xp *= multiplier
        loot_message = f"🍀 Lucky! XP multiplied by {multiplier}!"
    elif loot_chance < 0.35:
        bonus_xp = random.randint(10, 50)
        earned_xp += bonus_xp
        loot_message = f"🎁 Bonus! +{bonus_xp} XP!"

    if loot_message:
        st.success(loot_message)

    # Add XP
    progress["total_xp"] += earned_xp

    # --- Level up ---
    new_level = progress["level"]
    while progress["total_xp"] >= new_level * 500:
        new_level += 1
    if new_level > progress["level"]:
        progress["level"] = new_level
        st.balloons()
        st.success(f"🎉 Congrats! You reached Level {new_level}!")

    # --- Badges ---
    badges_earned = []
    if total_game_time >= 100 and "100 Min Single Session" not in progress["badges"]:
        progress["badges"].append("100 Min Single Session")
        badges_earned.append("🏅 100 Min Single Session")
    if total_game_time >= 30 and "Quick Workout" not in progress["badges"]:
        progress["badges"].append("Quick Workout")
        badges_earned.append("🏅 Quick Workout")
    if loot_message and "Lucky Workout" not in progress["badges"]:
        progress["badges"].append("Lucky Workout")
        badges_earned.append("✨ Lucky Workout Badge!")
    if badges_earned:
        st.success("New Badges!\n" + "\n".join(badges_earned))

    # --- Streak tracking ---
    today_str = str(date.today())
    if progress["last_date"] != today_str:
        if progress["last_date"]:
            try:
                last_date_obj = datetime.strptime(progress["last_date"], "%Y-%m-%d").date()
                if last_date_obj == date.today() - timedelta(days=1):
                    progress["streak"] += 1
                else:
                    progress["streak"] = 1
            except:
                progress["streak"] = 1
        else:
            progress["streak"] = 1
        progress["last_date"] = today_str

    # --- Check daily quest ---
    check_daily_quest(user_inputs)

    # Save progress
    save_progress()

    # --- Display summary ---
    st.subheader("Summary:")
    st.write(f"🎮 Total Gaming Time: {total_game_time:.1f} min")
    st.write(f"XP: {progress['total_xp']:.1f} | Level: {progress['level']} | Streak: {progress['streak']} days")
    if progress["badges"]:
        st.write("🏆 Badges: " + ", ".join(progress["badges"]))
