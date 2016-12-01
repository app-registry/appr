import os.path
import pytest
import cnr.utils


def test_mkdirp_on_existing_dir(tmpdir):
    exists = str(tmpdir.mkdir("dir1"))
    cnr.utils.mkdir_p(exists)
    assert os.path.exists(exists)


def test_mkdirp(tmpdir):
    path = os.path.join(str(tmpdir), "new/directory/tocreate")
    cnr.utils.mkdir_p(path)
    assert os.path.exists(path)

@pytest.mark.xfail
def test_mkdirp_unauthorized(tmpdir):
    import os
    d = str(tmpdir.mkdir("dir2"))
    path = os.path.join(d, "directory/tocreate")
    os.chmod(d, 0)
    with pytest.raises(OSError):
        cnr.utils.mkdir_p(path)
