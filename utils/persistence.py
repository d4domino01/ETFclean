"""
Data Persistence Module
Saves and loads app state to JSON so settings survive app refreshes
"""

import json
import os
from datetime import datetime
from pathlib import Path

PERSISTENCE_FILE = "app_state.json"
PRICE_HISTORY_FILE = "price_history.json"


def save_holdings(holdings):
    """Save portfolio holdings to file"""
    try:
        data = {
            "holdings": holdings,
            "last_saved": datetime.now().isoformat()
        }
        with open(PERSISTENCE_FILE, 'w') as f:
            json.dump(data, f, indent=2, default=str)
    except Exception as e:
        print(f"Error saving holdings: {e}")


def load_holdings():
    """Load portfolio holdings from file"""
    try:
        if os.path.exists(PERSISTENCE_FILE):
            with open(PERSISTENCE_FILE, 'r') as f:
                data = json.load(f)
                return data.get("holdings", {})
    except Exception as e:
        print(f"Error loading holdings: {e}")
    return {}


def save_price_history(price_history):
    """Save historical prices to file"""
    try:
        data = {
            "price_history": price_history,
            "last_saved": datetime.now().isoformat()
        }
        with open(PRICE_HISTORY_FILE, 'w') as f:
            json.dump(data, f, indent=2, default=str)
    except Exception as e:
        print(f"Error saving price history: {e}")


def load_price_history():
    """Load historical prices from file"""
    try:
        if os.path.exists(PRICE_HISTORY_FILE):
            with open(PRICE_HISTORY_FILE, 'r') as f:
                data = json.load(f)
                return data.get("price_history", {})
    except Exception as e:
        print(f"Error loading price history: {e}")
    return {}


def save_settings(settings):
    """Save app settings to file"""
    try:
        data = {
            "settings": settings,
            "last_saved": datetime.now().isoformat()
        }
        with open("app_settings.json", 'w') as f:
            json.dump(data, f, indent=2, default=str)
    except Exception as e:
        print(f"Error saving settings: {e}")


def load_settings():
    """Load app settings from file"""
    try:
        if os.path.exists("app_settings.json"):
            with open("app_settings.json", 'r') as f:
                data = json.load(f)
                return data.get("settings", {})
    except Exception as e:
        print(f"Error loading settings: {e}")
    return {}


def get_last_saved_time():
    """Get when data was last saved"""
    try:
        if os.path.exists(PERSISTENCE_FILE):
            with open(PERSISTENCE_FILE, 'r') as f:
                data = json.load(f)
                return data.get("last_saved", "Never")
    except:
        pass
    return "Never"


def clear_persistence():
    """Clear all saved data"""
    try:
        for file in [PERSISTENCE_FILE, PRICE_HISTORY_FILE, "app_settings.json"]:
            if os.path.exists(file):
                os.remove(file)
        return True
    except Exception as e:
        print(f"Error clearing data: {e}")
        return False
