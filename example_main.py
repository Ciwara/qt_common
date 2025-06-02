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

from Common.cmain import cmain
from Common.cstatic import logger

if __name__ == "__main__":
    try:
        app = QApplication(sys.argv)
        app.setAttribute(Qt.AA_EnableHighDpiScaling)
        app.setAttribute(Qt.AA_UseHighDpiPixmaps)
        
        logger.info("Lancement de l'application")
        cmain(test=True)
        
        logger.info("Lancement de la boucle d'événements")
        sys.exit(app.exec_())
    except Exception as e:
        logger.error(f"Erreur lors de l'exécution de l'application: {e}")
        sys.exit(1)
