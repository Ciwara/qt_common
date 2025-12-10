# Système de Thèmes v2.0 - Architecture Centralisée

## 🎯 Vue d'ensemble

Le système de thèmes v2.0 est une refonte complète qui centralise toute la gestion des thèmes dans un seul dossier avec une API unifiée et simplifiée.

## 📁 Structure du dossier

```text
src/Common/ui/themes/
├── __init__.py         # API publique et exports
├── config.py           # Configuration centralisée des thèmes
├── styles.py           # Génération des styles CSS
├── manager.py          # Gestionnaire principal
└── README.md           # Cette documentation
```

## 🎨 Thèmes disponibles

Le système inclut 3 thèmes prêts à l'emploi :

| Thème | Nom d'affichage | Type | Catégorie |
|-------|----------------|------|-----------|
| `system` | Thème Système | ☀️/🌙 Dynamique | Système |
| `light_modern` | Moderne Clair | ☀️ Clair | Moderne |
| `dark_modern` | Moderne Sombre | 🌙 Sombre | Moderne |

Le thème `system` suit automatiquement les préférences système (clair ou sombre).

## 🚀 Utilisation rapide

### Import de base

```python
from Common.ui.themes import (
    ThemeManager,
    get_available_themes,
    get_current_theme,
    set_current_theme
)
```

### Utilisation du gestionnaire

```python
# Créer une instance du gestionnaire
manager = ThemeManager()

# Obtenir le thème actuel
current = manager.get_current_theme()

# Changer de thème
manager.set_theme("dark_modern")

# Appliquer le thème à l'application Qt
manager.apply_theme_to_application("light_modern")  # ou "dark_modern" ou "system"
```

## ✅ Résumé des améliorations

- **✅ Centralisé** : Tout dans un seul dossier `/themes/`
- **✅ Unifié** : API cohérente avec ThemeManager
- **✅ Nettoyé** : Seulement 2 thèmes (clair et sombre) + mode système
- **✅ Simplifié** : Interface d'utilisation claire
- **✅ Mode sombre** : Support complet du thème sombre
- **✅ Mode système** : Détection automatique du mode clair/sombre du système 