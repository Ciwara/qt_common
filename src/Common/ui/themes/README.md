# Système de Thèmes v2.0 - Architecture Centralisée

## 🎯 Vue d'ensemble

Le système de thèmes v2.0 est une refonte complète qui centralise toute la gestion des thèmes dans un seul dossier avec une API unifiée et simplifiée.

## 📁 Structure du dossier

```
src/Common/ui/themes/
├── __init__.py         # API publique et exports
├── config.py           # Configuration centralisée des thèmes
├── styles.py           # Génération des styles CSS
├── manager.py          # Gestionnaire principal
├── legacy.py           # Ancien système (compatibilité)
├── legacy_manager.py   # Ancien gestionnaire (compatibilité)
├── legacy_modern.py    # Anciens styles modernes (compatibilité)
└── README.md           # Cette documentation
```

## 🎨 Thèmes disponibles

Le système inclut 5 thèmes prêts à l'emploi :

| Thème | Nom d'affichage | Type | Catégorie |
|-------|----------------|------|-----------|
| `default` | Défaut | ☀️ Clair | Basique |
| `light_modern` | Moderne Clair | ☀️ Clair | Moderne |
| `dark_modern` | Moderne Sombre | 🌙 Sombre | Moderne |
| `blue_professional` | Professionnel Bleu | ☀️ Clair | Professionnel |
| `green_nature` | Nature Verte | ☀️ Clair | Coloré |

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
manager.apply_theme_to_application("light_modern")
```

## ✅ Résumé des améliorations

- **✅ Centralisé** : Tout dans un seul dossier `/themes/`
- **✅ Unifié** : API cohérente avec ThemeManager
- **✅ Nettoyé** : Plus de doublons ni de fichiers dispersés
- **✅ Simplifié** : Interface d'utilisation claire
- **✅ Extensible** : Ajout facile de nouveaux thèmes
- **✅ Compatible** : Garde la compatibilité avec l'ancien système
- **✅ Testé** : Script de test complet inclus

## 🧪 Test du système

Exécuter le test complet :

```bash
python test_themes_clean.py
```

---

**Système refactorisé et centralisé** - Tous les thèmes sont maintenant dans un seul endroit ! 