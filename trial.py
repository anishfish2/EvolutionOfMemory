from sc2 import maps
from sc2.player import Bot, Computer
from sc2.main import run_game
from sc2.data import Race, Difficulty
from sc2.bot_ai import BotAI

import neat
config_path = 'neat_config.ini'

#Pick one worker and move to center
class moveBotCenter(BotAI):
    def __init__(self):
        super().__init__()
        self.tag_to_worker = {}

    async def on_step(self, iteration: int):
        # Check if a worker with a specific tag exists, and if not, assign the tag
        if 'my_worker' not in self.tag_to_worker:
            worker = self.workers.random
            if worker:
                self.tag_to_worker['my_worker'] = worker

        for worker in self.workers:
            if worker.tag != self.tag_to_worker.get('my_worker', None):
                # Stop command to stop all non selected worker current actions
                worker.stop()
                pass

        # Code for selected worker
        if 'my_worker' in self.tag_to_worker:
            worker = self.tag_to_worker['my_worker']
            target_position = self.game_info.map_center 
            worker.move(target_position)

# run_game(maps.get("AbyssalReefLE"), [
#     Bot(Race.Zerg, customBot()),
#     Computer(Race.Protoss, Difficulty.Easy)
# ], realtime=True)


class NEATBot(BotAI):
    def __init__(self, genome, config):
        super().__init__()
        self.genome = genome
        self.config = config
        self.net = neat.nn.FeedForwardNetwork.create(self.genome, self.config)
        self.minerals_gathered = 0  # Track the total minerals gathered
        self.gathering_started = 0 # Track the total minerals started
        self.tag_to_worker = {}
        
    async def on_step(self, iteration):
        if 'my_worker' not in self.tag_to_worker:
            worker = self.workers.random
            if worker:
                self.tag_to_worker['my_worker'] = worker

        for worker in self.workers:
            if worker.tag != self.tag_to_worker.get('my_worker', None):
                # Stop command to stop all non selected worker current actions
                worker.stop()
                pass

        # Code for selected worker
        if 'my_worker' in self.tag_to_worker:
            worker = self.tag_to_worker['my_worker']
            # Provide observation input to the neural network for the selected worker
            observation_input = self.get_observation_input()

            # Use the neural network to decide whether to mine minerals
            action = self.net.activate(observation_input)

            # If the neural network decides to mine, issue a gather command
            if action[0] >= 0.0:  # Adjust the threshold as needed
                mineral_patch = self.mineral_field.closest_to(worker)
                worker.gather(mineral_patch)

        

    def calculate_fitness(self):
        # Calculate the time it took for gathering
        gathering_time = self.time - self.gathering_started

        # Calculate the fitness based on minerals gathered and gathering time
        # Adjust the weights and formula as needed for your specific fitness criteria
        fitness = self.minerals_gathered - gathering_time * 0.01

        return fitness
    
    def get_observation_input(self):
        observation_input = []

        # Define the observation range (e.g., within 10 units)
        observation_range = 10

        # Get the position of the selected worker
        worker_position = self.tag_to_worker['my_worker'].position

        # Loop through mineral patches and include them in the observation if they are within range
        for mineral_patch in self.mineral_field:
            if mineral_patch.distance_to(worker_position) <= observation_range:
                # Add information about mineral patches within range
                observation_input.append(mineral_patch.position.x)
                observation_input.append(mineral_patch.position.y)
                # You can add more information about mineral patches as needed

        # Add information about other game objects within range (e.g., enemies, buildings)
        for unit in self.units:
            if unit.distance_to(worker_position) <= observation_range and unit != self.tag_to_worker['my_worker']:
                # Add information about the unit within range
                observation_input.append(unit.position.x)
                observation_input.append(unit.position.y)
                # You can add more information about units as needed

        # Ensure the observation input has a fixed size by padding with zeros if necessary
        observation_size = 100  # Define the desired observation size
        while len(observation_input) < observation_size:
            observation_input.append(0.0)

        return observation_input

config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                     neat.DefaultSpeciesSet, neat.DefaultStagnation,
                     config_path)

# Create the NEAT population
population = neat.Population(config)



def evaluate_genome(genome, config):
    bot = NEATBot(genome, config)

    run_game(maps.get("AbyssalReefLE"), [
    Bot(Race.Zerg, bot),
    Computer(Race.Protoss, Difficulty.Easy)
    ], realtime=True)

    # Define a fitness value based on the performance of the worker
    fitness = bot.calculate_fitness()

    return fitness

# Run the NEAT algorithm
genome = neat.DefaultGenome(100)
winner = population.run(evaluate_genome(genome, config), 100)