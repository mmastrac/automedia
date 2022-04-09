"""
Single-threaded job queue. This should be turned into a parallel job queue at some point.
"""
class JobQueue:
    def __init__(self, name=None, parent=None) -> None:
        self.name = name if name else ""
        self.parent = parent

    def submit(self, name, job):
        job(JobQueue(name=name, parent=self))
        pass

    def error(self, msg):
        print(f'E[{self._name()}]: {msg}', flush=True)
        pass

    def info(self, msg):
        print(f'I[{self._name()}]: {msg}', flush=True)
        pass

    def warning(self, msg):
        print(f'W[{self._name()}]: {msg}', flush=True)
        pass

    def wait(self):
        pass

    def _name(self):
        if self.parent:
            return f'{self.parent._name()}/{self.name}'
        return self.name
