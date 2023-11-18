#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Autor: Fadiga


from __future__ import absolute_import, division, print_function, unicode_literals

from datetime import datetime

from playhouse import migrate as migrate_
from playhouse.migrate import (
    BooleanField,
    CharField,
    DateTimeField,
    ForeignKeyField,
    IntegerField,
    migrate,
)

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

    def create_all_or_pass(self, drop_tables=False):
        did_create = False
        for model in self.LIST_CREAT:
            if drop_tables:
                model.drop_table()
            if not model.table_exists():
                model.create_table()
                did_create = True

        if did_create:
            print("---- database -----")
            from fixture import FixtInit

            FixtInit().create_all_or_pass()
        self.make_migrate()

    def make_migrate(self, db_v=1):
        try:
            version = Version.get_or_none(Version.id == db_v)
            number = version.number
        except:
            number = 0
            version = Version()
        count_list = len(self.LIST_MIGRATE)
        print("--check migrate--")
        if count_list != number:
            for x, y, z in self.LIST_MIGRATE:
                try:
                    migrate(migrator.add_column(x, y, z))
                    print(x, " : ", y)
                except Exception as e:
                    print(e)

            version.number = count_list
            version.save()
