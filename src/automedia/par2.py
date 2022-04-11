import os
import subprocess

from enum import Enum
from pathlib import Path
from typing import List
from subprocess import Popen

from .operation import Operation

DEFAULT_PAR2_CREATE_ARGS = ' '.join(['-u', '-n3', '-r10'])
DEFAULT_PAR2_VERIFY_ARGS = ' '.join(['-N'])

RECOVERY_LIST_HEADER = "[media-tools-v1]"

class RecoveryList:
    def __init__(self, files) -> None:
        self.files = files

    def read(file: Path):
        with open(file, 'rt') as f:
            header = f.readline()
            if header.rstrip() != RECOVERY_LIST_HEADER:
                raise Exception(f"Invalid {file.name} found (header was {header}), cannot create parity files")
            old_files = [x.rstrip() for x in f.readlines()]
            old_files.sort()
        return RecoveryList(old_files)

    def write(self, file: Path):
        with open(file, 'wt') as f:
            f.write("[media-tools-v1]\n")
            f.write('\n'.join([x.name for x in self.files]))

class RecoveryListState(Enum):
    MISSING = 0
    UP_TO_DATE = 1
    ERROR = 2

class Par2Operation(Operation):
    def __init__(self, args, recovery_name) -> None:
        self.args = list(args)
        self.recovery_name = recovery_name

    def recovery_list(self, dir):
        return dir / f'{self.recovery_name}.filelist'

    def par2_index(self, dir):
        return dir / f'{self.recovery_name}.par2'

    def validate_recovery_list(self, q, dir: Path, files: List[Path]) -> RecoveryListState:
        if not self.par2_index(dir).exists():
            if self.recovery_list(dir).exists():
                q.warning("File list exists, but PAR2 does not exist")
            return RecoveryListState.MISSING
        if self.recovery_list(dir).exists():
            try:
                list = RecoveryList.read(self.recovery_list(dir))
                if list.files != [x.name for x in files]:
                    q.warning("PAR2 exists, but is out-of-date")
                    q.warning(list.files)
                    q.warning([x.name for x in files])
                else:
                    q.info("PAR2 exists, and is up-to-date")
                    return RecoveryListState.UP_TO_DATE
            except Exception as e:
                q.error(str(e))
                return RecoveryListState.ERROR
        return RecoveryListState.MISSING

    def run_par2(self, q, dir, args):
        # q.info(args)
        cmd = Popen(args, executable="par2", encoding="utf8", errors="", cwd=dir, stdout=subprocess.PIPE, stdin=subprocess.DEVNULL, stderr=subprocess.PIPE)
        stdout, stderr = cmd.communicate()
        if stderr:
            q.error(stderr)
        elif not stdout.find("\nDone"):
            q.error(stdout)
        elif cmd.returncode != 0:
            q.error(f"PAR2 returned a non-zero errorcode: {cmd.returncode}")
        else:
            return True
        return False

    def initialize(self, q, dir):
        self.root_args = args = ['par2', self.COMMAND] + self.args + ['--', f'{self.recovery_name}']
        q.info(f"{self.VERB} par2 files: {' '.join(self.root_args + ['[files...]'])}")

class CreatePar2Operation(Par2Operation):
    COMMAND = 'create'
    VERB = 'Creating'
    def operate(self, q, dir, files):
        if self.validate_recovery_list(q, dir, files) != RecoveryListState.MISSING:
            return
        args = self.root_args + [x.name for x in files]
        if self.run_par2(q, dir, args):
            if self.par2_index(dir).exists():
                RecoveryList(files).write(self.recovery_list(dir))
                q.info("Done")
            else:
                q.warning("No PAR2 files were generated")

class VerifyPar2Operation(Par2Operation):
    COMMAND = 'verify'
    VERB = 'Verifying'
    def operate(self, q, dir, files):
        if self.validate_recovery_list(q, dir, files) != RecoveryListState.UP_TO_DATE:
            q.warning("Unable to verify directory")
            return
        args = self.root_args + [x.name for x in files]
        if self.run_par2(q, dir, args):
            # If the user requested removal of PAR2 files, we should unlink our recovery list too
            if not self.par2_index(dir).exists():
                q.warning("PAR2 files were removed after verification")
                os.unlink(self.recovery_list(dir))
