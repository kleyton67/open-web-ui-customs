import concurrent.futures
import time
from loguru import logger
from abc import abstractmethod
import asyncio


class Task(object):
    def __init__(self,):
        pass
    
    @abstractmethod
    def run(self):
        pass
    
class ProceduralTask(Task):
    def __init__(self, id, content):
        self.id = id
        self.content = content
    
    def run(self):
        logger.info(f"Processing {self.id}")
        time.sleep(2)
        logger.info(f"Processed {self.content}")
        return self.id

class AsyncTask(Task):
    def __init__(self, id, content):
        self.id = id
        self.content = content
    
    async def async_running(self):
        logger.info(f"Processing {self.id}")
        await asyncio.sleep(2)
        logger.info(f"Processed {self.content}")
        return self.id

    def run(self):
        result = asyncio.run(self.async_running())
        return result


# Controller - orchestrates the workers and tasks processing
class TaskController:
    def __init__(self, worker_count=5):
        self.worker_count = worker_count

    def process_tasks(self, task:Task):
        return task.run()

    def start_workers(self, tasks):
        with concurrent.futures.ProcessPoolExecutor(max_workers=self.worker_count) as executor:
            return zip(tasks, executor.map(self.process_tasks, tasks))

def main():
    tasks = [
            ProceduralTask(id=1, content='Task 1'),
            ProceduralTask(id=2, content='Task 2'),
            AsyncTask(id=3, content='Task 3'),
            AsyncTask(id=4, content='Task 4'),
            ProceduralTask(id=5, content='Task 5'),   
            AsyncTask(id=6, content='Task 6'),
        ]
    controller = TaskController(worker_count=2)
    # Start workers
    results = controller.start_workers(tasks)

    import pdb
    pdb.set_trace()

if __name__ == "__main__":
    main()