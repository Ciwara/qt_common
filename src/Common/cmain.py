#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu
# maintainer: Fadiga

"""
Ce module ne doit pas être exécuté directement.
Utilisez example_main.py ou importez la fonction cmain() depuis un autre script.
"""

import gettext
import locale
import sys
import atexit

# Vérification si le module est exécuté directement
if __name__ == "__main__":
    print("❌ Erreur: Ce module ne peut pas être exécuté directement.")
    print("📝 Utilisez plutôt: python example_main.py")
    print("   ou importez la fonction: from Common.cmain import cmain")
    sys.exit(1)

from PyQt6.QtWidgets import QDialog, QApplication

from . import gettext_windows
from .cstatic import CConstants, license_required, logger
from .models import Organization, Owner, Settings, init_database, dbh
from .ui.license_view import LicenseViewWidget
from .ui.login import LoginWidget
from .ui.organization_add_or_edit import NewOrEditOrganizationViewWidget
from .ui.restoration_view import RestorationViewWidget
from .migrations import run_migrations
from .migrations.migration_tracker import MigrationTracker

from .ui.user_add_or_edit import NewOrEditUserViewWidget
from .ui.util import is_valide_mac
from .ui.window import FWindow

def cleanup():
    """Fonction de nettoyage appelée à la fermeture de l'application"""
    try:
        logger.info("💾 Sauvegarde de la base de données avant fermeture...")
        # Sauvegarder la base de données avant de la fermer.
        # IMPORTANT: `atexit` peut être appelé quand QApplication est déjà détruite,
        # donc aucune UI (QMessageBox/QFileDialog) ne doit être invoquée ici.
        try:
            app = QApplication.instance()
            if app is not None:
                from .exports import save_database_on_exit
                # parent=None: pas de fenêtre, mais QApplication existe encore
                save_database_on_exit(max_backups=10, parent=None)
            else:
                logger.info("QApplication déjà fermée: sauvegarde UI ignorée")
        except Exception as backup_error:
            logger.warning(f"Impossible d'effectuer la sauvegarde automatique: {backup_error}")
        
        logger.info("Fermeture de la base de données")
        if dbh is not None and not dbh.is_closed():
            dbh.close()
    except Exception as e:
        logger.error(f"Erreur lors de la fermeture de la base de données: {e}")

# Enregistrement de la fonction de nettoyage
atexit.register(cleanup)


def ensure_application_database_tables():
    """
    Projet hôte : si un module top-level ``database`` expose ``Setup`` (ex. MPayments
    avec AdminDatabase.create_all_or_pass), crée les tables métier après les migrations
    Common et avant la fenêtre principale.
    """
    try:
        import database as app_db
    except ImportError:
        return
    setup_cls = getattr(app_db, "Setup", None)
    if setup_cls is None:
        return
    if dbh is not None and dbh.is_closed():
        dbh.connect()
    setup_cls().create_all_or_pass()
    logger.info("Tables métier initialisées (module database.Setup)")


def setup_localization():
    logger.info("Configuration de la localisation")
    gettext_windows.setup_env()
    locale.setlocale(locale.LC_ALL, "")
    gettext.install("main.py", localedir="locale")
    logger.debug("Localisation configurée avec succès")

def check_and_run_migrations():
    """Vérifie et exécute les migrations nécessaires"""
    try:
        logger.info("🔍 Vérification des migrations nécessaires")
        
        # Vérifier que la base de données est initialisée
        if not init_database():
            logger.error("❌ Impossible d'initialiser la base de données")
            return False
            
        # Vérifier la connexion à la base de données
        if dbh is None:
            logger.error("❌ La base de données n'est pas initialisée")
            return False
            
        if dbh.is_closed():
            logger.info("🔄 Connexion à la base de données")
            try:
                dbh.connect()
            except Exception as e:
                logger.error(f"❌ Erreur lors de la connexion à la base de données: {e}")
                return False
                
        logger.info("✅ Connexion à la base de données établie")
        if not MigrationTracker.migrate():
            logger.error("❌ Échec de la migration du système de suivi")
            return False
            
        # Exécuter les migrations
        if run_migrations():
            logger.info("✅ Migrations vérifiées et appliquées avec succès")
            return True
        else:
            logger.error("❌ Erreur lors de l'exécution des migrations")
            return False
            
    except Exception as e:
        logger.error(f"❌ Erreur lors de la vérification des migrations: {e}")
        return False
    finally:
        # Fermer la connexion à la base de données
        if dbh is not None and not dbh.is_closed():
            dbh.close()
            logger.info("✅ Connexion à la base de données fermée")

def initialize_main_window():   
    """Tentative d'initialisation de la fenêtre principale (externe)"""
    try:
        from ui.mainwindow import MainWindow
        logger.info("Initialisation de la fenêtre principale externe")
        window = MainWindow()
        setattr(FWindow, "window", window)
        logger.debug("Fenêtre principale externe initialisée")
        return window
    except ImportError as e:
        logger.warning(f"Module ui.mainwindow non trouvé: {e}")
        raise e

def initialize_common_main_window():
    """Initialisation de la fenêtre principale du module Common"""
    from .ui.commun_mainwindow import CommonMainWindow
    logger.info("Initialisation de la fenêtre principale du module Common")
    window = CommonMainWindow()
    setattr(FWindow, "window", window)
    logger.debug("Fenêtre principale Common initialisée")
    return window


def handle_initial_conditions(window):
    logger.info("Vérification des conditions initiales")
    
    try:
        # Initialisation des paramètres
        settings = Settings.init_settings()
        logger.debug("Paramètres initialisés avec succès")

        # Vérification des propriétaires actifs
        active_owners = Owner.select().where(Owner.isactive, Owner.group != Owner.SUPERUSER)
        if not active_owners.exists():
            logger.debug("Aucun propriétaire actif du groupe Administrateur trouvé")
            if RestorationViewWidget().exec() != QDialog.DialogCode.Accepted:
                logger.warning("Restauration annulée par l'utilisateur")
                return False
            if NewOrEditUserViewWidget().exec() != QDialog.DialogCode.Accepted:
                logger.warning("Création d'utilisateur annulée par l'utilisateur")
                return False

        # Vérification des organisations
        if not Organization.select().exists():
            logger.debug("Aucune organisation trouvée")
            if NewOrEditOrganizationViewWidget().exec() != QDialog.DialogCode.Accepted:
                logger.warning("Création d'organisation annulée par l'utilisateur")
                return False

        # Vérification de la licence (désactivable : COMMON_SKIP_LICENSE ou LICENSE_REQUIRED=False)
        if license_required():
            license_status = is_valide_mac()[1]
            if license_status != CConstants.OK:
                logger.debug(f"Vérification de la licence - Statut: {license_status}")
                if LicenseViewWidget(parent=None).exec() != QDialog.DialogCode.Accepted:
                    logger.warning("Activation de la licence annulée par l'utilisateur")
                    return False
                license_status = is_valide_mac()[1]
                if license_status != CConstants.OK:
                    logger.warning(
                        "Licence toujours invalide après la fenêtre d'activation (statut: %s)",
                        license_status,
                    )
                    return False
        else:
            logger.info(
                "Démarrage sans contrôle de licence (COMMON_SKIP_LICENSE ou LICENSE_REQUIRED désactivé)."
            )

        # Vérification de la connexion
        if settings.auth_required:
            logger.debug("Authentification requise")
            login_dialog = LoginWidget()
            # Connecter le signal de connexion réussie pour mettre à jour le menu
            if hasattr(window, 'refresh_menu_after_login'):
                login_dialog.login_successful.connect(window.refresh_menu_after_login)
            if login_dialog.exec() != QDialog.DialogCode.Accepted:
                logger.warning("Connexion annulée ou échouée")
                return False
            logger.info("Authentification réussie")
            # Mettre à jour le menu après la connexion réussie
            if hasattr(window, 'refresh_menu_after_login'):
                window.refresh_menu_after_login()
        else:
            logger.debug("Aucune authentification requise - Connexion automatique du dernier utilisateur")
            # Désactiver tous les utilisateurs identifiés
            Owner.update(is_identified=False).where(Owner.is_identified == True).execute()
            
            # Récupérer le dernier utilisateur connecté (celui avec la dernière date de connexion)
            last_user = Owner.select().where(Owner.isactive == True).order_by(Owner.last_login.desc()).first()
            
            if last_user:
                # Connecter automatiquement le dernier utilisateur
                last_user.is_identified = True
                last_user.save()
                logger.info(f"✅ Utilisateur '{last_user.username}' connecté automatiquement")
                
                # Mettre à jour le menu pour afficher l'utilisateur connecté
                if hasattr(window, 'refresh_menu_after_login'):
                    window.refresh_menu_after_login()
            else:
                logger.warning("⚠️ Aucun utilisateur actif trouvé pour la connexion automatique")
        
        logger.info("Toutes les conditions initiales sont satisfaites")
        window.showMaximized()
        return True

    except Exception as e:
        logger.error(f"Erreur lors de la vérification des conditions initiales: {e}")
        return False

def cmain(test=False):
    logger.info("Démarrage de l'application")
    
    try:
        # Initialisation de l'application Qt
        app = QApplication(sys.argv)
        
        # Initialisation de la base de données
        if not init_database():
            logger.error("Impossible d'initialiser la base de données")
            return False
            
        # Vérification de la connexion à la base de données
        if dbh is None:
            logger.error("La base de données n'est pas initialisée")
            return False
            
        if dbh.is_closed():
            logger.info("Connexion à la base de données")
            dbh.connect()
        
        # Vérification et exécution des migrations
        if not check_and_run_migrations():
            logger.error("Impossible de vérifier ou d'appliquer les migrations")
            return False

        ensure_application_database_tables()

        if dbh is not None and dbh.is_closed():
            logger.info("Connexion à la base de données (post-migrations)")
            dbh.connect()

        setup_localization()

        # Appliquer le thème déjà enregistré (sinon il n'est jamais relu au prochain lancement)
        try:
            from .ui.theme import THEME_LIGHT, THEME_NAMES, apply_theme

            if dbh is not None and dbh.is_closed():
                dbh.connect()
            _st = Settings.init_settings()
            _t = getattr(_st, "theme", None) or THEME_LIGHT
            if isinstance(_t, str):
                _t = _t.strip().lower()
            if _t in ("", "default"):
                _t = THEME_LIGHT
            elif _t not in THEME_NAMES:
                _t = THEME_LIGHT
            apply_theme(app, _t, save_to_settings=False)
        except Exception as e:
            logger.warning("Thème au démarrage ignoré: %s", e)

        # Appliquer la taille de police enregistrée (accessibilité)
        try:
            from .ui.theme import apply_font_scale

            if dbh is not None and dbh.is_closed():
                dbh.connect()
            _st = Settings.init_settings()
            apply_font_scale(app, getattr(_st, "font_scale", 1.0) or 1.0, save_to_settings=False)
        except Exception as e:
            logger.warning("Taille police au démarrage ignorée: %s", e)

        # Tentative d'initialisation de la fenêtre principale
        window = None

        if test:
            window = initialize_common_main_window()
        else:
            window = initialize_main_window()

        if window is None:
            logger.error("Aucune fenêtre n'a pu être initialisée")
            return False

        # Ne court-circuiter la connexion / licence qu'en mode `test` unitaire.
        # Si `CConstants.DEBUG` est True, l'ancien comportement sautait
        # `handle_initial_conditions` : aucun Owner.is_identified (ex. factures).
        if test:
            window.showMaximized()
            return app.exec()

        if handle_initial_conditions(window):
            return app.exec()

        return False

    except Exception as e:
        logger.error(f"Erreur lors du démarrage de l'application: {e}")
        return False
