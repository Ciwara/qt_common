#!/usr/bin/env python
# -*- coding: utf-8 -*-
# maintainer: Fad

import os
import sys
import peewee
from datetime import datetime

# Ajouter le répertoire parent au chemin Python
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from Common.cstatic import logger
from Common.models import dbh

__all__ = ['MigrationTracker']

class MigrationTracker(peewee.Model):
    """Modèle pour suivre les migrations appliquées"""
    class Meta:
        database = dbh
        table_name = 'migration_tracker'

    migration_name = peewee.CharField(unique=True)
    applied_at = peewee.DateTimeField(default=datetime.now)
    status = peewee.CharField(default='pending')  # pending, success, failed
    error_message = peewee.TextField(null=True)

    @classmethod
    def create_table(cls, safe=True):
        """Crée la table de suivi des migrations si elle n'existe pas"""
        try:
            # Vérifier si la table existe déjà
            if cls.table_exists():
                logger.info("✅ Table de suivi des migrations existe déjà")
                return True
                
            super().create_table(safe=safe)
            logger.info("✅ Table de suivi des migrations créée")
            return True
        except Exception as e:
            logger.error(f"❌ Erreur lors de la création de la table de suivi: {e}")
            raise

    @classmethod
    def is_migration_applied(cls, migration_name):
        """Vérifie si une migration a déjà été appliquée"""
        try:
            if not cls.table_exists():
                logger.warning("⚠️ Table de suivi des migrations n'existe pas")
                return False
                
            return cls.select().where(
                cls.migration_name == migration_name,
                cls.status == 'success'
            ).exists()
        except Exception as e:
            logger.error(f"❌ Erreur lors de la vérification de la migration {migration_name}: {e}")
            return False

    @classmethod
    def mark_migration_applied(cls, migration_name, status='success', error_message=None):
        """Marque une migration comme appliquée"""
        try:
            if not cls.table_exists():
                logger.warning("⚠️ Table de suivi des migrations n'existe pas")
                return False
                
            migration, created = cls.get_or_create(
                migration_name=migration_name,
                defaults={
                    'status': status,
                    'error_message': error_message
                }
            )
            
            if not created:
                migration.status = status
                migration.error_message = error_message
                migration.save()
                
            logger.info(f"✅ Migration {migration_name} marquée comme {status}")
            return True
                
        except Exception as e:
            logger.error(f"❌ Erreur lors du marquage de la migration {migration_name}: {e}")
            return False

    @classmethod
    def get_pending_migrations(cls, all_migrations):
        """Récupère la liste des migrations en attente"""
        try:
            if not cls.table_exists():
                logger.warning("⚠️ Table de suivi des migrations n'existe pas")
                return all_migrations
                
            applied = {m.migration_name for m in cls.select().where(cls.status == 'success')}
            return [m for m in all_migrations if m not in applied]
        except Exception as e:
            logger.error(f"❌ Erreur lors de la récupération des migrations en attente: {e}")
            return all_migrations

    @classmethod
    def migrate(cls):
        """Exécute la migration pour créer la table de suivi"""
        try:
            # Vérifier la connexion à la base de données
            if dbh is None or dbh.is_closed():
                logger.error("❌ La base de données n'est pas connectée")
                return False
                
            with dbh.atomic():
                if cls.create_table():
                    logger.info("✅ Migration de la table de suivi terminée avec succès")
                    return True
                else:
                    logger.error("❌ Échec de la création de la table de suivi")
                    return False
        except Exception as e:
            logger.error(f"❌ Erreur lors de la migration de la table de suivi: {e}")
            return False