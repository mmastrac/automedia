from pathlib import Path

class Docker:
    def __init__(self, pwd, prefixes) -> None:
        if pwd == None or prefixes == None:
            self.docker_prefix = None
            return

        # Test each candidate to see if we can find the pwd
        pwd = Path(pwd)
        prefixes = [Path(x) for x in prefixes]
        for candidate in prefixes:
            if (candidate / pwd.relative_to('/')).exists():
                self.docker_prefix = candidate
                self.pwd = candidate / pwd.relative_to('/')
                return

        raise BaseException("Unable to locate docker root")

    def none():
        return Docker(None, None)

    def dockerize_path(self, path):
        path = Path(path)
        if self.docker_prefix is None:
            return path
        if path.is_absolute():
            return self.docker_prefix / Path(path).relative_to('/')
        return self.pwd / path
