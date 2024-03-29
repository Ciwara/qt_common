#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Autor: Fadiga


from __future__ import unicode_literals, absolute_import, division, print_function


from datetime import datetime
from Common.models import (
    Owner,
    Organization,
    License,
    Version,
    FileJoin,
    History,
    Settings,
)
from playhouse import migrate as migrate_
from playhouse.migrate import (
    migrate,
    CharField,
    BooleanField,
    ForeignKeyField,
    IntegerField,
    DateTimeField,
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
        # print("all or pass")
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

    def make_migrate(self):
        try:
            version = Version.get_or_none(Version.id == 1)
            number = version.number
        except:
            number = 0
            version = Version()
        count_list = len(self.LIST_MIGRATE)
        print("--check migrate--")
        if count_list != number:
            from Common.models import migrator

            print("Make migrate", self.LIST_MIGRATE)
            for x, y, z in self.LIST_MIGRATE:
                try:
                    migrate(migrator.add_column(x, y, z))
                    print(x, " : ", y)
                except Exception as e:
                    print(e)

            version.number = count_list
            version.save()
