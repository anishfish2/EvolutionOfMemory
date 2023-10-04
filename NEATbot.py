import sc2
from sc2 import maps
from sc2.player import Bot, Computer
from sc2.main import run_game
from sc2.data import Race, Difficulty
from sc2.bot_ai import BotAI
from sc2.position import Point2

import numpy as np 
import neat
config_path = 'neat_config.ini'

import time

import random

# Current Prey Bot: NEAT implementation to mine minerals
class NEATBot(BotAI):
    def __init__(self, genome, config):
        super().__init__()
        self.genome = genome
        self.config = config
        self.net = neat.nn.FeedForwardNetwork.create(self.genome, self.config)
        self.mined_mineral_fields = set()
        self.food_crumbs = set()
        self.tag_to_worker = {}
        self.max_energy = 100  # Set the maximum energy level
        self.current_energy = self.max_energy  # Initialize current energy level
        self.start_time = None
        self.observation_range = 100
        self.movement_speed = 10
        self.worker_x = None
        self.worker_y = None
    
    async def on_step(self, iteration):

        if iteration == 0:
            self.start_time = time.time()

            
        if self.current_energy <= 0:
            # print("Bot's energy is depleted. Ending the run.")
            await self.end_game()  # Using await to call the asynchronous function
            
            return
        
        # Decrease current energy
        self.current_energy = self.current_energy - .1

        # Pick one worker to be prey
        if 'my_worker' not in self.tag_to_worker:
            worker = self.workers.random
            if worker:
                self.tag_to_worker['my_worker'] = worker
                self.worker_x = worker.position.x
                self.worker_y = worker.position.y
        
        for worker in self.workers:
            if worker.tag != self.tag_to_worker.get('my_worker', None):
                # Stop command to stop all non selected worker current actions
                worker.stop()
                pass

        # Code for selected worker
        if 'my_worker' in self.tag_to_worker:
            worker = self.tag_to_worker['my_worker']

            # Provide observation input to the neural network
            observation_input = self.get_observation_input()

            # Use the neural network to decide whether to mine minerals
            action = self.net.activate(observation_input)

            select_action = np.argmax(np.array(action))

            # Generate random action if network says nothing
            print("Action:", action)
            if sum(action) == 0:
                select_action = random.randint(0, 9)
            
            print(select_action)
            print("Observation:", observation_input)
            if select_action == 10:
                print("Energy", self.current_energy)
                print("Action:", select_action)
            print(worker.position)
            print(self.worker_x, self.worker_y)
            if select_action == 0:  # Move up
                worker.move(Point2((self.worker_x, self.worker_y + self.movement_speed)))
                self.worker_y += self.movement_speed
                
            elif select_action == 1:  # Move down
                worker.move(Point2((self.worker_x, self.worker_y - self.movement_speed)))
                self.worker_y -= self.movement_speed
                
            elif select_action == 2:  # Move left
                worker.move(Point2((self.worker_x - self.movement_speed, self.worker_y)))
                self.worker_x -= self.movement_speed
                
            elif select_action == 3:  # Move right
                worker.move(Point2((self.worker_x + self.movement_speed, self.worker_y)))
                self.worker_x += self.movement_speed
                
            elif select_action == 4:  # Move diagonally up-left
                worker.move(Point2((self.worker_x - self.movement_speed, self.worker_y + self.movement_speed)))
                self.worker_x -= self.movement_speed
                self.worker_y += self.movement_speed
                
            elif select_action == 5:  # Move diagonally up-right
                worker.move(Point2((self.worker_x + self.movement_speed, self.worker_y + self.movement_speed)))
                self.worker_x += self.movement_speed
                self.worker_y += self.movement_speed
                
            elif select_action == 6:  # Move diagonally down-left
                worker.move(Point2((self.worker_x - self.movement_speed, self.worker_y - self.movement_speed)))
                self.worker_x -= self.movement_speed
                self.worker_y -= self.movement_speed
                
            elif select_action == 7:  # Move diagonally down-right
                worker.move(Point2((self.worker_x + self.movement_speed, self.worker_y - self.movement_speed)))
                self.worker_x += self.movement_speed
                self.worker_y -= self.movement_speed
            print(self.worker_x, self.worker_y)

            # elif select_action == 8:
            #     available_mineral_patches = [mineral_patch for mineral_patch in self.mineral_field if mineral_patch.tag not in self.mined_mineral_fields and mineral_patch.distance_to(worker.position) <= self.observation_range]
            
            #     if available_mineral_patches:
            #         # Choose the closest available mineral patch
            #         mineral_patch = min(available_mineral_patches, key=lambda patch: patch.distance_to(worker.position))
                    
            #         # Gather from the chosen mineral patch
            #         worker.gather(mineral_patch)
                    
            #         if worker.distance_to(mineral_patch) < 5.0:  # Adjust the threshold distance

            #             # Add the mineral patch to the set of mined fields
            #             self.mined_mineral_fields.add(mineral_patch.tag)
            #             self.current_energy += 5
            #             print("Gathered Materials")
            #         else:
            #             print("Too far from the mineral patch")    
            # elif select_action == 9: #Place Food Dropper
            #     print("Placing Dropper")
            #     self.food_crumbs.add(Point2((worker.position.x, worker.position.y)))
                    

    def calculate_fitness(self):
        '''
            Calculate fitness for genome

            Returns: Custom formula involving time stayed alive and food eaten
        '''
        
        time_alive = time.time() - self.start_time

        fitness = time_alive

        return fitness
    
    def get_observation_input(self):
        '''
            Get observation input for the prey.

            This method collects information about mineral patches and other game objects
            within a specified observation range from the selected worker.

            Returns:
                List: Observation input containing information about game objects. 0, 1 for [Mineral, Mineral Dropper, Enemy, Enemy Dropper]
        '''
        observation_input = np.array([0, 0, 0, 0])

        

        # Get the position of the selected worker
        worker_position = self.tag_to_worker['my_worker'].position

        # Loop through mineral patches and include them in the observation if they are within range
        for mineral_patch in self.mineral_field:
            if mineral_patch.distance_to(worker_position) <= self.observation_range and mineral_patch.tag not in self.mined_mineral_fields:
                observation_input[0] = 1

        for food_crumb in self.food_crumbs:
            if food_crumb.distance_to(worker_position) <= self.observation_range:
                observation_input[1] = 1
        
        return observation_input
    
    async def end_game(self):
        print("Ending the game")
        await self.leave_game()
    async def leave_game(self):
        try:
            await self.client.leave()
        except Exception as e:
            print(f"Error leaving the game: {e}")