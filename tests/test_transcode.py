from automedia import main
import unittest
import pytest

@pytest.mark.parametrize("dir", [1])
def test_transcode_good(tmp_path, dir):
    print(dir)
    result = main.do_main(['', '--symlinks', '--root', f'tests/transcode-test-{dir}', 'transcode', '--preset', 'aac-64k', '--output', str(tmp_path)])
    assert result == 0
    pass
