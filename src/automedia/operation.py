from abc import abstractmethod

class Operation:
    @abstractmethod
    def operate(self, dir, files):
        pass

    @abstractmethod
    def initialize(self, q, dir):
        pass

class PrintFilesOperation:
    def operate(self, q, _, files):
        q.info(f"{len(files)} file(s)")
        for file in files:
            q.info(f"  {file.name}")
        pass
