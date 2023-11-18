#!/usr/bin/env python
# -*- coding: utf8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu
# maintainer: Fad
from __future__ import absolute_import, division, print_function, unicode_literals

import hashlib
import os
import time

# from peewee_migrate import Router
from datetime import datetime, timedelta

import peewee
from playhouse.migrate import (
    BooleanField,
    CharField,
    DateTimeField,
    SqliteMigrator,
    migrate,
)

from .ui.util import copy_file, date_to_str, datetime_to_str

DB_FILE = "database.db"

print("Peewee version : " + peewee.__version__)

NOW = datetime.now()

dbh = peewee.SqliteDatabase(DB_FILE)
migrator = SqliteMigrator(dbh)


class BaseModel(peewee.Model):
    class Meta:
        database = dbh

    is_syncro = BooleanField(default=False)
    last_update_date = DateTimeField(default=NOW)

    def updated(self):
        self.is_syncro = True
        self.last_update_date = NOW
        self.save()

    def save_(self):
        self.is_syncro = False
        self.save()

    def data(self):
        return {
            "is_syncro": self.is_syncro,
            "last_update_date": datetime_to_str(self.last_update_date),
        }

    @classmethod
    def all(cls):
        return list(cls.select())


class FileJoin(BaseModel):
    DEST_FILES = "Files"

    class Meta:
        ordering = ("file_name", "desc")
        # db_table = 'file_join'

    file_name = peewee.CharField(max_length=200, null=True)
    file_slug = peewee.CharField(max_length=200, null=True, unique=True)
    on_created = peewee.DateTimeField(default=NOW)

    def data(self):
        return {
            "file_name": self.file_name,
            "file_slug": self.file_slug,
            "on_created": date_to_str(self.on_created),
            "is_syncro": self.is_syncro,
            "last_update_date": datetime_to_str(self.last_update_date),
        }

    def __str__(self):
        return "{} {}".format(self.file_name, self.file_slug)

    def save(self):
        self.file_slug = copy_file(self.DEST_FILES, self.file_slug)
        super(FileJoin, self).save()

    def display_name(self):
        return "{}".format(self.file_name)

    @property
    def get_file(self):
        return os.path.join(
            os.path.join(os.path.dirname(os.path.abspath("__file__")), self.DEST_FILES),
            self.file_slug,
        )

    def show_file(self):
        from ui.util import uopen_file

        uopen_file(self.get_file)

    def remove_file(self):
        """Remove doc and file"""
        self.delete_instance()
        try:
            os.remove(self.get_file)
        except TypeError:
            pass

    def isnottrash(self):
        self.trash = False
        self.save()

    @property
    def os_info(self):
        return os.stat(self.get_file)

    @property
    def created_date(self):
        return time.ctime(self.os_info.st_ctime)

    @property
    def modification_date(self):
        return time.ctime(self.os_info.st_mtime)

    @property
    def last_date_access(self):
        return time.ctime(self.os_info.st_atime)

    @property
    def get_taille(self):
        """La taille du document"""
        octe = 1024
        q = octe
        kocte = octe * octe
        unit = "ko"

        taille_oct = float(self.os_info.st_size)
        if kocte < taille_oct:
            unit = "Mo"
            q = kocte

        taille = round(taille_oct / q, 2)
        return "{} {}".format(taille, unit)


class Owner(BaseModel):

    """The web user who is also owner of the Organization"""

    class Meta:
        ordering = ("username", "desc")
        # db_table = 'owner'

    USER = "Utilisateur"
    ADMIN = "Administrateur"
    ROOT = "superuser"

    username = peewee.CharField(max_length=30, unique=True, verbose_name="Identifiant")
    group = peewee.CharField(default=USER)
    islog = peewee.BooleanField(default=False)
    phone = peewee.CharField(max_length=30, null=True, verbose_name="Telephone")
    password = peewee.CharField(max_length=150)
    isactive = peewee.BooleanField(default=True)
    last_login = peewee.DateTimeField(default=NOW)
    login_count = peewee.IntegerField(default=0)

    def data(self):
        return {
            "username": self.username,
            "group": self.group,
            "islog": self.islog,
            "phone": self.phone,
            "password": self.password,
            "isactive": self.isactive,
            "last_login": datetime_to_str(self.last_login),
            "login_count": self.login_count,
        }

    def __str__(self):
        return "{}".format(self.username)

    def display_name(self):
        return "{name}/{group}/{login_count}".format(
            name=self.username, group=self.group, login_count=self.login_count
        )

    def crypt_password(self, password):
        pw = hashlib.sha224(str(password).encode("utf-8")).hexdigest()
        print(pw)
        return pw

    def save(self):
        if self.islog:
            self.login_count += 1
        super(Owner, self).save()

    def is_login(self):
        return Owner.select().get(islog=True)


class Organization(BaseModel):
    logo_orga = peewee.CharField(verbose_name="", null=True)
    name_orga = peewee.CharField(verbose_name="")
    phone = peewee.IntegerField(null=True, verbose_name="")
    bp = peewee.CharField(null=True, verbose_name="")
    email_org = peewee.CharField(null=True, verbose_name="")
    adress_org = peewee.TextField(null=True, verbose_name="")
    slug = peewee.CharField(null=True)

    def __str__(self):
        return self.display_name()

    def display_name(self):
        return "{}/{}/{}".format(self.name_orga, self.phone, self.email_org)

    @classmethod
    def get_or_create(cls, name_orga, typ):
        try:
            ctct = cls.get(name_orga=name_orga, type_=typ)
        except cls.DoesNotExist:
            ctct = cls.create(name_orga=name_orga, type_=typ)
        return ctct

    def data(self):
        return {
            "logo_orga": self.logo_orga,
            "slug": self.slug,
            "name_orga": self.name_orga,
            "phone": self.phone,
            "bp": self.bp,
            "email_org": self.email_org,
            "adress_org": self.adress_org,
            "is_syncro": self.is_syncro,
            "last_update_date": datetime_to_str(self.last_update_date),
        }


class License(BaseModel):
    # organization = peewee.ForeignKeyField(Organization, backref='organizations')
    code = peewee.CharField(unique=True)
    isactivated = peewee.BooleanField(default=False)
    activation_date = peewee.DateTimeField(default=NOW)
    can_expired = peewee.BooleanField(default=False)
    evaluation = peewee.BooleanField(default=False)
    expiration_date = peewee.DateTimeField(null=True)
    owner = peewee.CharField(default="USER")
    update_date = peewee.DateTimeField(default=NOW)

    def __str__(self):
        return self.code

    def data(self):
        return {
            # 'model': "License",
            "code": self.code,
            "isactivated": self.isactivated,
            "activation_date": datetime_to_str(self.activation_date),
            "can_expired": self.can_expired,
            "evaluation": self.evaluation,
            "expiration_date": datetime_to_str(self.expiration_date),
            "owner": self.owner,
            "update_date": datetime_to_str(self.update_date),
            "is_syncro": self.is_syncro,
            "last_update_date": datetime_to_str(self.last_update_date),
        }

    def check_key(self):
        return

    @property
    def is_expired(self):
        return NOW > self.expiration_date if self.expiration_date else True

    def can_use(self):
        from .cstatic import CConstants

        if not self.isactivated:
            if self.can_expired:
                return CConstants.OK if not self.is_expired else CConstants.IS_EXPIRED
            else:
                return CConstants.IS_NOT_ACTIVATED
        else:
            return CConstants.OK

    def activation(self):
        self.isactivated = True
        self.can_expired = False
        self.save()

    def deactivation(self):
        self.isactivated = False
        self.save()

    def get_evaluation(self):
        self.evaluation = True
        self.can_expired = True
        self.expiration_date = datetime.now() + timedelta(days=60, milliseconds=4)
        self.save()

    def remove_activation(self):
        self.can_expired = True
        self.expiration_date = datetime.now() - timedelta(days=1)
        self.save()

    def remaining_days(self):
        return (
            "{} jours".format(self.expiration_date - datetime.now().days)
            if self.can_expired
            else "illimité"
        )


class Version(BaseModel):
    date = peewee.DateTimeField(default=NOW, verbose_name="Date de Version")
    number = peewee.IntegerField(default=1, verbose_name="Numéro de Version")

    def __str__(self):
        return "{}/{}".format(self.number, self.date)

    def data(self):
        return {
            "model": "Version",
            "date": datetime_to_str(self.date),
            "number": self.number,
            "is_syncro": self.is_syncro,
            "last_update_date": datetime_to_str(self.last_update_date),
        }

    def display_name(self):
        return "db-v{}".format(self.number)

    def update_v(self):
        self.number += 1
        self.date = NOW
        # print(self.number)
        self.save()

    @classmethod
    def get_or_create(cls, number):
        try:
            ctct = cls.get(number=number)
        except cls.DoesNotExist:
            ctct = cls.create(number=number, date=NOW)
        return ctct


class History(BaseModel):
    date = peewee.DateTimeField(default=NOW)
    data = peewee.CharField()
    action = peewee.CharField()

    def __str__(self, arg):
        return "{} à {} par {}".format(date=self.date, action=self.action)

    def data(self):
        return {
            "date": datetime_to_str(self.date),
            "data": self.data,
            "action": self.action,
            "is_syncro": self.is_syncro,
            "last_update_date": datetime_to_str(self.last_update_date),
        }


class Settings(BaseModel):
    """docstring for Settings"""

    PREV = 0
    CURRENT = 1
    DEFAULT = 2
    LCONFIG = ((PREV, "Precedent"), (DEFAULT, "Par defaut"), (CURRENT, "Actuel"))

    DF = "systeme"
    BL = "blue"
    DK = "dark"
    FAD = "Bnb"
    THEME = {DF: "Par defaut", DK: "Dark", BL: "Blue", FAD: "Bnb"}

    USA = "dollar"
    XOF = "xof"
    EURO = "euro"
    DEVISE = {USA: "$", XOF: "F", EURO: "€"}

    LEFT = "left"
    RITGH = "right"
    TOP = "top"
    BOTTOM = "bottom"
    POSITION = {LEFT: "Gauche", RITGH: "Droite", TOP: "Haut", BOTTOM: "Bas"}

    slug = peewee.CharField(choices=LCONFIG, default=DEFAULT)
    is_login = peewee.BooleanField(default=True)
    after_cam = peewee.IntegerField(default=1, verbose_name="")
    toolbar = peewee.BooleanField(default=True)
    toolbar_position = peewee.CharField(choices=POSITION, default=LEFT)
    url = peewee.CharField(default="http://file-repo.ml")
    theme = peewee.CharField(default=DF)
    devise = peewee.CharField(choices=DEVISE, default=XOF)

    def data(self):
        return {
            "slug": self.slug,
            "is_login": self.is_login,
            "after_cam": self.after_cam,
            "toolbar": self.toolbar,
            "toolbar_position": self.toolbar_position,
            "url": self.url,
            "theme": self.theme,
            "devise": self.devise,
            "is_syncro": self.is_syncro,
            "last_update_date": datetime_to_str(self.last_update_date),
        }

    def __str__(self):
        return self.display_name()

    def display_name(self):
        return "{}/{}/{}".format(self.slug, self.is_login, self.theme)

    def save(self):
        """ """
        if not self.url:
            self.url = "http://file-repo.ml"
        super(Settings, self).save()
