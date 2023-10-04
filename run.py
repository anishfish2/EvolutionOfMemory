from sc2 import maps
from sc2.player import Bot, Computer
from sc2.main import run_game
from sc2.data import Race, Difficulty
from sc2.bot_ai import BotAI
import sc2

import neat
from neatBot import NEATBot



import time



def evaluate_genome(genome, config):
    bot = NEATBot(genome, config)

    run_game(maps.get("AbyssalReefLE"), [
    Bot(Race.Zerg, bot),
    Computer(Race.Protoss, Difficulty.Easy)
    ], realtime=True)

    fitness = bot.calculate_fitness()
    
    return fitness

config_path = 'neat_config.ini'
config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                     neat.DefaultSpeciesSet, neat.DefaultStagnation,
                     config_path)

# Create the NEAT population
population = neat.Population(config)

# Run the NEAT algorithm
genome = neat.DefaultGenome(100)
winner = population.run(evaluate_genome(genome, config), 100)