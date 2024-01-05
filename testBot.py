from sc2 import maps
from sc2.player import Bot, Computer
from sc2.main import run_game
from sc2.data import Race, Difficulty
from sc2.bot_ai import BotAI
import sc2

import neat
from neat.six_util import iteritems, itervalues
from neatBot import NEATBot
from centerBot import moveBotCenter 
from workingBot import workingBot
from neatCenterBot import neatCenterBot
import time




bot = moveBotCenter()
        
run_game(maps.get("NEATmap"), [
Bot(Race.Protoss, bot),
Computer(Race.Protoss, Difficulty.Easy)
], realtime=False)