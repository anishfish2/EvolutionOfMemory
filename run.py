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
    # for genome_id, genome in genomes:
        bot = NEATBot(genome, config)
        
        run_game(maps.get("NEATmap"), [
        Bot(Race.Protoss, bot),
        Computer(Race.Protoss, Difficulty.Easy)
        ], realtime=False)

        fitness = bot.calculate_fitness()
        print(f"Genome fitness: {fitness}")

        genome.fitness = fitness

config_path = 'neat_config.ini'
config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                    neat.DefaultSpeciesSet, neat.DefaultStagnation,
                    config_path)


# Create the NEAT population
# population = neat.Population(config)

# example_genome_id, example_genome = next(iter(population.population.items()))
# Run the NEAT algorithm
genome = neat.DefaultGenome(100)
evaluate_genome(genome, config)

# winner = population.run(evaluate_genome, 100)

# evaluate_genome(genome, config)