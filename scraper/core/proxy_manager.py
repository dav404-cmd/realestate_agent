import asyncio
import os
import httpx
from dotenv import load_dotenv

load_dotenv()


class ProxyManager:
    def __init__(self):
        self.server = os.getenv("PROXY_SERVER")
        self.username = os.getenv("PROXY_USER")
        self.password = os.getenv("PROXY_PASSWORD")

    async def verify_proxy(self):

        proxy_url = f"http://{self.username}:{self.password}@{self.server.replace('http://', '')}"

        proxies = {
            "http://": proxy_url,
            "https://": proxy_url
        }

        try:
            async with httpx.AsyncClient(proxies=proxies, timeout=10.0) as client:
                response = await client.get("https://httpbin.org/ip")

                if response.status_code == 200:
                    print(f"Proxy verified successfully! Current IP: {response.json().get('origin')}")

                    return {
                        "server": self.server,
                        "username": self.username,
                        "password": self.password
                    }
        except Exception as e:
            print(f"Proxy verification failed: {e}")

        return None

if __name__ == "__main__":
    proxy = ProxyManager()
    ans = proxy.verify_proxy()
    asyncio.run(ans)