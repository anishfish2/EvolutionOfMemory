from sc2.position import Point2
from sc2.bot_ai import BotAI
import sc2
import asyncio
from sc2.unit import Unit
import numpy as np
import neat
config_path = 'center_neat_config.ini'

import time
import math
import random

class neatCenterBot(BotAI):
    def __init__(self, genome, config):
        super().__init__()
        self.genome = genome
        self.config = config
        self.net = neat.nn.FeedForwardNetwork.create(self.genome, self.config)
        self.mined_mineral_fields = set()
        self.food_crumbs = set()
        self.tag_to_worker = {}
        self.max_energy = 50  # Set the maximum energy level
        self.current_energy = self.max_energy  # Initialize current energy level
        self.start_time = None
        self.observation_range = 3
        self.movement_speed = .1
        self.worker_x = None
        self.worker_y = None
        self.worker_position = None
        self.starting_base_position = None
        self.penalty = 0
        self.closest_to = None
        self.best = float('inf')

    async def on_step(self, iteration: int):
        if iteration == 0:
            self.start_time = time.time()

            # Check if a worker with a specific tag exists, and if not, assign the tag
            if 'my_worker' not in self.tag_to_worker:
                worker = self.workers.random
                if worker:
                    self.tag_to_worker['my_worker'] = worker
            
                    
            for worker in self.workers:
                if worker.tag != self.tag_to_worker.get('my_worker', None):
                    # Stop command to stop all non-selected worker current actions
                    worker.stop()

            # Code for selected worker
            if 'my_worker' in self.tag_to_worker:
                worker = self.tag_to_worker['my_worker']

                self.worker_x, self.worker_y = worker.position.x, worker.position.y
                await asyncio.sleep(1)




        if 'my_worker' in self.tag_to_worker:
                worker = self.tag_to_worker['my_worker']


                if self.current_energy <= 0:
                    await self.end_game()  # Using await to call the asynchronous function
                
                    return
            
                # Decrease current energy
                self.current_energy = self.current_energy - .1


                observation_input = self.get_observation_input()
                if observation_input < self.best:
                    self.best = observation_input
                action = self.net.activate([observation_input])
                delta_x, delta_y = self.move_character(action[0], action[1])
                if delta_x + delta_y == 0:
                    self.penalty += 1
                print(action[0], action[1])
                if self.worker_x + delta_x >= 10 and self.worker_x + delta_x <= 118 and self.worker_y + delta_y >= 10 and self.worker_y + delta_y <= 118:
                    self.worker_x += delta_x
                    self.worker_y += delta_y
                    worker.move(Point2((self.worker_x, self.worker_y)))
                else:
                    self.penalty += .1
                

                

    def move_character(self, angle, magnitude):
        # Convert angle to radians
        angle_rad = math.radians(angle)

        # Calculate the change in x and y using trigonometry
        delta_x = magnitude * math.cos(angle_rad)
        delta_y = magnitude * math.sin(angle_rad)

        return delta_x, delta_y

    def get_observation_input(self):
            '''
                Get observation input for the prey.

                This method collects information about mineral patches and other game objects
                within a specified observation range from the selected worker.

                Returns:
                    List: Observation input containing information about game objects. 0, 1 for [Mineral Sensor 1, Mineral Sensor 2,...,Mineral Sensor 8, Dropper Sensor 1, Dropper Sensor 2,..., Dropper Sensor 8]
            '''
            return Point2((self.worker_x, self.worker_y)).distance_to(self.game_info.map_center)
    
    def calculate_fitness(self):
        '''
            Calculate fitness for genome

            Returns: Custom formula involving time stayed alive and food eaten
        '''
        fitness = self.best + self.penalty

        return fitness
    
    async def end_game(self):
        print("Ending the game")
        await self.leave_game()
        time.sleep(2)

    async def leave_game(self):
        try:
            await self.client.leave()
        except Exception as e:
            print(f"Error leaving the game: {e}")