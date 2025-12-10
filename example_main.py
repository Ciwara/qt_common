#!/usr/bin/env python
# -*- coding: utf-8 -*-
# maintainer: Fad

"""
Exemple d'utilisation du module Common avec cmain()

⚠️ IMPORTANT: Ce fichier laisse cmain() gérer la création de QApplication
Ne créez PAS de QApplication avant d'appeler cmain() car cela causerait
une double création et des erreurs.
"""

import sys
from pathlib import Path

# Ajout du répertoire src au PYTHONPATH
src_path = Path(__file__).parent / 'src'
sys.path.insert(0, str(src_path))

if __name__ == "__main__":
    try:
        print("=" * 60)
        print("🚀 Exemple d'application - Module Common")
        print("=" * 60)
        print()
        
        # Importer le module cmain
        # cmain() crée et configure QApplication automatiquement
        from Common.cmain import cmain
        from Common.cstatic import logger
        
        print("⚙️  Lancement de l'application via cmain()...")
        print("   → Le thème système sera appliqué automatiquement")
        print("   → La base de données sera initialisée")
        print("   → Les migrations seront exécutées si nécessaire")
        print()
        
        # Lancer l'application
        # cmain(test=True) démarre en mode test (sans vérifications de licence/login)
        # cmain() retourne le code de sortie de app.exec_()
        exit_code = cmain(test=True)
        
        if exit_code:
            logger.info("✅ Application fermée normalement")
            print()
            print("✅ Application fermée avec succès")
        else:
            logger.warning("⚠️ Application fermée avec des avertissements")
            print()
            print("⚠️ Application fermée (voir les logs pour plus de détails)")
            
        sys.exit(exit_code if exit_code else 0)
        
    except KeyboardInterrupt:
        print()
        print("⚠️ Application interrompue par l'utilisateur")
        sys.exit(1)
        
    except ImportError as e:
        print()
        print(f"❌ Erreur d'import: {e}")
        print()
        print("💡 Vérifiez que :")
        print("   - Le répertoire 'src' contient le module Common")
        print("   - Toutes les dépendances sont installées")
        print("   - Vous êtes dans le bon répertoire")
        sys.exit(1)
        
    except Exception as e:
        print()
        print(f"❌ Erreur lors de l'exécution: {e}")
        try:
            logger.error(f"Erreur lors de l'exécution: {e}", exc_info=True)
        except:
            pass
        sys.exit(1)
