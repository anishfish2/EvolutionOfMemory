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
from neatCenterBot import neatCenterBot
import time



def evaluate_genome(genome, config):
    # for genome_id, genome in genomes:
        bot = neatCenterBot(genome, config)
        
        run_game(maps.get("NEATmap"), [
        Bot(Race.Protoss, bot),
        Computer(Race.Protoss, Difficulty.Easy)
        ], realtime=False)

        fitness = bot.calculate_fitness()
        print(f"Genome fitness: {fitness}")

        genome.fitness = fitness

def evaluate_genomes(genomes, config):
    for genome_id, genome in genomes:
        print("evaluating", genome_id, "/", len(genomes))
        evaluate_genome(genome, config)
 
def advance_one_generation(p, isPrey):
    print("starting to advance one population")
    global best_prey_genome
    global best_prey_config
    p.reporters.start_generation(p.generation)

    evaluate_genomes(list(iteritems(p.population)), p.config)

    best = None
    a = 0
    for g in itervalues(p.population):
        print(a , "/", len(p.population))
        if best is None or g.fitness > best.fitness:
            best = g
        a += 1
    p.reporters.post_evaluate(p.config, p.population, p.species, best)

    if p.best_genome is None or best.fitness > p.best_genome.fitness:
        print("new best genome in population")
        p.best_genome = best
        best_prey_genome = best
        best_prey_config = p.config

    if not p.config.no_fitness_termination:

        fv = p.fitness_criterion(g.fitness for g in itervalues(p.population))
        if fv >= p.config.fitness_threshold:
            p.reporters.found_solution(p.config, p.generation, best)
            return 1
        
    p.population = p.reproduction.reproduce(p.config, p.species, p.config.pop_size, p.generation)

    if not p.species.species:
        p.reporters.complete_extinction()

        if p.config.reset_on_extinction:
            p.population = p.reproduction.create_new(p.config.genome_type,
                                                            p.config.genome_config,
                                                            p.config.pop_size)



    p.species.speciate(p.config, p.population, p.generation)

    p.reporters.end_generation(p.config, p.population, p.species)

    p.generation += 1

    print("ending advance of one population")
    return 0



def main():
    num_preys = 1
    generations = 5 

    config_path = 'center_neat_config.ini'
    config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                    neat.DefaultSpeciesSet, neat.DefaultStagnation,
                    config_path)

    prey_pops = []

    for i in range(num_preys):
        p = neat.Population(config)
        p.add_reporter(neat.StdOutReporter(True))
        stats = neat.StatisticsReporter()
        p.add_reporter(stats)
        p.add_reporter(neat.Checkpointer(5, None, f'checkpoints/prey-test-agent_{i}-'))
        prey_pops.append(p)
    
    print(f"prey_pops = {prey_pops}")

    curr_num_gens = 0

    while generations is None or curr_num_gens < generations:
        # need to find the best opposing genomes and their configs
        if curr_num_gens == 0:
            best_prey_genome = list(iteritems(prey_pops[0].population))[0][1]
            best_prey_config = prey_pops[0].config

        print(f"Running prey populations", curr_num_gens, "/", generations)
        count = 0
        for p in prey_pops:
            print(count, "/", len(prey_pops))
            ret_val = advance_one_generation(p, True)
            print("finished advancing one population")
            if ret_val == 1:
                print("threshold passed, returned 1")
            else:
                print("threshold not passed, needs another go")

        curr_num_gens += 1
    print("done")


if __name__ == '__main__':
    main()
