import json
import pathlib
from copy import deepcopy
from typing import Any

DEFAULT_SETTINGS: dict[str, Any] = {
    "theme": "obsidian_helix",
    "high_contrast": False,
    "monochrome": False,
    "animations_enabled": True,
    "splash_animation_enabled": True,
    "transition_animation_enabled": True,
    "performance_mode": False,
    "history_enabled": True,
    "cache_enabled": True,
    "default_window_size": 60,
    "ruler_interval": 10,
    "coordinate_display_enabled": True,
    "default_species": "human",
    "auto_open_viewer": True,
    "show_summary_by_default": True,
    "remember_last_session": True,
    "last_gene": None,
    "launch_mode": "command"
}

def get_settings_path() -> pathlib.Path:
    path = pathlib.Path.home() / ".genetinav" / "settings.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    return path

def load_settings(path: pathlib.Path | None = None) -> dict[str, Any]:
    if path is None:
        path = get_settings_path()
        
    settings = deepcopy(DEFAULT_SETTINGS)
    
    if not path.exists():
        return settings
        
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            
        if not isinstance(data, dict):
            return settings
            
        for key in settings:
            if key in data:
                settings[key] = data[key]
                
    except (json.JSONDecodeError, OSError):
        pass
        
    return settings

def save_settings(settings: dict[str, Any], path: pathlib.Path | None = None) -> None:
    if path is None:
        path = get_settings_path()
        
    path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(path, "w", encoding="utf-8") as f:
        json.dump(settings, f, indent=2)

def reset_settings(path: pathlib.Path | None = None) -> dict[str, Any]:
    settings = deepcopy(DEFAULT_SETTINGS)
    save_settings(settings, path)
    return settings
