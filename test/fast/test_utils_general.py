from utils.general import get_file_paths_in_directory


def test_empty_directory(tmp_path):
    assert get_file_paths_in_directory(tmp_path) == []


def test_directory_with_files(tmp_path):
    (tmp_path / "file1.txt").touch()
    (tmp_path / "file2.txt").touch()
    assert len(get_file_paths_in_directory(tmp_path)) == 2


def test_directory_with_files_and_subdirs(tmp_path):
    (tmp_path / "file1.txt").touch()
    subdir1 = tmp_path / "subdir1"
    subdir1.mkdir()
    (subdir1 / "file2.txt").touch()
    subdir2 = tmp_path / "subdir2"
    subdir2.mkdir()
    (subdir2 / "file3.txt").touch()
    assert len(get_file_paths_in_directory(tmp_path)) == 3


def test_directory_with_py_files(tmp_path):
    (tmp_path / "script1.py").touch()
    (tmp_path / "script2.py").touch()
    (tmp_path / "document.txt").touch()
    (tmp_path / "image.jpg").touch()

    py_files = get_file_paths_in_directory(tmp_path, ".py")

    assert len(py_files) == 2
    assert all(file.endswith(".py") for file in py_files)
