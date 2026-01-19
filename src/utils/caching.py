"""
Caching utility functions
"""

import os
import pickle
from pathlib import Path
from src.config.settings import PROCESSED_DIR, ENABLE_CACHING


def get_cache_path(cache_type: str, identifier: str) -> Path:
    """Get cache file path."""
    cache_dir = Path(PROCESSED_DIR) / cache_type
    cache_dir.mkdir(parents=True, exist_ok=True)
    return cache_dir / f"{identifier}.pkl"


def save_to_cache(data, cache_type: str, identifier: str):
    """Save data to cache."""
    if not ENABLE_CACHING:
        return
    
    cache_path = get_cache_path(cache_type, identifier)
    try:
        with open(cache_path, 'wb') as f:
            pickle.dump(data, f)
        print(f"  ✓ Cached to: {cache_path}")
    except Exception as e:
        print(f"  ⚠️  Cache save failed: {e}")


def load_from_cache(cache_type: str, identifier: str):
    """Load data from cache."""
    if not ENABLE_CACHING:
        return None
    
    cache_path = get_cache_path(cache_type, identifier)
    
    if not cache_path.exists():
        return None
    
    try:
        with open(cache_path, 'rb') as f:
            data = pickle.load(f)
        print(f"  ✓ Loaded from cache: {cache_path}")
        return data
    except Exception as e:
        print(f"  ⚠️  Cache load failed: {e}")
        return None