from automedia import main
import pytest

@pytest.mark.parametrize("dir", [1, 2])
def test_verify_good(dir):
    result = main.do_main(['', '--symlinks=allowfile', '--root', f'tests/verify-test-{dir}', 'verify'])
    assert result == 0

@pytest.mark.parametrize("dir", [1, 2, 3])
def test_verify_bad(dir):
    result = main.do_main(['', '--symlinks=allowfile', '--root', f'tests/verify-test-bad-{dir}', 'verify'])
    assert result == 1
