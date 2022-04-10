"""
Single-threaded job queue. This should be turned into a parallel job queue at some point.
"""
class JobQueue:
    def __init__(self, name=None, parent=None) -> None:
        self.name = name if name else ""
        self.parent = parent
        self.waited = False
        self.subs = []
        self.logs = []

    def __del__(self):
        if not self.waited and len(self.subs) > 0:
            print(f'X[{self._name()}]: Failed to wait for subordinate jobs!', flush=True)
        if self.logs:
            print(f'X[{self._name()}]: Failed to print logs!', flush=True)

    def submit(self, name, job):
        sub = JobQueue(name=name, parent=self)
        self.subs.append(sub)
        job(sub)
        for level, msg in sub.logs:
            print(f'{level}[{sub._name()}]: {msg}', flush=True)
        sub.logs = []
        pass

    def error(self, msg):
        self._log("E", msg)

    def info(self, msg):
        self._log("I", msg)

    def warning(self, msg):
        self._log("W", msg)

    def _log(self, level, msg):
        self.logs.append((level, msg))

    def wait(self):
        self.waited = True
        pass

    def _name(self):
        if self.parent:
            return f'{self.parent._name()}/{self.name}'
        return self.name
