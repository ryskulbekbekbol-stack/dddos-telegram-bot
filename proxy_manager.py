#!/usr/bin/env python3
# 🌐 PROXY MANAGER

import random
import threading
import requests
from queue import Queue

class ProxyManager:
    def __init__(self):
        self.proxies = []
        self.working_proxies = []
        self.proxy_queue = Queue()
        self.proxy_sources = [
            "https://raw.githubusercontent.com/proxifly/free-proxy-list/main/proxies/all/data.txt",
            "https://raw.githubusercontent.com/clarketm/proxy-list/master/proxy-list-raw.txt",
            "https://api.proxyscrape.com/v2/?request=displayproxies&protocol=http&timeout=10000&country=all&ssl=all&anonymity=all",
        ]
    
    def fetch_proxies(self):
        all_proxies = []
        for url in self.proxy_sources:
            try:
                r = requests.get(url, timeout=5)
                if r.status_code == 200:
                    proxies = [line.strip() for line in r.text.split('\n') if line.strip()]
                    all_proxies.extend(proxies)
            except:
                pass
        self.proxies = list(set(all_proxies))
        return len(self.proxies)
    
    def check_proxy(self, proxy):
        try:
            host, port = proxy.split(':')
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            result = sock.connect_ex((host, int(port)))
            sock.close()
            return result == 0
        except:
            return False
    
    def get_working_proxies(self, limit=1000):
        self.working_proxies = []
        for proxy in self.proxies[:limit]:
            if self.check_proxy(proxy):
                self.working_proxies.append(proxy)
        return self.working_proxies
