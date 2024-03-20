import odds_dropper
import db
import asyncio
import threading
from dotenv import load_dotenv

load_dotenv()

record = odds_dropper.oddsDropper()

asyncio.run(record.call_pinnacle())



def set_timeout(func, sec):
    t = threading.Timer(sec, func)
    t.start()
    return t






