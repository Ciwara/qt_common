#!/usr/bin/env python
# -*- coding: utf8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu
# maintainer: Fad

from .cstatic import logger
from .models import init_database


class AdminFixture:
    """Classe de base pour l'initialisation des données de base (fixtures)"""
    
    def __init__(self):
        """Initialise la classe AdminFixture"""
        logger.debug("Initialisation de AdminFixture")
        
        # S'assurer que la base de données est initialisée
        init_database()
        
        # Initialiser les données de base
        self.init_fixtures()
    
    def init_fixtures(self):
        """Méthode à surcharger dans les classes filles pour initialiser les données spécifiques"""
        logger.debug("Initialisation des fixtures de base")
        # Cette méthode peut être surchargée dans les classes filles
        # pour ajouter des données initiales spécifiques à l'application
        pass

