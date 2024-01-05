from sc2 import maps
from sc2.player import Bot, Computer
from sc2.main import run_game
from sc2.data import Race, Difficulty
from sc2.bot_ai import BotAI
import sc2
import time

import neat
from neat.six_util import iteritems
from neatBot import NEATBot
from centerBot import moveBotCenter
from neatCenterBot import neatCenterBot
import time

# Function to write data to a file
def write_to_file(generation, genome_id, fitness):
    with open('neat_log.txt', 'a') as file:
        file.write(f"Generation {generation}, Genome ID {genome_id}, Fitness: {fitness}\n")



# Define the evaluation function
def evaluate_genome(genome, config, generation):
    bot = neatCenterBot(genome, config)

    run_game(maps.get("NEATmap"), [
        Bot(Race.Protoss, bot),
        Computer(Race.Protoss, Difficulty.Easy)
    ], realtime=False)


    fitness = bot.calculate_fitness()
    print(f"Genome fitness: {fitness}")
    genome.fitness = fitness

    # Write information to the file
    write_to_file(generation, genome.key, fitness)

    return fitness

# Load NEAT configuration
config_path = 'center_neat_config.ini'
config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                     neat.DefaultSpeciesSet, neat.DefaultStagnation, config_path)

# Create the NEAT population
population = neat.Population(config)

with open('neat_log.txt', 'w'):
    pass

generations = 5
best = None
for i in range(generations):
    with open('neat_log.txt', 'a') as file:
        file.write("Estimated time for generation: " + str(18 * len(list(iteritems(population.population)))) + " seconds \n")
    for g in list(iteritems(population.population)):
        evaluate_genome(g[1], config, i)

        if best is None or g[1].fitness > best.fitness:
            best = g[1]


    if population.best_genome is None or best.fitness > population.best_genome.fitness:
            population.best_genome = best

    population.population = population.reproduction.reproduce(population.config, population.species, population.config.pop_size, i)

    if not population.species.species:
                population.reporters.complete_extinction()

                if population.config.reset_on_extinction:
                    population.population = population.reproduction.create_new(population.config.genome_type,
                                                                   population.config.genome_config,
                                                                   population.config.pop_size)
                else:
                    break

    population.species.speciate(population.config, population.population, i)

    population.reporters.end_generation(population.config, population.population, population.species)

    population.generation = i

print("best fitness:", best.fitness)