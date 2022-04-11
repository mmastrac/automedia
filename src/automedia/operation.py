from abc import abstractmethod

class Operation:
    @abstractmethod
    def operate(dir, files):
        pass

class PrintFilesOperation:
    def operate(self, q, dir, files):
        q.info(f"{len(files)} file(s)")
        for file in files:
            q.info(f"  {file.name}")
        pass
