import tkinter as tk
from tkinter import messagebox
import json
import os
import random
from datetime import date, datetime, timedelta

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

# --- Daily Quest Functions ---
def generate_daily_quest():
    exercises = list(conversion_rates.keys())
    quest_exercise = random.choice(exercises)
    if "Plank" in quest_exercise:
        amount = random.randint(30, 90)  # seconds
    else:
        amount = random.randint(5, 20)  # minutes
    reward = amount * conversion_rates[quest_exercise]
    progress["daily_quest"] = {
        "exercise": quest_exercise,
        "amount": amount,
        "reward": reward,
        "date": str(date.today()),
        "completed": False
    }
    save_progress()
    messagebox.showinfo("Daily Quest",
                        f"🎯 New Daily Quest:\nDo {amount} {quest_exercise} today for {reward:.1f} bonus XP!")

def check_daily_quest():
    quest = progress.get("daily_quest")
    today_str = str(date.today())
    # Generate new quest if none exists or new day
    if quest is None or quest["date"] != today_str:
        generate_daily_quest()
        quest = progress["daily_quest"]
    # Check completion
    exercise_done = entries[quest["exercise"]].get()
    try:
        amount_done = float(exercise_done)
    except ValueError:
        amount_done = 0
    if not quest["completed"] and amount_done >= quest["amount"]:
        progress["total_xp"] += quest["reward"]
        quest["completed"] = True
        save_progress()
        messagebox.showinfo("Quest Completed!",
                            f"✅ You completed today's quest!\nBonus {quest['reward']:.1f} XP awarded!")

# --- Main calculation function ---
def calculate():
    total_game_time = 0
    details = []
    for exercise, rate in conversion_rates.items():
        try:
            amount = float(entries[exercise].get())
        except ValueError:
            amount = 0
        earned = amount * rate
        if earned > 0:
            details.append(f"{exercise}: {earned:.1f} min")
        total_game_time += earned

    # XP = total_game_time
    earned_xp = total_game_time
    progress["total_xp"] += earned_xp

    # Level system: Level up every 500 XP
    new_level = progress["level"]
    while progress["total_xp"] >= new_level * 500:
        new_level += 1
    if new_level > progress["level"]:
        progress["level"] = new_level
        messagebox.showinfo("Level Up!", f"🎉 Congrats! You reached Level {new_level}!")

    # Badges
    badges_earned = []
    if total_game_time >= 100 and "100 Min Single Session" not in progress["badges"]:
        progress["badges"].append("100 Min Single Session")
        badges_earned.append("🏅 100 Min Single Session")
    if total_game_time >= 30 and "Quick Workout" not in progress["badges"]:
        progress["badges"].append("Quick Workout")
        badges_earned.append("🏅 Quick Workout")
    if badges_earned:
        messagebox.showinfo("New Badges!", "\n".join(badges_earned))

    # Streak tracking
    today_str = str(date.today())
    if progress["last_date"] != today_str:
        if progress["last_date"] is not None:
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

    # Check daily quest
    check_daily_quest()

    save_progress()

    result_label.config(text=f"🎮 Total Gaming Time: {total_game_time:.1f} min\n"
                             f"XP: {progress['total_xp']:.1f} | Level: {progress['level']} | Streak: {progress['streak']} days")
    if details:
        messagebox.showinfo("Details", "\n".join(details))

# --- GUI setup ---
root = tk.Tk()
root.title("Exercise → Gaming Calculator (Gamified)")

entries = {}
row = 0
for exercise in conversion_rates:
    tk.Label(root, text=exercise).grid(row=row, column=0, padx=10, pady=5, sticky="w")
    entry = tk.Entry(root)
    entry.insert(0, "0")
    entry.grid(row=row, column=1, padx=10, pady=5)
    entries[exercise] = entry
    row += 1

calc_button = tk.Button(root, text="Calculate", command=calculate)
calc_button.grid(row=row, column=0, columnspan=2, pady=10)

result_label = tk.Label(root, text=f"🎮 Total Gaming Time: 0 min | XP: {progress['total_xp']} | "
                                   f"Level: {progress['level']} | Streak: {progress['streak']} days",
                        font=("Arial", 12, "bold"))
result_label.grid(row=row+1, column=0, columnspan=2, pady=10)

root.mainloop()
