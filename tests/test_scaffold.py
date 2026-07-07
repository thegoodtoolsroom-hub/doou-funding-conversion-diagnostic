from pathlib import Path

def test_required_folders_exist():
    required = [
        "app",
        "engine",
        "templates",
        "product_lock",
        "test_data",
        "tests",
        "outputs",
        "docs",
    ]
    for folder in required:
        assert Path(folder).exists(), f"Missing folder: {folder}"

def test_required_setup_files_exist():
    required = ["README.md", "requirements.txt", "Makefile"]
    for file_name in required:
        assert Path(file_name).exists(), f"Missing file: {file_name}"
