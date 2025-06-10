#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Package des thèmes pour l'application Qt
Centralise toute la gestion des thèmes en un seul endroit
"""

# Imports principaux pour l'API publique
from .config import (
    ThemeConfig,
    get_available_themes,
    is_theme_dark,
    theme_exists,
    get_current_theme,
    set_current_theme
)

from .manager import (
    ThemeManager,
    apply_theme_to_application,
    apply_theme_immediately,
    get_theme_manager
)
from .styles import get_theme_style

# Version du système de thèmes
__version__ = "2.0.0"

# API publique du package
__all__ = [
    'ThemeConfig',
    'ThemeManager', 
    'get_available_themes',
    'is_theme_dark',
    'theme_exists',
    'get_current_theme',
    'set_current_theme',
    'get_theme_style',
    'apply_theme_to_application',
    'apply_theme_immediately',
    'get_theme_manager',
] 