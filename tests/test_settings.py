import json
import pytest
from genetinav.settings import (
    DEFAULT_SETTINGS,
    load_settings,
    save_settings,
    reset_settings
)

def test_load_settings_no_file(tmp_path):
    settings_path = tmp_path / "settings.json"
    settings = load_settings(settings_path)
    assert settings == DEFAULT_SETTINGS

def test_save_and_load_roundtrip(tmp_path):
    settings_path = tmp_path / "settings.json"
    
    custom_settings = DEFAULT_SETTINGS.copy()
    custom_settings["theme"] = "dark_mode"
    custom_settings["default_window_size"] = 100
    
    save_settings(custom_settings, settings_path)
    
    loaded = load_settings(settings_path)
    assert loaded["theme"] == "dark_mode"
    assert loaded["default_window_size"] == 100
    assert loaded == custom_settings

def test_load_missing_key_fills_default(tmp_path):
    settings_path = tmp_path / "settings.json"
    
    partial_data = {
        "theme": "cyberpunk",
        "unknown_key": "should_be_ignored"
    }
    with open(settings_path, "w", encoding="utf-8") as f:
        json.dump(partial_data, f)
        
    loaded = load_settings(settings_path)
    assert loaded["theme"] == "cyberpunk"
    assert loaded["high_contrast"] == DEFAULT_SETTINGS["high_contrast"]
    assert "unknown_key" not in loaded

def test_load_corrupted_file_returns_defaults(tmp_path):
    settings_path = tmp_path / "settings.json"
    
    with open(settings_path, "w", encoding="utf-8") as f:
        f.write("{invalid json format...")
        
    loaded = load_settings(settings_path)
    assert loaded == DEFAULT_SETTINGS

def test_reset_settings(tmp_path):
    settings_path = tmp_path / "settings.json"
    
    custom_settings = DEFAULT_SETTINGS.copy()
    custom_settings["theme"] = "something_else"
    save_settings(custom_settings, settings_path)
    
    reset = reset_settings(settings_path)
    assert reset == DEFAULT_SETTINGS
    
    with open(settings_path, "r", encoding="utf-8") as f:
        disk_data = json.load(f)
    assert disk_data == DEFAULT_SETTINGS
