#!/usr/bin/env python
# -*- coding: utf8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu
# maintainer: Fad

from .models import dbh, init_database, BaseModel
from .cstatic import logger


class AdminDatabase:
    """Classe de base pour la gestion de la base de données et des migrations"""
    
    def __init__(self):
        """Initialise la classe AdminDatabase"""
        logger.debug("Initialisation de AdminDatabase")
        
        # Initialiser la base de données si ce n'est pas déjà fait
        if dbh is None:
            init_database()
        
        # Liste des modèles à créer
        self.LIST_CREAT = []
        
        # Liste des migrations à exécuter
        self.LIST_MIGRATE = []
    
    def create_all_or_pass(self):
        """Crée toutes les tables de LIST_CREAT si elles n'existent pas"""
        logger.info("Création des tables de l'application")
        
        # S'assurer que la base de données est initialisée
        if dbh is None:
            init_database()
        
        # S'assurer que la base de données est connectée
        if dbh.is_closed():
            dbh.connect()
        
        # Créer les tables pour tous les modèles dans LIST_CREAT
        if self.LIST_CREAT:
            logger.info(f"Création de {len(self.LIST_CREAT)} table(s)")
            for model in self.LIST_CREAT:
                # S'assurer que le modèle utilise la bonne base de données
                if model._meta.database is None:
                    model._meta.database = dbh
                logger.debug(f"Création de la table pour {model.__name__}")
            
            # Créer toutes les tables en une seule fois
            dbh.create_tables(self.LIST_CREAT, safe=True)
            logger.info("Tables créées avec succès")
        else:
            logger.warning("Aucune table à créer (LIST_CREAT est vide)")
        
        # Exécuter les migrations si nécessaire
        if self.LIST_MIGRATE:
            logger.info(f"Exécution de {len(self.LIST_MIGRATE)} migration(s)")
            # Les migrations seront gérées par le système de migration de peewee
            # Ici, on peut ajouter la logique de migration si nécessaire

