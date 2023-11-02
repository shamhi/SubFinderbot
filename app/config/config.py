from dotenv import load_dotenv
from os import getenv

load_dotenv()

TOKEN: str = getenv('TOKEN')

IDS: list[int] = list(map(int, getenv('IDS').split(',')))
