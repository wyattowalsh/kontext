"""
Configuration package for Kontext.

This package handles application configuration management
with YAML files and environment variable overrides.
"""

from .settings import AppConfig, load_config, save_config

__all__ = ['AppConfig', 'load_config', 'save_config']