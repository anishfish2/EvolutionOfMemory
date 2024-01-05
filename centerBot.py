from sc2.position import Point2
from sc2.bot_ai import BotAI
import sc2
import asyncio
# Dummy Bot: Moves to center
class moveBotCenter(BotAI):
    def __init__(self):
        super().__init__()
        self.tag_to_worker = {}
        self.worker_x = None
        self.worker_y = None

    async def on_step(self, iteration: int):
        # Check if a worker with a specific tag exists, and if not, assign the tag
        if 'my_worker' not in self.tag_to_worker:
            worker = self.workers.random
            if worker:
                self.tag_to_worker['my_worker'] = worker
            self.worker_x = worker.position.x
            self.worker_y = worker.position.y

            map_width = self.game_info.map_size.width
            map_height = self.game_info.map_size.height
            print(map_width, map_height)
            
        for worker in self.workers:
            if worker.tag != self.tag_to_worker.get('my_worker', None):
                # Stop command to stop all non selected worker current actions
                worker.stop()
                pass


        # Code for selected worker
        if 'my_worker' in self.tag_to_worker:
            worker = self.tag_to_worker['my_worker']
            target_position = self.game_info.map_center 

            self.worker_x += 1
            self.worker_y += 1
            worker.move(Point2((self.worker_x, self.worker_x)))
            
 