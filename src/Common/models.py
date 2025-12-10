#!/usr/bin/env python
# -*- coding: utf8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu
# maintainer: Fad

import os
import sys
import time
import bcrypt
import re
import peewee
from datetime import datetime, timedelta

from peewee_migrate import Router
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
        logger.info(f"Sauvegarde de l'enregistrement {self.__class__.__name__} (id: {self.id})")
        self.is_syncro = False
        self.save()

    def data(self):
        return {
            "is_syncro": self.is_syncro,
            "last_update_date": datetime_to_str(self.last_update_date),
        }

    @classmethod
    def all(cls):
        logger.info(f"Récupération de tous les enregistrements de {cls.__name__}")
        return list(cls.select())

    def save(self, *args, **kwargs):
        logger.debug(f"Sauvegarde de l'enregistrement {self.__class__.__name__} (id: {getattr(self, 'id', 'new')})")
        return super().save(*args, **kwargs)

    def delete_instance(self, *args, **kwargs):
        logger.info(f"Suppression de l'enregistrement {self.__class__.__name__} (id: {self.id})")
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
    SUPERUSER = "superuser"

    username = peewee.CharField(max_length=30, unique=True, verbose_name="Identifiant")
    group = peewee.CharField(default=USER)
    is_identified = peewee.BooleanField(default=False)
    phone = peewee.CharField(max_length=30, null=True, verbose_name="Telephone")
    password = peewee.CharField(max_length=150)
    isactive = peewee.BooleanField(default=True)
    last_login = peewee.DateTimeField(default=NOW)
    login_count = peewee.IntegerField(default=0)
    reset_token = peewee.CharField(max_length=64, null=True)
    reset_token_expiry = peewee.DateTimeField(null=True)

    # Constantes pour la gestion des sessions
    SESSION_TIMEOUT = 30 * 60  # 30 minutes en secondes
    MAX_LOGIN_ATTEMPTS = 5
    LOCKOUT_DURATION = 15 * 60  # 15 minutes en secondes

    def data(self):
        return {
            "username": self.username,
            "group": self.group,
            "is_identified": self.is_identified,
            "phone": self.phone,
            "password": self.password,
            "isactive": self.isactive,
            "last_login": datetime_to_str(self.last_login),
            "login_count": self.login_count,
            "reset_token": self.reset_token,
            "reset_token_expiry": datetime_to_str(self.reset_token_expiry),
        }

    def __str__(self):
        return "{}".format(self.username)

    def display_name(self):
        return "{name}/{group}/{login_count}".format(
            name=self.username, group=self.group, login_count=self.login_count
        )

    def crypt_password(self, password):
        """Hachage sécurisé du mot de passe avec bcrypt"""
        if not password:
            return None
        # Génération d'un sel unique pour chaque mot de passe
        salt = bcrypt.gensalt()
        # Hachage du mot de passe avec le sel
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')

    def verify_password(self, password):
        """Vérifie si le mot de passe correspond au hachage stocké"""
        if not password or not self.password:
            return False
        return bcrypt.checkpw(password.encode('utf-8'), self.password.encode('utf-8'))

    @staticmethod
    def validate_password(password):
        """Valide la force du mot de passe selon des critères de sécurité"""
        if len(password) < 8:
            return False, "Le mot de passe doit contenir au moins 8 caractères"
        
        if not re.search(r"[A-Z]", password):
            return False, "Le mot de passe doit contenir au moins une majuscule"
            
        if not re.search(r"[a-z]", password):
            return False, "Le mot de passe doit contenir au moins une minuscule"
            
        if not re.search(r"\d", password):
            return False, "Le mot de passe doit contenir au moins un chiffre"
            
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
            return False, "Le mot de passe doit contenir au moins un caractère spécial"
            
        return True, "Mot de passe valide"

    def save(self):
        # Log informatif pour les sauvegardes importantes
        action = "mise à jour"
        if not hasattr(self, 'id') or self.id is None:
            action = "création"
        
        # Ne pas incrémenter le compteur de connexions ici car c'est déjà fait dans login()
        super(Owner, self).save()
        
        # Log de confirmation plus propre
        if action == "création":
            logger.info(f"✅ Utilisateur '{self.username}' ({self.group}) créé avec succès")

    def is_login(self):
        return Owner.select().get(is_identified=True)
    
    @classmethod
    def get_non_superusers(cls):
        """Retourne tous les propriétaires sauf les superusers"""
        return cls.select().where(cls.group != cls.SUPERUSER)
    
    @classmethod
    def get_active_non_superusers(cls):
        """Retourne tous les propriétaires actifs sauf les superusers"""
        return cls.select().where(cls.isactive, cls.group != cls.SUPERUSER)

    def is_session_valid(self):
        """Vérifie si la session est toujours valide"""
        if not self.is_identified or not self.last_login:
            return False
            
        # Calculer le temps écoulé depuis la dernière connexion
        elapsed_time = (datetime.now() - self.last_login).total_seconds()
        return elapsed_time < self.SESSION_TIMEOUT

    def check_login_attempts(self):
        """Vérifie si l'utilisateur n'est pas bloqué suite à trop de tentatives"""
        if not hasattr(self, 'login_attempts'):
            self.login_attempts = 0
            self.last_attempt = None
            
        # Réinitialiser les tentatives si le temps de blocage est écoulé
        if self.last_attempt and (datetime.now() - self.last_attempt).total_seconds() > self.LOCKOUT_DURATION:
            self.login_attempts = 0
            self.last_attempt = None
            
        return self.login_attempts < self.MAX_LOGIN_ATTEMPTS

    def increment_login_attempts(self):
        """Incrémente le compteur de tentatives de connexion"""
        if not hasattr(self, 'login_attempts'):
            self.login_attempts = 0
            self.last_attempt = None
            
        self.login_attempts += 1
        self.last_attempt = datetime.now()
        self.save()

    def reset_login_attempts(self):
        """Réinitialise le compteur de tentatives de connexion"""
        self.login_attempts = 0
        self.last_attempt = None
        self.save()

    def get_remaining_lockout_time(self):
        """Retourne le temps restant avant la fin du blocage"""
        if not self.last_attempt:
            return 0
            
        elapsed = (datetime.now() - self.last_attempt).total_seconds()
        remaining = self.LOCKOUT_DURATION - elapsed
        return max(0, remaining)

    def generate_reset_token(self):
        """Génère un token de réinitialisation de mot de passe"""
        import secrets
        import string
        
        # Générer un token aléatoire de 32 caractères
        alphabet = string.ascii_letters + string.digits
        token = ''.join(secrets.choice(alphabet) for _ in range(32))
        
        # Stocker le token et sa date d'expiration (1 heure)
        self.reset_token = token
        self.reset_token_expiry = datetime.now() + timedelta(hours=1)
        self.save()
        
        return token

    def verify_reset_token(self, token):
        """Vérifie si le token de réinitialisation est valide"""
        if not hasattr(self, 'reset_token') or not hasattr(self, 'reset_token_expiry'):
            return False
            
        if not self.reset_token or not self.reset_token_expiry:
            return False
            
        # Vérifier si le token correspond et n'est pas expiré
        is_valid = (
            self.reset_token == token and 
            datetime.now() < self.reset_token_expiry
        )
        
        # Si le token est valide, le supprimer
        if is_valid:
            self.reset_token = None
            self.reset_token_expiry = None
            self.save()
            
        return is_valid

    def reset_password(self, new_password):
        """Réinitialise le mot de passe de l'utilisateur"""
        # Valider le nouveau mot de passe
        is_valid, message = self.validate_password(new_password)
        if not is_valid:
            return False, message
            
        # Hacher et sauvegarder le nouveau mot de passe
        self.password = self.crypt_password(new_password)
        self.save()
        
        return True, "Mot de passe réinitialisé avec succès"


class Organization(BaseModel):
    logo_orga = peewee.TextField(verbose_name="", null=True)
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

    # DF = "default"
    # BL = "light_modern"
    # DK = "dark_modern"
    # THEME = {DF: "Défaut", BL: "Moderne Clair", DK: "Moderne Sombre"}

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
    auth_required = peewee.BooleanField(default=True)
    after_cam = peewee.IntegerField(default=1, verbose_name="")
    toolbar = peewee.BooleanField(default=True)
    toolbar_position = peewee.CharField(choices=POSITION, default=LEFT)
    url = peewee.CharField(default="http://file-repo.ml")
    theme = peewee.CharField(default="default")
    devise = peewee.CharField(choices=DEVISE, default=XOF)

    @classmethod
    def init_settings(cls):
        """Initialise les paramètres par défaut si nécessaire"""
        try:
            settings = cls.get(id=1)
            # logger.debug("Paramètres existants trouvés")  # Message masqué
        except cls.DoesNotExist:
            logger.debug("Création des paramètres par défaut")
            
            # Utiliser une insertion SQL directe pour contourner les problèmes de Peewee
            try:
                global dbh  # Utiliser la variable globale directement
                if dbh is None:
                    logger.error("dbh n'est pas initialisé")
                    raise Exception("Base de données non initialisée")
                    
                query = """
                INSERT OR REPLACE INTO settings 
                (id, is_syncro, last_update_date, slug, auth_required, after_cam, toolbar, toolbar_position, url, theme, devise)
                VALUES (1, 0, datetime('now'), ?, ?, ?, ?, ?, ?, ?, ?)
                """
                dbh.execute_sql(query, [
                    cls.DEFAULT,      # slug
                    True,             # auth_required
                    1,                # after_cam
                    True,             # toolbar
                    cls.LEFT,         # toolbar_position
                    "http://file-repo.ml",  # url
                    "system",        # theme
                    cls.XOF           # devise
                ])
                logger.debug("Paramètres créés avec succès via SQL")
                
                # Récupérer l'enregistrement créé
                settings = cls.get(id=1)
                logger.debug(f"Vérification création réussie - thème: {settings.theme}")
                
            except Exception as e:
                logger.error(f"Erreur lors de la création SQL: {e}")
                # Fallback vers la méthode classique
                settings = cls(
                    id=1,
                    slug=cls.DEFAULT,
                    auth_required=True,
                    after_cam=1,
                    toolbar=True,
                    toolbar_position=cls.LEFT,
                    url="http://file-repo.ml",
                    theme="default",
                    devise=cls.XOF
                )
                settings.save()
                logger.debug("Paramètres créés avec succès via fallback")
                
        return settings

    def data(self):
        return {
            "slug": self.slug,
            "auth_required": self.auth_required,
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
        return "{}/{}/{}".format(self.slug, self.auth_required, self.theme)

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

def init_default_version():
    """Initialise une version par défaut avec id=1 si nécessaire"""
    try:
        # Vérifier si un enregistrement Version avec id=1 existe
        version_exists = Version.get_or_none(Version.id == 1)
        
        if version_exists is None:
            logger.info("Création de la version par défaut avec id=1")
            
            # Utiliser une insertion SQL directe pour garantir id=1
            try:
                global dbh
                if dbh is None:
                    logger.error("dbh n'est pas initialisé")
                    raise Exception("Base de données non initialisée")
                    
                query = """
                INSERT OR REPLACE INTO version 
                (id, is_syncro, last_update_date, date, number)
                VALUES (1, 0, datetime('now'), datetime('now'), 1)
                """
                dbh.execute_sql(query)
                logger.info("✅ Version par défaut créée avec succès (id=1, number=1)")
                
                # Vérifier la création
                version = Version.get(id=1)
                logger.debug(f"Vérification création réussie - version: {version.display_name()}")
                
                return True
                
            except Exception as e:
                logger.error(f"Erreur lors de la création SQL de Version: {e}")
                # Fallback vers la méthode classique
                try:
                    version = Version(number=1)
                    version.save()
                    logger.info("✅ Version par défaut créée avec succès via fallback")
                    return True
                except Exception as e2:
                    logger.error(f"Erreur fallback Version: {e2}")
                    return False
        else:
            logger.debug(f"Une version avec id=1 existe déjà: {version_exists.display_name()}")
            return False
            
    except Exception as e:
        logger.error(f"Erreur lors de la création de la version par défaut: {e}")
        return False

def init_default_organization():
    """Initialise une organisation par défaut avec id=1 si nécessaire"""
    try:
        # Vérifier si un enregistrement Organization avec id=1 existe
        org_exists = Organization.get_or_none(Organization.id == 1)
        
        if org_exists is None:
            logger.info("Création de l'organisation par défaut avec id=1")
            
            # Utiliser une insertion SQL directe pour garantir id=1
            try:
                global dbh
                if dbh is None:
                    logger.error("dbh n'est pas initialisé")
                    raise Exception("Base de données non initialisée")
                    
                query = """
                INSERT OR REPLACE INTO organization 
                (id, is_syncro, last_update_date, logo_orga, name_orga, phone, bp, email_org, adress_org, slug)
                VALUES (1, 0, datetime('now'), NULL, ?, 0, ?, ?, ?, ?)
                """
                dbh.execute_sql(query, [
                    "Organisation par défaut",
                    "BP 000", 
                    "contact@example.com",
                    "Adresse par défaut",
                    "default-org"
                ])
                logger.info("✅ Organisation par défaut créée avec succès (id=1)")
                
                # Vérifier la création
                org = Organization.get(id=1)
                logger.debug(f"Vérification création réussie - organisation: {org.name_orga}")
                
                return True
                
            except Exception as e:
                logger.error(f"Erreur lors de la création SQL d'Organization: {e}")
                # Fallback vers la méthode classique
                try:
                    org = Organization(
                        name_orga="Organisation par défaut",
                        phone=0,
                        bp="BP 000",
                        email_org="contact@example.com",
                        adress_org="Adresse par défaut",
                        slug="default-org"
                    )
                    org.save()
                    logger.info("✅ Organisation par défaut créée avec succès via fallback")
                    return True
                except Exception as e2:
                    logger.error(f"Erreur fallback Organization: {e2}")
                    return False
        else:
            logger.debug(f"Une organisation avec id=1 existe déjà: {org_exists.name_orga}")
            return False
            
    except Exception as e:
        logger.error(f"Erreur lors de la création de l'organisation par défaut: {e}")
        return False

def init_default_superuser():
    """Initialise un superuser par défaut si nécessaire"""
    try:
        # Vérifier si un superuser existe déjà
        superuser_exists = Owner.select().where(Owner.group == Owner.SUPERUSER).exists()
        
        if not superuser_exists:
            logger.info("Création du superuser par défaut")
            
            # Créer le superuser par défaut
            superuser = Owner()
            superuser.username = "superuser"
            superuser.group = Owner.SUPERUSER
            superuser.password = superuser.crypt_password("superuser123")  # Mot de passe par défaut
            superuser.phone = "00000000"
            superuser.isactive = True
            superuser.is_identified = False
            superuser.login_count = 0
            superuser.save()
            
            logger.info("✅ Superuser 'superuser' créé avec succès (mot de passe: superuser123)")
            return True
        else:
            logger.debug("Un superuser existe déjà")
            return False
            
    except Exception as e:
        logger.error(f"Erreur lors de la création du superuser par défaut: {e}")
        return False


def list_admins():
    """Liste tous les administrateurs du système"""
    try:
        admins = Owner.select().where(Owner.group == Owner.ADMIN)
        return list(admins)
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des administrateurs: {e}")
        return []

def list_owners_non_superuser():
    """Liste tous les propriétaires sauf les superusers"""
    try:
        owners = Owner.select().where(Owner.group != Owner.SUPERUSER)
        return list(owners)
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des propriétaires: {e}")
        return []

def list_active_owners_non_superuser():
    """Liste tous les propriétaires actifs sauf les superusers"""
    try:
        owners = Owner.select().where(
            Owner.isactive == True,
            Owner.group != Owner.SUPERUSER
        )
        return list(owners)
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des propriétaires actifs: {e}")
        return []

def list_owners_by_group(exclude_superuser=True):
    """Liste les propriétaires groupés par type, en excluant optionnellement les superusers"""
    try:
        result = {
            Owner.USER: [],
            Owner.ADMIN: [],
        }
        
        # Construire la requête avec ou sans superuser
        query = Owner.select()
        if exclude_superuser:
            query = query.where(Owner.group != Owner.SUPERUSER)
        else:
            result[Owner.SUPERUSER] = []
        
        # Grouper par type
        for owner in query:
            if owner.group in result:
                result[owner.group].append(owner)
        
        return result
    except Exception as e:
        logger.error(f"Erreur lors du groupement des propriétaires: {e}")
        return {}

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
        
        # Initialisation des enregistrements par défaut
        init_default_version()
        init_default_organization()
        init_default_superuser()
        
        return True
    except Exception as e:
        logger.error(f"Erreur lors de l'initialisation de la base de données: {e}")
        return False

# Initialisation de la base de données au chargement du module
init_database()
