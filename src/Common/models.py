#!/usr/bin/env python
# -*- coding: utf8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu
# maintainer: Fad


import hashlib
import os
import sys
import time

from peewee_migrate import Router
from datetime import datetime, timedelta

import peewee
from playhouse.migrate import DateTimeField, BooleanField
from peewee import SqliteDatabase

from .cstatic import logger
from .ui.util import copy_file, date_to_str, datetime_to_str

DB_FILE = "database.db"

# If running in a PyInstaller bundle
if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
    # Change the db_file to the absolute path
    DB_FILE = os.path.join(sys._MEIPASS, DB_FILE)

logger.info(f"Utilisation de la base de données: {DB_FILE}")

logger.info(f"Version de Peewee: {peewee.__version__}")

NOW = datetime.now()

# Variables globales pour la base de données et les migrations
dbh = None
router = None

def get_router():
    """Retourne l'instance du router pour les migrations"""
    global router
    if router is None:
        if dbh is None:
            init_database()
        router = Router(dbh, migrate_dir='migrations')
    return router

class BaseModel(peewee.Model):
    class Meta:
        database = None  # Sera défini après l'initialisation de dbh

    is_syncro = BooleanField(default=False)
    last_update_date = DateTimeField(default=NOW)

    def updated(self):
        logger.debug(f"Mise à jour de l'enregistrement {self.__class__.__name__} (id: {self.id})")
        self.is_syncro = True
        self.last_update_date = NOW
        self.save()

    def save_(self):
        logger.debug(f"Sauvegarde de l'enregistrement {self.__class__.__name__} (id: {self.id})")
        self.is_syncro = False
        self.save()

    def data(self):
        return {
            "is_syncro": self.is_syncro,
            "last_update_date": datetime_to_str(self.last_update_date),
        }

    @classmethod
    def all(cls):
        logger.debug(f"Récupération de tous les enregistrements de {cls.__name__}")
        return list(cls.select())

    def save(self, *args, **kwargs):
        logger.debug(f"Sauvegarde de l'enregistrement {self.__class__.__name__} (id: {getattr(self, 'id', 'new')})")
        return super().save(*args, **kwargs)

    def delete_instance(self, *args, **kwargs):
        logger.debug(f"Suppression de l'enregistrement {self.__class__.__name__} (id: {self.id})")
        return super().delete_instance(*args, **kwargs)


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
            f"{self.expiration_date - datetime.now()} jours"
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
    RIGHT = "right"
    TOP = "top"
    BOTTOM = "bottom"
    POSITION = {LEFT: "Gauche", RIGHT: "Droite", TOP: "Haut", BOTTOM: "Bas"}

    slug = peewee.CharField(choices=LCONFIG, default=DEFAULT)
    is_login = peewee.BooleanField(default=True)
    after_cam = peewee.IntegerField(default=1, verbose_name="")
    toolbar = peewee.BooleanField(default=True)
    toolbar_position = peewee.CharField(choices=POSITION, default=LEFT)
    url = peewee.CharField(default="http://file-repo.ml")
    theme = peewee.CharField(default=DF)
    devise = peewee.CharField(choices=DEVISE, default=XOF)

    @classmethod
    def init_settings(cls):
        """Initialise les paramètres par défaut si nécessaire"""
        settings = cls.filter(id=1).first()
        if settings is None:
            logger.debug("Création des paramètres par défaut")
            settings = cls(
                id=1,
                slug=cls.DEFAULT,
                is_login=True,
                after_cam=1,
                toolbar=True,
                toolbar_position=cls.LEFT,
                url="http://file-repo.ml",
                theme=cls.DF,
                devise=cls.XOF
            )
            settings.save()
            logger.debug("Paramètres par défaut créés avec succès")
        else:
            logger.debug("Paramètres existants trouvés")
        return settings

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

    def save(self, *args, **kwargs):
        """ """
        if not self.url:
            self.url = "http://file-repo.ml"
        
        # Filtrer les arguments non supportés par la version de Peewee
        filtered_kwargs = {}
        for key, value in kwargs.items():
            if key != 'force_insert':  # Ignorer force_insert s'il n'est pas supporté
                filtered_kwargs[key] = value
        
        return super(Settings, self).save(*args, **filtered_kwargs)

def init_database():
    """Initialise la base de données et crée les tables si nécessaire"""
    global dbh, router
    try:
        logger.info("Initialisation de la base de données")
        
        # Liste des modèles à créer
        models = [
            BaseModel,
            FileJoin,
            Owner,
            Organization,
            License,
            Version,
            History,
            Settings
        ]
        
        if dbh is None:
            logger.info("Création de la connexion à la base de données")
            dbh = SqliteDatabase(
                DB_FILE,
                pragmas={
                    'journal_mode': 'wal',  # Write-Ahead Logging
                    'cache_size': -64 * 1000,  # 64MB cache
                    'foreign_keys': 1,
                    'ignore_check_constraints': 0,
                    'synchronous': 0,  # Let the OS handle syncing
                    'temp_store': 2,  # Store temp tables and indices in memory
                }
            )
            
            # Initialisation du router pour les migrations
            router = Router(dbh, migrate_dir='migrations')
            
            # Définir la base de données pour tous les modèles
            for model in models:
                model._meta.database = dbh

        # Vérification si la base de données est déjà connectée
        if dbh.is_closed():
            logger.info("Connexion à la base de données")
            dbh.connect()
        logger.info("Base de données connectée")
        
        # Création des tables
        dbh.create_tables(models, safe=True)
        logger.info("Tables créées avec succès")
        
        # Initialisation des paramètres par défaut
        Settings.init_settings()
        logger.info("Paramètres par défaut initialisés")
        
        return True
    except Exception as e:
        logger.error(f"Erreur lors de l'initialisation de la base de données: {e}")
        return False

# Initialisation de la base de données au chargement du module
init_database()
