import sc2
from sc2 import maps
from sc2.player import Bot, Computer
from sc2.main import run_game
from sc2.data import Race, Difficulty
from sc2.bot_ai import BotAI
from sc2.position import Point2, Point3

import numpy as np 
import neat

config_path = 'neat_config.ini'

import time
import math
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

    async def find_starting_base(self):
        for unit in self.units:
            if unit.type_id in {sc2.constants.UnitTypeId.COMMANDCENTER, sc2.constants.UnitTypeId.NEXUS, sc2.constants.UnitTypeId.HATCHERY}:
                self.starting_base_position = unit.position
                break
        
    async def set_mineral_values(self):
        for unit in self.units:
            if unit.type_id == sc2.constants.UnitTypeId.MINERALFIELD:
                self.do(unit.tag_set(sc2.ControlGroup(1)))

    async def find_closest_mineral_patch(self):
        worker = self.tag_to_worker['my_worker']
        # Get all mineral patches on the map
        mineral_patches = self.mineral_field

        if mineral_patches:
            # Calculate the distance between the worker and each mineral patch
            distances = [worker.distance_to(mineral) for mineral in mineral_patches]

            # Find the index of the mineral patch with the minimum distance
            closest_mineral_index = distances.index(min(distances))

            # Return the closest mineral patch
            return mineral_patches[closest_mineral_index]

        return None
    
    async def on_step(self, iteration):
        
        if iteration == 0:
            self.start_time = time.time()
            await self.find_starting_base()
            await self.set_mineral_values()
            
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

        else:
            if 'my_worker' in self.tag_to_worker:
                worker = self.tag_to_worker['my_worker']


                if self.current_energy <= 0:
                    await self.end_game()  # Using await to call the asynchronous function
                
                    return

            # Decrease current energy
                self.current_energy = self.current_energy - .1

            # Check if the worker is close to an unmined mineral
            self.closest_to = self.mineral_field.closest_to(self.worker_position)

            if (self.worker_position.distance_to(self.closest_to) < self.observation_range) and (self.closest_to.tag not in self.mined_mineral_fields):
                self._client.debug_box2_out(Point3((self.closest_to.position.x, self.closest_to.position.y, 7)), 2, 5)
                self.mined_mineral_fields.add(self.mineral_field.closest_to(worker).tag)
                return
            
            observation_input = self.get_observation_input()
            action = self.net.activate(observation_input)

            select_action = np.argmax(np.array(action))
            
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
    
    def calculate_fitness(self):
        '''
            Calculate fitness for genome

            Returns: Custom formula involving time stayed alive and food eaten
        '''
        
        time_alive = time.time() - self.start_time 

        fitness = time_alive + 10 * len(self.mined_mineral_fields) - self.penalty

        return fitness
    
    def get_observation_input(self):
        '''
            Get observation input for the prey.

            This method collects information about mineral patches and other game objects
            within a specified observation range from the selected worker.

            Returns:
                List: Observation input containing information about game objects. 0, 1 for [Mineral Sensor 1, Mineral Sensor 2,...,Mineral Sensor 8, Dropper Sensor 1, Dropper Sensor 2,..., Dropper Sensor 8]
        '''
        observation_input = np.zeros(8)  # Initialize the array with zeros

        
    def find_nearest_object(section_center, objects):
        min_distance = float('inf')
        nearest_object = None

        for obj in objects:
            distance = section_center.distance_to(Point2(obj))
            if distance < min_distance:
                min_distance = distance
                nearest_object = obj

        return nearest_object

    async def end_game(self):
        print("Ending the game")
        await self.leave_game()
        time.sleep(2)

    async def leave_game(self):
        try:
            await self.client.leave()
        except Exception as e:
            print(f"Error leaving the game: {e}")