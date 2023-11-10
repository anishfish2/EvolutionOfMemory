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
            
        if self.current_energy <= 0:
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
                self.worker_position = worker.position
        
        for worker in self.workers:
            if worker.tag != self.tag_to_worker.get('my_worker', None):
                # Stop command to stop all non selected worker current actions
                worker.stop()
                pass

        # Code for selected worker
        if 'my_worker' in self.tag_to_worker:
            worker = self.tag_to_worker['my_worker']

           

            
            self.worker_position = Point2((self.worker_x, self.worker_y))
    
            # Check if the worker is close to an unmined mineral
            self.closest_to = self.mineral_field.closest_to(self.worker_position)

            if (self.worker_position.distance_to(self.closest_to) < self.observation_range) and (self.closest_to.tag not in self.mined_mineral_fields):
                self._client.debug_box2_out(Point3((self.closest_to.position.x, self.closest_to.position.y, 7)), 2, 5)


                self.mined_mineral_fields.add(self.mineral_field.closest_to(worker).tag)
            
                
                return
            # Provide observation input to the neural network
            observation_input = self.get_observation_input()
            # Use the neural network to decide whether to mine minerals
            action = self.net.activate(observation_input)

            select_action = np.argmax(np.array(action))
            
            
            if sum(action) == 0:
                select_action = random.randint(0, 9)
            if select_action == 0:  # Move up
                if  self.worker_y + self.movement_speed < self.game_info.map_size.height - 1:
                    worker.move(Point2((self.worker_x, self.worker_y + self.movement_speed)))
                    self.worker_y += self.movement_speed
                    self.worker_position = worker.position
                else:
                    self.penalty += .01


            elif select_action == 1:  # Move down
                if 0 < self.worker_y - self.movement_speed:
                    worker.move(Point2((self.worker_x, self.worker_y - self.movement_speed)))
                    self.worker_y -= self.movement_speed
               
                    self.worker_position = worker.position
                else:
                    self.penalty += .01
            elif select_action == 2:  # Move left
                if 0 < self.worker_x - self.movement_speed:
                    worker.move(Point2((self.worker_x - self.movement_speed, self.worker_y)))
                    self.worker_x -= self.movement_speed
                    self.worker_position = worker.position 
                else:
                    self.penalty += .01
            elif select_action == 3:  # Move right
                if self.worker_x + self.movement_speed < self.game_info.map_size.width - 1:
                    worker.move(Point2((self.worker_x + self.movement_speed, self.worker_y)))
                    self.worker_x += self.movement_speed
                    self.worker_position = worker.position
                else:
                    self.penalty += .01
            elif select_action == 4:  # Move diagonally up-left
                if 0 < self.worker_x - self.movement_speed and self.worker_y + self.movement_speed < self.game_info.map_size.height - 1:
                    worker.move(Point2((self.worker_x - self.movement_speed, self.worker_y + self.movement_speed)))
                    self.worker_x -= self.movement_speed
                    self.worker_y += self.movement_speed
                    self.worker_position = worker.position
                else:
                    self.penalty += .01
            elif select_action == 5:  # Move diagonally up-right
                if self.worker_x + self.movement_speed < self.game_info.map_size.width - 1 and self.worker_y + self.movement_speed < self.game_info.map_size.height - 1:
                    worker.move(Point2((self.worker_x + self.movement_speed, self.worker_y + self.movement_speed)))
                    self.worker_x += self.movement_speed
                    self.worker_y += self.movement_speed
                    self.worker_position = worker.position
                else:
                    self.penalty += .01
            elif select_action == 6:  # Move diagonally down-left
                if 0 < self.worker_x - self.movement_speed and 0 < self.worker_y - self.movement_speed:
                    worker.move(Point2((self.worker_x - self.movement_speed, self.worker_y - self.movement_speed)))
                    self.worker_x -= self.movement_speed
                    self.worker_y -= self.movement_speed
                    self.worker_position = worker.position
                else:
                    self.penalty += .01
            elif select_action == 7:  # Move diagonally down-right
                if self.worker_x + self.movement_speed < self.game_info.map_size.width - 1 and 0 < self.worker_y - self.movement_speed:
                    worker.move(Point2((self.worker_x + self.movement_speed, self.worker_y - self.movement_speed)))
                    self.worker_x += self.movement_speed
                    self.worker_y -= self.movement_speed
                    self.worker_position = worker.position
                else:
                    self.penalty += .01

            if iteration % 100 == 0:
                print("Action", select_action, "Energy:", self.current_energy, "Reward:", self.mined_mineral_fields)

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
        observation_input = np.zeros(16)  # Initialize the array with zeros

        # Get the position of the selected worker
        # worker_position = self.tag_to_worker['my_worker'].position

        # Define the directions for the 8 sensors
        directions = [
            (1, 0),   # Right
            (0, 1),   # Up
            (-1, 0),  # Left
            (0, -1),  # Down
            (1, 1),   # Up-Right
            (-1, 1),  # Up-Left
            (-1, -1), # Down-Left
            (1, -1)   # Down-Right
        ]

        # Loop through directions and include objects in the observation if they intersect the line
        for i, direction in enumerate(directions):
            dx, dy = direction
            sensor_position = self.worker_position + Point2((dx * self.observation_range, dy * self.observation_range))

            # Use Bresenham's Line Algorithm to iterate through the cells along the line
            x0, y0 = int(self.worker_x), int(self.worker_y)
            x1, y1 = int(sensor_position.x), int(sensor_position.y)

            steep = abs(y1 - y0) > abs(x1 - x0)
            if steep:
                x0, y0 = y0, x0
                x1, y1 = y1, x1

            if x0 > x1:
                x0, x1 = x1, x0
                y0, y1 = y1, y0

            deltax = x1 - x0
            deltay = abs(y1 - y0)
            error = deltax / 2
            y = y0
            ystep = None

            if y0 < y1:
                ystep = 1
            else:
                ystep = -1

            for x in range(x0, x1 + 1):
                if steep:
                    cell_position = Point2((y, x))
                else:
                    cell_position = Point2((x, y))

                # Check if any mineral patches are present in the current cell
                for mineral_patch in self.mineral_field:
                    if mineral_patch.distance_to(cell_position) <= 3 and mineral_patch.tag not in self.mined_mineral_fields:
                        if mineral_patch.distance_to(self.worker_position) < observation_input[i] or observation_input[i] == 0:
                            observation_input[i] = mineral_patch.distance_to(self.worker_position)# Set the corresponding sensor value to 1 for minerals

                # Check if any food crumbs are present in the current cell
                for food_crumb in self.food_crumbs:
                    if food_crumb.distance_to(cell_position) <= 1:
                        observation_input[i + 8] = 1  # Set the corresponding sensor value to 1 for droppers

                error -= deltay
                if error < 0:
                    y += ystep
                    error += deltax

        return observation_input
    
    async def end_game(self):
        print("Ending the game")
        await self.leave_game()
        time.sleep(2)

    async def leave_game(self):
        try:
            await self.client.leave()
        except Exception as e:
            print(f"Error leaving the game: {e}")