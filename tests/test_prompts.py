import pytest

from app.prompts import DEFAULT_VERSION, PROMPTs, get_prompt

def test_get_prompt_returns_known_vesion():
    assert get_prompt("v1") == PROMPTs["v1"]
    
def test_default_version_exists():
    assert DEFAULT_VERSION in PROMPTs
    
def test_unknown_version_raises():
    with pytest.raises(ValueError):
        get_prompt("v999")
        