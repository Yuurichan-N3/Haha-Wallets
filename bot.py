from aiohttp import ClientResponseError, ClientSession, ClientTimeout
from aiohttp_socks import ProxyConnector
from fake_useragent import FakeUserAgent
from datetime import datetime
from colorama import Fore, Style, init
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm
import asyncio
import json
import os
import pytz
import threading

init(autoreset=True)
wib = pytz.timezone('Asia/Jakarta')

class HahaWallet:
    def __init__(self) -> None:
        self.headers = {
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
            "Content-Type": "application/json",
            "Origin": "chrome-extension://andhndehpcjpmneneealacgnmealilal",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "none",
            "User-Agent": FakeUserAgent().random,
            "X-Request-Source-Extra": "chrome"
        }
        self.proxies = []
        self.proxy_index = 0
        self.account_proxies = {}
        self.lock = threading.Lock()
        self.pbar = None

    def print_question(self):
        while True:
            try:
                print(f"\n{Fore.CYAN}Select proxy option:{Style.RESET_ALL}")
                print("1. Jalankan dengan proxy sharing")
                print("2. Jalankan dengan Proxy Pribadi")
                print("3. Jalankan tanpa Proxy")
                choose = int(input(f"{Fore.YELLOW}Choose [1/2/3] -> {Style.RESET_ALL}").strip())

                if choose in [1, 2, 3]:
                    proxy_type = (
                        "Run With Free Shared Proxy" if choose == 1 else 
                        "Run With Private Proxy" if choose == 2 else 
                        "Run Without Proxy"
                    )
                    print(f"{Fore.GREEN}{Style.BRIGHT}{proxy_type} Selected.{Style.RESET_ALL}")
                    return choose
                else:
                    print(f"{Fore.RED}{Style.BRIGHT}Please enter either 1, 2 or 3.{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED}{Style.BRIGHT}Invalid input. Enter a number (1, 2 or 3).{Style.RESET_ALL}")

    def clear_terminal(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def log(self, message, account=None):
        with self.lock:
            timestamp = datetime.now().astimezone(wib).strftime('%x %X %Z')
            account_info = f"[{account}] " if account else ""
            print(
                f"{Fore.CYAN}{Style.BRIGHT}[{timestamp}]{Style.RESET_ALL} "
                f"{Fore.WHITE}{Style.BRIGHT}|{Style.RESET_ALL} "
                f"{account_info}{message}",
                flush=True
            )

    def welcome(self):
        print(f"""
{Fore.YELLOW}{Style.BRIGHT}
╔══════════════════════════════════════════════╗
║     HahaWallet Multi-Account Auto Claimer    ║
║    Telegram Group: t.me/sentineldiscus       ║
╚══════════════════════════════════════════════╝
{Style.RESET_ALL}""")

    def load_accounts(self):
        filename = "accounts.txt"
        try:
            if not os.path.exists(filename):
                self.log(f"{Fore.RED}File {filename} not found.{Style.RESET_ALL}")
                return []

            with open(filename, 'r') as file:
                accounts = []
                for line in file:
                    parts = line.strip().split("|")
                    if len(parts) == 2:
                        email, password = parts
                        accounts.append({"Email": email.strip(), "Password": password.strip()})
                return accounts
        except Exception as e:
            self.log(f"{Fore.RED}Error loading accounts: {e}{Style.RESET_ALL}")
            return []

    async def load_proxies(self, use_proxy_choice: int):
        filename = "proxy.txt"
        try:
            if use_proxy_choice == 1:
                async with ClientSession(timeout=ClientTimeout(total=30)) as session:
                    async with session.get("https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/all.txt") as response:
                        response.raise_for_status()
                        content = await response.text()
                        self.proxies = content.splitlines()
                        with open(filename, 'w') as f:
                            f.write(content)
            else:
                if not os.path.exists(filename):
                    self.log(f"{Fore.RED}{Style.BRIGHT}File {filename} not found.{Style.RESET_ALL}")
                    return
                with open(filename, 'r') as f:
                    self.proxies = f.read().splitlines()

            if not self.proxies:
                self.log(f"{Fore.RED}{Style.BRIGHT}No proxies found.{Style.RESET_ALL}")
                return

            self.log(f"{Fore.GREEN}{Style.BRIGHT}Total Proxies: {len(self.proxies)}{Style.RESET_ALL}")

        except Exception as e:
            self.log(f"{Fore.RED}{Style.BRIGHT}Failed to load proxies: {e}{Style.RESET_ALL}")
            self.proxies = []

    def check_proxy_schemes(self, proxy):
        schemes = ["http://", "https://", "socks4://", "socks5://"]
        if any(proxy.startswith(scheme) for scheme in schemes):
            return proxy
        return f"http://{proxy}"

    def get_next_proxy_for_account(self, account):
        with self.lock:
            if account not in self.account_proxies:
                if not self.proxies:
                    return None
                proxy = self.check_proxy_schemes(self.proxies[self.proxy_index])
                self.account_proxies[account] = proxy
                self.proxy_index = (self.proxy_index + 1) % len(self.proxies)
            return self.account_proxies[account]

    def rotate_proxy_for_account(self, account):
        with self.lock:
            if not self.proxies:
                return None
            proxy = self.check_proxy_schemes(self.proxies[self.proxy_index])
            self.account_proxies[account] = proxy
            self.proxy_index = (self.proxy_index + 1) % len(self.proxies)
            return proxy

    async def user_login(self, email: str, password: str, proxy=None):
        url = "https://prod.haha.me/users/login"
        data = json.dumps({"email": email, "password": password})
        headers = {
            **self.headers,
            "Content-Length": str(len(data))
        }
        connector = ProxyConnector.from_url(proxy) if proxy else None
        try:
            async with ClientSession(connector=connector, timeout=ClientTimeout(total=60)) as session:
                async with session.post(url=url, headers=headers, data=data) as response:
                    response.raise_for_status()
                    result = await response.json()
                    return result['id_token']
        except Exception as e:
            self.log(f"{Fore.RED}Login failed: {str(e)}{Style.RESET_ALL}", email)
            return None

    async def user_balance(self, token: str, proxy=None):
        url = "https://prod.haha.me/wallet-api/graphql"
        data = json.dumps({
            "operationName": None,
            "variables": {},
            "query": "{\n  getKarmaPoints\n}"
        })
        headers = {
            **self.headers,
            "Authorization": token,
            "Content-Length": str(len(data))
        }
        connector = ProxyConnector.from_url(proxy) if proxy else None
        try:
            async with ClientSession(connector=connector, timeout=ClientTimeout(total=60)) as session:
                async with session.post(url=url, headers=headers, data=data) as response:
                    response.raise_for_status()
                    result = await response.json()
                    return result['data']
        except Exception:
            return None

    async def daily_checkin(self, token: str, proxy=None):
        url = "https://prod.haha.me/wallet-api/graphql"
        data = json.dumps({
            "operationName": None,
            "variables": {"timezone": "Asia/Jakarta"},
            "query": "query ($timezone: String) {\n  getDailyCheckIn(timezone: $timezone)\n}"
        })
        headers = {
            **self.headers,
            "Authorization": token,
            "Content-Length": str(len(data))
        }
        connector = ProxyConnector.from_url(proxy) if proxy else None
        try:
            async with ClientSession(connector=connector, timeout=ClientTimeout(total=60)) as session:
                async with session.post(url=url, headers=headers, data=data) as response:
                    response.raise_for_status()
                    result = await response.json()
                    return result['data']
        except Exception:
            return None

    async def claim_checkin(self, token: str, proxy=None):
        url = "https://prod.haha.me/wallet-api/graphql"
        data = json.dumps({
            "operationName": None,
            "variables": {"timezone": "Asia/Jakarta"},
            "query": "mutation ($timezone: String) {\n  setDailyCheckIn(timezone: $timezone)\n}"
        })
        headers = {
            **self.headers,
            "Authorization": token,
            "Content-Length": str(len(data))
        }
        connector = ProxyConnector.from_url(proxy) if proxy else None
        try:
            async with ClientSession(connector=connector, timeout=ClientTimeout(total=60)) as session:
                async with session.post(url=url, headers=headers, data=data) as response:
                    response.raise_for_status()
                    result = await response.json()
                    return result['data']['setDailyCheckIn']
        except Exception:
            return None

    async def get_id_token(self, email: str, password: str, use_proxy: bool):
        proxy = self.get_next_proxy_for_account(email) if use_proxy else None

        token = None
        retries = 3
        for _ in range(retries):
            token = await self.user_login(email, password, proxy)
            if token:
                self.log(f"{Fore.GREEN}Login successful{Style.RESET_ALL}", email)
                return token
            proxy = self.rotate_proxy_for_account(email) if use_proxy else None
        
        return None

    async def process_single_account(self, account, use_proxy):
        email = account["Email"]
        password = account["Password"]
        
        try:
            token = await self.get_id_token(email, password, use_proxy)
            if not token:
                return False

            proxy = self.get_next_proxy_for_account(email) if use_proxy else None
            
            # Get balance
            user = await self.user_balance(token, proxy)
            if user:
                balance = user["getKarmaPoints"]
                self.log(f"Balance: {balance} Karma", email)

            # Daily check-in
            check_in = await self.daily_checkin(token, proxy)
            if not check_in:
                self.log(f"{Fore.RED}Check-in failed{Style.RESET_ALL}", email)
                return False

            if check_in['getDailyCheckIn']:
                claim = await self.claim_checkin(token, proxy)
                if claim:
                    user = await self.user_balance(token, proxy)
                    new_balance = user["getKarmaPoints"] if user else "N/A"
                    self.log(f"Check-in claimed - New balance: {new_balance} Karma", email)
                else:
                    self.log(f"{Fore.RED}Failed to claim check-in{Style.RESET_ALL}", email)

            return True

        except Exception as e:
            self.log(f"{Fore.RED}Error processing account: {str(e)}{Style.RESET_ALL}", email)
            return False
        finally:
            if self.pbar:
                self.pbar.update(1)

    async def process_accounts_batch(self, accounts, use_proxy, max_workers=5):
        total_accounts = len(accounts)
        self.pbar = tqdm(total=total_accounts, desc="Processing accounts", unit="account")

        async def process_batch(batch):
            tasks = [self.process_single_account(account, use_proxy) for account in batch]
            return await asyncio.gather(*tasks)

        batch_size = max_workers
        results = []
        
        for i in range(0, total_accounts, batch_size):
            batch = accounts[i:i + batch_size]
            batch_results = await process_batch(batch)
            results.extend(batch_results)

        self.pbar.close()
        
        successful = sum(1 for r in results if r)
        self.log(f"\n{Fore.GREEN}Successfully processed {successful}/{total_accounts} accounts{Style.RESET_ALL}")

    async def main(self):
        self.clear_terminal()
        self.welcome()

        accounts = self.load_accounts()
        if not accounts:
            self.log(f"{Fore.RED}No accounts loaded. Exiting...{Style.RESET_ALL}")
            return

        self.log(f"Loaded {len(accounts)} accounts")

        use_proxy_choice = self.print_question()
        use_proxy = use_proxy_choice in [1, 2]

        if use_proxy:
            await self.load_proxies(use_proxy_choice)
            if not self.proxies and use_proxy:
                self.log(f"{Fore.RED}No proxies available. Exiting...{Style.RESET_ALL}")
                return

        await self.process_accounts_batch(accounts, use_proxy)

if __name__ == "__main__":
    wallet = HahaWallet()
    asyncio.run(wallet.main())
