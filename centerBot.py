# Dummy Bot: Moves to center
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