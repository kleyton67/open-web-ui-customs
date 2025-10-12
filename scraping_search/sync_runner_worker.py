from events import EventDumper

from concurrent.futures import ThreadPoolExecutor

class SaveQueue:
    def __init__(self, timestamp, max_workers=1, logger=None):
        self._exec = ThreadPoolExecutor(max_workers=max_workers)
        self.logger=logger

    def save_before(self, pre_frames, dumper: EventDumper):
        event_path = dumper.begin()
        self.logger.info(f"EVENT: criado em {event_path}. BEFORE saved!!!")
        fut = self._exec.submit(dumper.save_before, pre_frames)
        

    def save_after(self, frame_idx, frame, dumper: EventDumper, is_last=False):
        fut = self._exec.submit(dumper.save_after, frame_idx, frame, is_last)
        
        if fut.done():
            del dumper

