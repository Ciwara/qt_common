#!/usr/bin/env python
# -*- coding: utf-8 -*-
# maintainer: Fad

"""Ajoute la colonne uuid à organization et renseigne les lignes existantes."""

import uuid

import peewee
from playhouse.migrate import SqliteMigrator, migrate as playhouse_migrate

from Common.cstatic import logger
from Common.models import Organization, dbh


def _has_column(table, column):
    rows = dbh.execute_sql("PRAGMA table_info({})".format(table)).fetchall()
    return any(row[1] == column for row in rows)


def _has_index(name):
    rows = dbh.execute_sql(
        "SELECT 1 FROM sqlite_master WHERE type='index' AND name=?",
        (name,),
    ).fetchall()
    return bool(rows)


def _drop_index_if_exists(name):
    if _has_index(name):
        dbh.execute_sql('DROP INDEX IF EXISTS "{}"'.format(name))
        logger.info("Index orphelin {} supprimé".format(name))


def migrate():
    try:
        if dbh is None or dbh.is_closed():
            logger.error("Base de données non connectée")
            return False

        # DDL SQLite : hors transaction atomique stricte (évite un index
        # créé puis une colonne absente après rollback partiel).
        index_name = "organization_uuid"

        if not _has_column("organization", "uuid"):
            # Ancien échec possible : index unique déjà créé sans colonne.
            _drop_index_if_exists(index_name)
            migrator = SqliteMigrator(dbh)
            # Sans unique=True : l'index est créé après le backfill.
            playhouse_migrate(
                migrator.add_column(
                    "organization",
                    "uuid",
                    peewee.CharField(max_length=36, null=True),
                )
            )
            logger.info("Colonne organization.uuid ajoutée")

        for org in Organization.select():
            if not org.uuid:
                org.uuid = str(uuid.uuid4())
                org.save()

        if not _has_index(index_name):
            dbh.execute_sql(
                'CREATE UNIQUE INDEX "{}" ON "organization" ("uuid")'.format(index_name)
            )
            logger.info("Index unique organization.uuid créé")

        logger.info("Migration organization uuid terminée")
        return True
    except Exception as e:
        logger.error("Échec migration organization uuid: {}".format(e))
        return False
