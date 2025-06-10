#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Module utilitaire pour la gestion optimisée des polices selon le système d'exploitation.
Évite les warnings Qt et améliore les performances.
"""

import platform
from PyQt5.QtGui import QFont, QFontDatabase
from PyQt5.QtWidgets import QApplication


class FontManager:
    """Gestionnaire de polices optimisé pour éviter les warnings Qt"""
    
    _system_fonts = None
    _preferred_font_family = None
    
    @classmethod
    def get_system_info(cls):
        """Retourne les informations système pour le choix des polices"""
        return {
            'system': platform.system(),
            'version': platform.version(),
            'machine': platform.machine()
        }
    
    @classmethod
    def get_available_fonts(cls):
        """Retourne la liste des polices disponibles sur le système"""
        if cls._system_fonts is None:
            font_db = QFontDatabase()
            cls._system_fonts = font_db.families()
        return cls._system_fonts
    
    @classmethod
    def get_preferred_font_family(cls):
        """Retourne la famille de police préférée selon le système"""
        if cls._preferred_font_family is not None:
            return cls._preferred_font_family
            
        system = platform.system()
        available_fonts = cls.get_available_fonts()
        
        # Définir les priorités de polices selon le système
        if system == "Darwin":  # macOS
            priority_fonts = [
                "Helvetica Neue",
                "Helvetica",
                "Arial"
            ]
        elif system == "Windows":
            priority_fonts = [
                "Segoe UI",
                "Calibri",
                "Arial",
                "Tahoma"
            ]
        else:  # Linux et autres
            priority_fonts = [
                "Ubuntu",
                "Noto Sans",
                "DejaVu Sans",
                "Liberation Sans",
                "Arial",
                "Helvetica"
            ]
        
        # Trouver la première police disponible
        for font in priority_fonts:
            if font in available_fonts:
                cls._preferred_font_family = font
                return font
        
        # Fallback vers la police par défaut du système
        cls._preferred_font_family = "sans-serif"
        return "sans-serif"
    
    @classmethod
    def get_font_fallback_string(cls):
        """Retourne une chaîne CSS avec les polices de fallback optimisées"""
        system = platform.system()
        
        if system == "Darwin":  # macOS
            return '"Helvetica Neue", "Helvetica", "Arial", sans-serif'
        elif system == "Windows":
            return '"Segoe UI", "Calibri", "Arial", "Tahoma", sans-serif'
        else:  # Linux
            return '"Ubuntu", "Noto Sans", "DejaVu Sans", "Liberation Sans", "Arial", sans-serif'
    
    @classmethod
    def create_optimized_font(cls, size=10, weight=QFont.Normal):
        """Crée une police optimisée pour le système actuel"""
        font_family = cls.get_preferred_font_family()
        return QFont(font_family, size, weight)
    
    @classmethod
    def get_css_font_family(cls):
        """Retourne la déclaration CSS font-family optimisée"""
        return f'font-family: {cls.get_font_fallback_string()};'


def get_system_font():
    """Raccourci pour obtenir la police système optimale"""
    return FontManager.get_preferred_font_family()


def get_css_font_fallback():
    """Raccourci pour obtenir la chaîne CSS des polices de fallback"""
    return FontManager.get_font_fallback_string()


def create_system_font(size=10, weight=QFont.Normal):
    """Raccourci pour créer une police système optimisée"""
    return FontManager.create_optimized_font(size, weight)


def optimize_css_fonts(css_content):
    """Optimise le CSS en remplaçant les polices par celles adaptées au système"""
    import re
    
    # Remplacer toutes les occurrences de font-family avec Segoe UI
    segoe_pattern = r'font-family:\s*"Segoe\s+UI"[^;]*;'
    optimized_font_family = FontManager.get_css_font_family()
    
    # Remplacer les patterns complets
    css_content = re.sub(segoe_pattern, optimized_font_family, css_content)
    
    return css_content


def log_font_info():
    """Affiche les informations de police pour debug"""
    print(f"🖥️  Système: {platform.system()}")
    print(f"📝 Police préférée: {FontManager.get_preferred_font_family()}")
    print(f"🔤 Fallback CSS: {FontManager.get_font_fallback_string()}")
    print(f"📊 Polices disponibles: {len(FontManager.get_available_fonts())}")


# Test des fonctions si exécuté directement
if __name__ == "__main__":
    app = QApplication([])
    log_font_info()
    
    # Test de création de police
    test_font = create_system_font(12, QFont.Bold)
    print(f"🧪 Police de test créée: {test_font.family()} - {test_font.pointSize()}pt")
    
    app.quit() 