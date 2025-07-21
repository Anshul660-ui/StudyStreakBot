from telegram import Update
from telegram.ext import Application, ApplicationBuilder, CommandHandler, ContextTypes
import json, os
from datetime import datetime

from keep_alive import keep_alive

DATA_FILE = "data.json"

def load_data():
    if os.path.exists(DATA_FILE):
        return json.load(open(DATA_FILE))
    return {}

def save_data(data):
    json.dump(data, open(DATA_FILE, "w"))

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f"Start command received from user {update.message.from_user.id}")
    welcome_msg = """Welcome to StudyStreakBot! 🎯

I am created by Anshul ✨

Use these commands to manage your study tasks:
• /addtask <task> - Add a new study task
• /tasks - View today's tasks
• /done <number> - Mark a task as complete (+10 points)
• /score - Check your points
• /terminate - Reset your points and tasks

Start building your study streak! 📚"""
    await update.message.reply_text(welcome_msg)

async def addtask(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)
    task = " ".join(context.args)
    if not task:
        await update.message.reply_text("Usage: /addtask <task>")
        return

    data = load_data()
    today = datetime.now().strftime("%Y-%m-%d")
    user_data = data.get(user_id, {"tasks": {}, "points": 0})
    tasks_today = user_data["tasks"].get(today, [])
    tasks_today.append({"task": task, "done": False})
    user_data["tasks"][today] = tasks_today
    data[user_id] = user_data
    save_data(data)

    await update.message.reply_text(f"Task '{task}' added!")

async def tasks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)
    data = load_data()
    today = datetime.now().strftime("%Y-%m-%d")
    user_data = data.get(user_id, {"tasks": {}, "points": 0})
    tasks_today = user_data["tasks"].get(today, [])

    if not tasks_today:
        await update.message.reply_text("No tasks added for today.")
        return

    msg = "Today's tasks:\n"
    for i, task in enumerate(tasks_today, start=1):
        status = "✅" if task["done"] else "❌"
        msg += f"{i}. {task['task']} {status}\n"
    await update.message.reply_text(msg)

async def done(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)
    data = load_data()
    today = datetime.now().strftime("%Y-%m-%d")
    user_data = data.get(user_id, {"tasks": {}, "points": 0})
    tasks_today = user_data["tasks"].get(today, [])

    if not context.args or not context.args[0].isdigit():
        await update.message.reply_text("Usage: /done <task_number>")
        return

    task_num = int(context.args[0]) - 1
    if task_num < 0 or task_num >= len(tasks_today):
        await update.message.reply_text("Invalid task number.")
        return

    tasks_today[task_num]["done"] = True
    user_data["tasks"][today] = tasks_today
    user_data["points"] += 10  # Award 10 points for completing a task
    data[user_id] = user_data
    save_data(data)

    await update.message.reply_text(f"Task '{tasks_today[task_num]['task']}' marked as done! +10 points")

async def score(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)
    username = update.message.from_user.first_name or update.message.from_user.username or "User"
    data = load_data()
    user_data = data.get(user_id, {"tasks": {}, "points": 0})
    points = user_data["points"]

    await update.message.reply_text(f"🏆 {username}, your current score: {points} points")

async def terminate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)
    data = load_data()

    # Check if the user exists in the data
    if user_id in data:
        # Remove the user's data
        del data[user_id]
        save_data(data)
        await update.message.reply_text("Your points have been reset, and all tasks have been deleted. You can start fresh!")
    else:
        await update.message.reply_text("No data found for you. You can start adding tasks!")

def main():
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    if not BOT_TOKEN:
        print("Error: BOT_TOKEN environment variable not set!")
        return

    try:
        app = ApplicationBuilder().token(BOT_TOKEN).build()

        app.add_handler(CommandHandler("start", start))
        app.add_handler(CommandHandler("addtask", addtask))
        app.add_handler(CommandHandler("tasks", tasks))
        app.add_handler(CommandHandler("done", done))
        app.add_handler(CommandHandler("score", score))
        app.add_handler(CommandHandler("terminate", terminate))  # Register the /terminate command

        print("Bot is running and listening for messages...")
        print("Try sending /start to your bot on Telegram")
        app.run_polling()

    except Exception as e:
        print(f"Error starting bot: {e}")

if __name__ == "__main__":
    keep_alive()
    main()