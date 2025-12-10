#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Application d'exemple pour tester les fonctionnalités du module Common
Utilise cmain() pour démarrer l'application

Auteur: Fad
Version: 1.0
"""

import sys
from pathlib import Path

# Ajout du répertoire src au PYTHONPATH
src_path = Path(__file__).parent / 'src'
sys.path.insert(0, str(src_path))

def main():
    """
    Fonction principale - Lance l'application avec le module Common
    
    Cette fonction :
    - Initialise l'application PyQt5 via cmain()
    - Affiche la fenêtre principale du module Common
    - Gère toutes les initialisations nécessaires (BDD, migrations, etc.)
    """
    print("=" * 60)
    print("🚀 Application d'exemple - Module Common")
    print("=" * 60)
    print()
    print("📝 Fonctionnalités testées :")
    print("   ✅ Base de données SQLite")
    print("   ✅ Migrations automatiques")
    print("   ✅ Interface utilisateur")
    print("   ✅ Gestion des utilisateurs et organisations")
    print()
    print("-" * 60)
    print()
    
    try:
        # Import du module cmain qui gère toute l'initialisation
        from Common.cmain import cmain
        from Common.cstatic import logger
        
        # Affichage des informations de démarrage
        logger.info("=" * 60)
        logger.info("🚀 Démarrage de l'application d'exemple")
        logger.info("=" * 60)
        
        # Lancer l'application en mode test (pour bypasser les vérifications de licence/login)
        # cmain(test=True) permet de démarrer directement sans authentification
        print("⚙️  Initialisation de l'application...")
        print("   → Initialisation de la base de données...")
        print()
        
        # Lancer l'application
        # Le paramètre test=True permet de démarrer sans les vérifications
        # d'authentification, licence, etc. pour faciliter les tests
        exit_code = cmain(test=True)
        
        if exit_code:
            logger.info("✅ Application fermée normalement")
            print()
            print("✅ Application fermée avec succès")
        else:
            logger.warning("⚠️ Application fermée avec des avertissements")
            print()
            print("⚠️ Application fermée (voir les logs pour plus de détails)")
            
        return exit_code
        
    except KeyboardInterrupt:
        print()
        print("⚠️ Application interrompue par l'utilisateur")
        logger.warning("Application interrompue par l'utilisateur")
        return 1
        
    except ImportError as e:
        print()
        print("❌ Erreur d'import:", str(e))
        print()
        print("💡 Vérifiez que :")
        print("   - Le répertoire 'src' contient le module Common")
        print("   - Toutes les dépendances sont installées (PyQt5, etc.)")
        print("   - Vous êtes dans le bon répertoire")
        return 1
        
    except Exception as e:
        print()
        print(f"❌ Erreur lors du démarrage: {e}")
        logger.error(f"Erreur lors du démarrage: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    """
    Point d'entrée principal de l'application d'exemple
    
    Pour lancer l'application :
        python app_example.py
    
    L'application utilisera automatiquement :
    - La base de données locale (database.db)
    - Toutes les fonctionnalités du module Common
    """
    exit_code = main()
    sys.exit(exit_code)

