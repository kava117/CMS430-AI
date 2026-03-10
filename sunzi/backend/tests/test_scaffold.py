import os
import importlib

BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def test_requirements_txt_exists():
    assert os.path.isfile(os.path.join(BACKEND_DIR, "requirements.txt"))


def test_requirements_contains_expected_packages():
    path = os.path.join(BACKEND_DIR, "requirements.txt")
    content = open(path).read()
    for pkg in ["flask", "openai", "chromadb", "python-dotenv", "pytest", "pytest-mock"]:
        assert pkg in content, f"Missing package: {pkg}"


def test_env_example_exists():
    assert os.path.isfile(os.path.join(BACKEND_DIR, ".env.example"))


def test_env_example_contains_openai_key():
    path = os.path.join(BACKEND_DIR, ".env.example")
    content = open(path).read()
    assert "OPENAI_API_KEY" in content


def test_art_of_war_text_exists_and_nonempty():
    path = os.path.join(BACKEND_DIR, "data", "art_of_war_giles.txt")
    assert os.path.isfile(path), "art_of_war_giles.txt not found in data/"
    content = open(path).read()
    assert len(content) > 10_000, f"File too short: {len(content)} chars"


def test_character_py_exports_prompts():
    import character
    assert hasattr(character, "GENERATOR_SYSTEM_PROMPT")
    assert hasattr(character, "CLASSIFIER_SYSTEM_PROMPT")
    assert len(character.GENERATOR_SYSTEM_PROMPT.strip()) > 0
    assert len(character.CLASSIFIER_SYSTEM_PROMPT.strip()) > 0
