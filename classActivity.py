import asyncio
import websockets
from functools import partial





class mainly:
    def __init__(self):
        self.message = ""
        self.flag = 0
        self.lu = 0
    async def writeMessage(self, m):
        print("message écrit !!! ")
        self.message=m
        self.flag = 1
        self.lu = 0
    def printe(self):
        print("est")
    def lireMessage(self):
        if self.lu == 1:
            return 0
        else:
            if self.flag == 1:
                self.lu = 1
                self.flag = 0
                return self.message
            else:
                return 0
    def presenceMessage(self):
        if self.lu == 0 and self.flag ==1:
            return True
        else:
            return False


