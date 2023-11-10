from sc2.position import Point2
from sc2.bot_ai import BotAI
import sc2
import asyncio
from sc2.unit import Unit

class workingBot(BotAI):
    def __init__(self):
        super().__init__()
        self.tag_to_worker = {}
        self.mined_mineral_fields = set()
        self.food_crumbs = set()
        self.max_energy = 100
        self.current_energy = self.max_energy
        self.start_time = None
        self.observation_range = 100
        self.movement_speed = 0.1
        self.worker_x = None
        self.worker_y = None
        self.worker_position = None
        self.starting_base_position = None
        self.penalty = 0
        self.is_mining = False
        self.is_returning = False
        self.check = False
        self.target = None
        self.is_mining = False
    async def on_step(self, iteration: int):
        if iteration == 0:
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

                worker.gather(self.mineral_field.closest_to(worker))
                await asyncio.sleep(1)
                print("This one", worker.orders)

        if 'my_worker' in self.tag_to_worker:
                worker = self.tag_to_worker['my_worker']

                print(iteration, worker.orders, worker.is_gathering, worker.is_carrying_minerals)
