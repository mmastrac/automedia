from automedia import main
import pytest

@pytest.mark.parametrize("dir", [1, 2])
def test_transcode_good(tmp_path, dir):
    print(dir)
    result = main.do_main(['', '--symlinks=allowfile', '--root', f'tests/transcode-test-{dir}', 'transcode', '--preset', 'aac-64k', '--output', str(tmp_path)])
    assert result == 0

@pytest.mark.parametrize("dir", [1])
def test_transcode_bad(tmp_path, dir):
    print(dir)
    result = main.do_main(['', '--symlinks=allowfile', '--root', f'tests/transcode-test-bad-{dir}', 'transcode', '--preset', 'aac-64k', '--output', str(tmp_path)])
    assert result == 1
