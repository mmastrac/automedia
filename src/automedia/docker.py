from lib2to3.pytree import Base
from pathlib import Path
from typing_extensions import Self

class Docker:
    def __init__(self, pwd, prefixes) -> None:
        if pwd == None or prefixes == None:
            self.docker_prefix = Path('/')
            return

        # Test each candidate to see if we can find the pwd
        pwd = Path(pwd)
        prefixes = [Path(x) for x in prefixes]
        for candidate in prefixes:
            candidate = Path(candidate) / pwd.relative_to('/')
            if candidate.exists():
                self.docker_prefix = candidate
                return

        raise BaseException("Unable to locate docker root")

    def none() -> Self:
        return Docker(None, None)

    def dockerize_path(self, path):
        return self.docker_prefix / Path(path)
