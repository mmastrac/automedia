"""
Single-threaded job queue. This should be turned into a parallel job queue at some point.
"""
class JobQueue:
    def __init__(self, name=None, parent=None) -> None:
        self.name = name
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
        if name is None and self.name is not None:
            raise Exception('Queue must have a name if parent queue has a name')
        sub = JobQueue(name=name, parent=self)
        self.subs.append(sub)
        job(sub)
        sub.flush_logs()

    def flush_logs(self):
        for level, msg in self.logs:
            print(f'{level}[{self._name()}]: {msg}', flush=True)
        self.logs = []

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

    def is_root(self):
        return self.parent is None or self.name is None

    def _name(self):
        if self.is_root():
            return '(root)'
        else:
            return f'{self.parent._name()}/{self.name}'
