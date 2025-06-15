#!/usr/bin/env python
# -*- coding: utf-8 -*-
# maintainer: Fad

import sys
from pathlib import Path

# Ajout du répertoire src au PYTHONPATH
src_path = Path(__file__).parent / 'src'
sys.path.insert(0, str(src_path))  # Utilisation de insert(0, ...) pour prioriser notre src

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication

# Import QtWebEngineWidgets avant la création de QApplication
try:
    from PyQt5.QtWebEngineWidgets import QWebEngineView
except ImportError:
    pass

# Définir l'attribut Qt.AA_ShareOpenGLContexts avant la création de QApplication
QApplication.setAttribute(Qt.AA_ShareOpenGLContexts)

# Créer l'application Qt
app = QApplication(sys.argv)
app.setAttribute(Qt.AA_EnableHighDpiScaling)
app.setAttribute(Qt.AA_UseHighDpiPixmaps)

if __name__ == "__main__":
    try:
        # Importer les modules après la création de QApplication
        from Common.cmain import cmain
        from Common.cstatic import logger
        from Common.models import init_database
        
        # Initialiser la base de données
        logger.info("🔧 Initialisation de la base de données...")
        if init_database():
            logger.info("✅ Base de données initialisée avec succès")
        else:
            logger.error("❌ Erreur lors de l'initialisation de la base de données")
            sys.exit(1)
        
        # Lancer l'application
        logger.info("Lancement de l'application")
        cmain(test=True)
        
        logger.info("Lancement de la boucle d'événements")
        sys.exit(app.exec_())
    except Exception as e:
        logger.error(f"Erreur lors de l'exécution de l'application: {e}")
        sys.exit(1)
