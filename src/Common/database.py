#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Autor: Fadiga

from datetime import datetime

from playhouse import migrate as migrate_
from playhouse.migrate import CharField  # ForeignKeyField,
from playhouse.migrate import BooleanField, DateTimeField, IntegerField, migrate

from .cstatic import logger
from .models import (
    FileJoin,
    History,
    License,
    Organization,
    Owner,
    Settings,
    Version,
    migrator,
)

logger.info("Chargement du module database")


class AdminDatabase(object):
    LIST_CREAT = [History, Owner, Organization, Settings, License, Version, FileJoin]
    CREATE_DB = True
    field = migrate_.ForeignKeyField(
        Organization, field=Organization.id, null=True, on_delete="SET NULL"
    )
    LIST_MIGRATE = [
        ("License", "organization", field),
        ("License", "is_syncro", BooleanField(default=True)),
        ("License", "evaluation", BooleanField(default=True)),
        ("License", "last_update_date", DateTimeField(default=datetime.now)),
        ("History", "last_update_date", DateTimeField(default=datetime.now)),
        ("History", "is_syncro", BooleanField(default=True)),
        ("Organization", "logo_orga", CharField(null=True)),
        ("Organization", "slug", CharField(null=True)),
        ("Organization", "last_update_date", DateTimeField(default=datetime.now)),
        ("Organization", "is_syncro", BooleanField(default=True)),
        ("Version", "is_syncro", BooleanField(default=True)),
        ("Version", "last_update_date", DateTimeField(default=datetime.now)),
        ("Owner", "is_syncro", BooleanField(default=True)),
        ("Owner", "last_update_date", DateTimeField(default=datetime.now)),
        ("Settings", "toolbar", BooleanField(default=True)),
        ("Settings", "last_update_date", DateTimeField(default=datetime.now)),
        ("Settings", "is_syncro", BooleanField(default=True)),
        ("Settings", "toolbar_position", CharField(default=Settings.LEFT)),
        ("Settings", "devise", CharField(null=True)),
        ("Settings", "after_cam", IntegerField(default=0)),
        ("FileJoin", "last_update_date", DateTimeField(default=datetime.now)),
        ("FileJoin", "is_syncro", BooleanField(default=True)),
    ]

    MIG_VERSION = 1

    def __init__(self):
        logger.debug("Initialisation de AdminDatabase")

    def create_all_or_pass(self, drop_tables=False):
        logger.info("Début de la création/mise à jour de la base de données")
        did_create = False
        for model in self.LIST_CREAT:
            if drop_tables:
                logger.warning(f"Suppression de la table {model.__name__}")
                model.drop_table()
            if not model.table_exists():
                logger.info(f"Création de la table {model.__name__}")
                model.create_table()
                did_create = True

        if did_create:
            logger.info("Initialisation des données de base")
            try:
                from .fixture import FixtInit
                FixtInit().create_all_or_pass()
            except ImportError as e:
                logger.error(f"Erreur lors de l'importation de FixtInit: {e}")
            except Exception as e:
                logger.error(f"Erreur lors de l'initialisation des données: {e}")
        self.make_migrate()
        logger.info("Base de données initialisée avec succès")

    def make_migrate(self, db_v=1):
        logger.info("Début de la migration de la base de données")
        try:
            version = Version.get_or_none(Version.id == db_v)
            number = version.number
            logger.debug(f"Version actuelle de la base de données: {number}")
        except Exception as e:
            logger.warning(f"Erreur lors de la récupération de la version: {e}")
            number = 0
            version = Version()
        
        count_list = len(self.LIST_MIGRATE)
        logger.info(f"Nombre de migrations à effectuer: {count_list}")
        
        if count_list != number:
            for x, y, z in self.LIST_MIGRATE:
                try:
                    logger.debug(f"Migration de {x}.{y}")
                    migrate(migrator.add_column(x, y, z))
                    logger.info(f"Migration réussie: {x}.{y}")
                except Exception as e:
                    logger.error(f"Erreur lors de la migration de {x}.{y}: {e}")

            version.number = count_list
            version.save()
            logger.info(f"Base de données migrée vers la version {count_list}")
        else:
            logger.info("Base de données déjà à jour") 