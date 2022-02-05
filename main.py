import asyncio
import tasksio
import logging
import discum
import random
import httpx
import os

from itertools import cycle
from random_user_agent.user_agent import UserAgent
from httpx_socks import AsyncProxyTransport

if os.name == "posix":
    os.system('clear')
else:
    os.system('cls')

logging.basicConfig(
    level=logging.INFO,
    format="\x1b[38;5;14m[\x1b[0m%(asctime)s\x1b[38;5;14m] \x1b[0m%(message)s",
    datefmt="%I:%M:%S",
)

class Discord(object):

    def __init__(self, proxies: dict = {}):
        self.proxies = proxies

        if self.proxies != None: self.transport = AsyncProxyTransport.from_url("%s://%s" % (proxies["type"], proxies["proxy"]))
        if self.proxies == None: self.transport = None
    
    async def get_headers(self, token: str):
        async with httpx.AsyncClient(transport=self.transport) as session:
            response = await session.get("https://discord.com/app")
            cookies = str(response.cookies)
            dcfduid = cookies.split("dcfduid=")[1].split(";")[0]
            sdcfduid = cookies.split("sdcfduid=")[1].split(";")[0]
            agent = UserAgent(limit=100).get_random_user_agent()
        
        return {
            "Authorization": token,
            "accept": "*/*",
            "accept-language": "en-US",
            "connection": "keep-alive",
            "cookie": "__dcfduid=%s; __sdcfduid=%s; locale=en-US" % (dcfduid, sdcfduid),
            "DNT": "1",
            "origin": "https://discord.com",
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "referer": "https://discord.com/channels/@me",
            "TE": "Trailers",
            "User-Agent": agent,
            "X-Super-Properties": "eyJvcyI6IldpbmRvd3MiLCJicm93c2VyIjoiRGlzY29yZCBDbGllbnQiLCJyZWxlYXNlX2NoYW5uZWwiOiJzdGFibGUiLCJjbGllbnRfdmVyc2lvbiI6IjEuMC45MDAxIiwib3NfdmVyc2lvbiI6IjEwLjAuMTkwNDIiLCJvc19hcmNoIjoieDY0Iiwic3lzdGVtX2xvY2FsZSI6ImVuLVVTIiwiY2xpZW50X2J1aWxkX251bWJlciI6ODMwNDAsImNsaWVudF9ldmVudF9zb3VyY2UiOm51bGx9"
        }
    
    async def send(self, token: str, channel_id: int, message: str):
        headers = await self.get_headers(token)
        txt = {"content": message}
        async with httpx.AsyncClient(transport=self.transport) as session:
            response = await session.post("https://discord.com/api/v9/channels/%s/messages" % (channel_id), headers=headers, json=txt)
            if response.status_code == 200:
                return {
                    "success": True,
                    "message": "Sent Message",
                    "token": token
                }
            else:
                return {
                    "success": False,
                    "error": "%s" % (response.json()),
                    "message": None
                }

class Protocol(object):
    
    def __init__(self):
        self.tokens = []
        self.users = list()

        with open("data/proxies.txt", encoding="utf-8") as f:
            self.proxies = [i.strip() for i in f]
        for line in open("data/tokens.txt"):
            self.tokens.append(line.replace("\n", ""))
        
        logging.info("loaded [%s] proxies" % (len(self.proxies)))
        logging.info("loaded [%s] tokens" % (len(self.tokens)))

        print()

        self.guild_id = input("\x1b[38;5;14m(\x1b[0m?\x1b[38;5;14m) \x1b[0mGuild ID\x1b[38;5;14m:\x1b[0m ")
        self.channel_id = int(input("\x1b[38;5;14m(\x1b[0m?\x1b[38;5;14m) \x1b[0mChannel ID\x1b[38;5;14m:\x1b[0m "))
        self.proxy_type = input("\x1b[38;5;14m(\x1b[0m?\x1b[38;5;14m) \x1b[0mProxytype\x1b[38;5;14m:\x1b[0m ")
        self.amount = int(input("\x1b[38;5;14m(\x1b[0m?\x1b[38;5;14m) \x1b[0mAmount to spam\x1b[38;5;14m:\x1b[0m "))
        self.tasks = int(input("\x1b[38;5;14m(\x1b[0m?\x1b[38;5;14m) \x1b[0mThreads/Tasks/Pools\x1b[38;5;14m:\x1b[0m "))

        print()
        
    async def start(self, token: str, message: str):
        try:
            proxy = random.choice(self.proxies)
            discord = Discord(
                proxies={
                    "type": self.proxy_type,
                    "proxy": proxy
                }
            )
            send = await discord.send(
                token=token,
                channel_id=self.channel_id,
                message=message
            )
            if send["success"]:
                logging.info("%s | %s" % (send["message"], send["token"]))
        except Exception as e:
            logging.error(e)

    async def fucking_start_and_start(self):
        client = discum.Client(token=self.tokens[0], log=False)
        client.gateway.fetchMembers(self.guild_id, self.channel_id, reset=True, keep="all")
        client.gateway.finishedMemberFetching(self.guild_id)
        @client.gateway.command
        def start_getting_ids(resp):
            if client.gateway.finishedMemberFetching(self.guild_id):
                client.gateway.removeCommand(start_getting_ids)
                client.gateway.close()

        client.gateway.run()
        for id in client.gateway.session.guild(self.guild_id).members:
            self.users.append(id)
            user_pool = cycle(self.users)
            message = ""
            for x in range(len(self.users)): message += "<@%s> " % (next(user_pool))

        async with tasksio.TaskPool(self.tasks) as pool:
            for x in range(self.amount):
                for token in self.tokens:
                    await pool.put(self.start(token, message))
                
if __name__ == "__main__":
    session = Protocol()
    asyncio.run(session.fucking_start_and_start())
