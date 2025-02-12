import telebot
import os
import json
from telebot import types
from dotenv import load_dotenv

load_dotenv()

API_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

if not API_TOKEN:
    raise ValueError("API_TOKEN не найден! Убедитесь, что переменная окружения TELEGRAM_BOT_TOKEN установлена в .env файле.")

bot = telebot.TeleBot(API_TOKEN)

TASKS_FILE = 'tasks.json'

def load_tasks():
    try:
        with open(TASKS_FILE, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return []

def save_tasks(tasks):
    with open(TASKS_FILE, 'w') as file:
        json.dump(tasks, file)


@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Привет! Я бот для управления задачами. Используйте команду /add для добавления задачи и /list для просмотра списка.")


@bot.message_handler(commands=['add'])
def add_task(message):
    bot.reply_to(message, "Напишите задачу, которую нужно добавить.")

    
    bot.register_next_step_handler(message, save_new_task)

def save_new_task(message):
    task_text = message.text
    tasks = load_tasks()

    task_id = len(tasks) + 1
    tasks.append({'id': task_id, 'task': task_text, 'done': False})
    save_tasks(tasks)

    bot.reply_to(message, f"Задача '{task_text}' добавлена!")

@bot.message_handler(commands=['list'])
def list_tasks(message):
    tasks = load_tasks()
    
    if not tasks:
        bot.reply_to(message, "У вас нет задач.")
    else:
        task_list = "\n".join([f"{task['id']}. {task['task']} - {'Выполнено' if task['done'] else 'Не выполнено'}" for task in tasks])
        bot.reply_to(message, f"Ваши задачи:\n{task_list}")


@bot.message_handler(commands=['delete'])
def delete_task(message):
    bot.reply_to(message, "Введите ID задачи, которую хотите удалить.")
    
    
    bot.register_next_step_handler(message, remove_task)

def remove_task(message):
    try:
        task_id = int(message.text)
        tasks = load_tasks()
        
        
        task = next((task for task in tasks if task['id'] == task_id), None)
        
        if task:
            tasks.remove(task)
            save_tasks(tasks)
            bot.reply_to(message, f"Задача с ID {task_id} удалена.")
        else:
            bot.reply_to(message, f"Задача с ID {task_id} не найдена.")
    
    except ValueError:
        bot.reply_to(message, "Пожалуйста, введите правильный ID задачи.")


@bot.message_handler(func=lambda message: True)
def echo_all(message):
    bot.reply_to(message, "Я не понял вашу команду. Используйте /start для начала.")

if __name__ == '__main__':
    bot.polling(none_stop=True)
