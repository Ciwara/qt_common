#!/usr/bin/env python
# -*- coding: utf8 -*-
"""
Module de gestion dynamique des thèmes - Version 3.0
Fournit la liste complète des 10 thèmes ultra-modernes disponibles
"""

def get_all_themes_dynamic():
    """
    🎨 LISTE COMPLÈTE DES THÈMES ULTRA-MODERNES
    
    Returns:
        dict: Dictionnaire complet {theme_key: description_française}
    """
    return {
        # === THÈMES DE BASE MODERNES ===
        "light_modern": "🌟 Moderne Clair",
        "dark_modern": "🌙 Moderne Sombre",
        
        # === THÈMES PROFESSIONNELS ===
        "professional_blue": "💼 Professionnel Bleu",
        "nature_green": "🌿 Nature Verte",
        
        # === THÈMES CRÉATIFS ===
        "warm_orange": "🔥 Chaleureux Orange", 
        "creative_purple": "🎨 Créatif Violet",
        
        # === THÈMES RÉVOLUTIONNAIRES ===
        "glassmorphism": "💎 Glassmorphism",
        "neumorphism": "🎯 Neumorphism",
        "cyberpunk_neon": "⚡ Cyberpunk Néon",
        
        # === THÈME SYSTÈME ===
        "default": "📋 Défaut Système"
    }

def get_themes_by_category():
    """
    📂 Thèmes organisés par catégories
    
    Returns:
        dict: Thèmes classés par catégories
    """
    return {
        "🎯 Modernes": [
            ("light_modern", "🌟 Moderne Clair"),
            ("dark_modern", "🌙 Moderne Sombre")
        ],
        "💼 Professionnels": [
            ("professional_blue", "💼 Professionnel Bleu"),
            ("nature_green", "🌿 Nature Verte")
        ],
        "🎨 Créatifs": [
            ("warm_orange", "🔥 Chaleureux Orange"),
            ("creative_purple", "🎨 Créatif Violet")
        ],
        "🚀 Révolutionnaires": [
            ("glassmorphism", "💎 Glassmorphism"),
            ("neumorphism", "🎯 Neumorphism"),
            ("cyberpunk_neon", "⚡ Cyberpunk Néon")
        ],
        "⚙️ Système": [
            ("default", "📋 Défaut Système")
        ]
    }

def get_themes_count():
    """
    📊 Statistiques des thèmes
    
    Returns:
        dict: Statistiques complètes
    """
    all_themes = get_all_themes_dynamic()
    categories = get_themes_by_category()
    
    return {
        "total_themes": len(all_themes),
        "total_categories": len(categories),
        "modern_themes": 2,
        "professional_themes": 2,
        "creative_themes": 2,
        "revolutionary_themes": 3,
        "system_themes": 1
    }

def get_theme_preview_colors():
    """
    🎨 Couleurs de prévisualisation pour chaque thème
    
    Returns:
        dict: Couleurs primaires par thème
    """
    return {
        "light_modern": "#0d6efd",
        "dark_modern": "#0d6efd", 
        "professional_blue": "#1e40af",
        "nature_green": "#059669",
        "warm_orange": "#ea580c",
        "creative_purple": "#7c3aed",
        "glassmorphism": "#667eea",
        "neumorphism": "#9ca3af",
        "cyberpunk_neon": "#00ffff",
        "default": "#6c757d"
    }

def is_theme_available(theme_key: str) -> bool:
    """
    ✅ Vérifie si un thème est disponible
    
    Args:
        theme_key (str): Clé du thème à vérifier
        
    Returns:
        bool: True si le thème existe
    """
    return theme_key in get_all_themes_dynamic()

def get_theme_display_name(theme_key: str) -> str:
    """
    📝 Obtient le nom d'affichage d'un thème
    
    Args:
        theme_key (str): Clé du thème
        
    Returns:
        str: Nom d'affichage avec emoji
    """
    themes = get_all_themes_dynamic()
    return themes.get(theme_key, f"❓ Thème Inconnu ({theme_key})")

def get_themes_for_menu():
    """
    📋 Format optimisé pour les menus déroulants
    
    Returns:
        list: Liste de tuples (key, display_name, color)
    """
    themes = get_all_themes_dynamic()
    colors = get_theme_preview_colors()
    
    menu_items = []
    for theme_key, display_name in themes.items():
        color = colors.get(theme_key, "#6c757d")
        menu_items.append((theme_key, display_name, color))
    
    return menu_items

def print_themes_summary():
    """
    📊 Affiche un résumé complet des thèmes disponibles
    """
    print("=" * 60)
    print("🎨 SYSTÈME DE THÈMES ULTRA-MODERNES - VERSION 3.0")
    print("=" * 60)
    
    stats = get_themes_count()
    print(f"📊 STATISTIQUES:")
    print(f"   • Total des thèmes: {stats['total_themes']}")
    print(f"   • Catégories: {stats['total_categories']}")
    print(f"   • Thèmes révolutionnaires: {stats['revolutionary_themes']}")
    print()
    
    categories = get_themes_by_category()
    for category, themes in categories.items():
        print(f"{category}:")
        for theme_key, display_name in themes:
            color = get_theme_preview_colors()[theme_key]
            print(f"   • {display_name} ({theme_key}) - {color}")
        print()
    
    print("=" * 60)

# Exemple d'utilisation
if __name__ == "__main__":
    print_themes_summary() 