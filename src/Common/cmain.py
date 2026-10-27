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
from .crash_handler import (
    SafeApplication,
    install_exception_hooks,
    report_uncaught_exception,
    show_startup_error,
)
from .cstatic import CConstants, license_required, logger
from .models import Organization, Owner, Settings, init_database, dbh
from .ui.login import LoginWidget
from .ui.organization_add_or_edit import NewOrEditOrganizationViewWidget
from .ui.restoration_view import RestorationViewWidget
from .migrations import run_migrations
from .migrations.migration_tracker import MigrationTracker

from .ui.user_add_or_edit import NewOrEditUserViewWidget
from .server import Network
from .ui.util import is_valide_mac, request_online_license
from .ui.window import FWindow


def _schedule_launch_report():
    """Inscription / desktop_client une seule fois (thread hors UI)."""
    if not getattr(CConstants, "SERV", False):
        return
    try:
        from PyQt6.QtCore import QThread, QTimer, pyqtSignal
    except Exception:
        return

    class _LaunchReportThread(QThread):
        done = pyqtSignal(object)

        def run(self):
            try:
                self.done.emit(Network().report_launch())
            except Exception as exc:
                self.done.emit({"ok": False, "message": str(exc)})

    def _start():
        thread = _LaunchReportThread()
        app = QApplication.instance()
        if app is not None:
            if not hasattr(app, "_launch_report_threads"):
                app._launch_report_threads = []
            app._launch_report_threads.append(thread)

            def _done(rep):
                try:
                    logger.info(
                        "Connexion serveur au lancement : %s",
                        rep.get("message") if isinstance(rep, dict) else rep,
                    )
                finally:
                    try:
                        app._launch_report_threads.remove(thread)
                    except (ValueError, AttributeError):
                        pass

            thread.done.connect(_done)
        thread.start()

    QTimer.singleShot(300, _start)


def cleanup():
    """Fonction de nettoyage appelée à la fermeture de l'application"""
    try:
        # Sauvegarde déjà faite via closeEvent / Exit (avec proposition USB).
        # Ici : filet de sécurité silencieux seulement si rien n'a été fait.
        try:
            from .exports import exit_backup_already_done, save_database_on_exit

            if exit_backup_already_done():
                logger.info("Sauvegarde de fermeture déjà effectuée (UI)")
            else:
                logger.info("💾 Sauvegarde de secours de la base de données...")
                # parent=None: pas de dialogue (atexit / QApplication peut être détruite)
                save_database_on_exit(max_backups=10, parent=None)
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

        # Licence : vérifier d'abord en local ; n'envoyer qu'une fois si absente.
        # Inscription / desktop_client ensuite (inscription sautée si déjà syncro + licence OK).
        license_blocked = False
        if license_required():
            online = request_online_license()
            logger.info("Demande de licence en ligne : %s", online.get("message"))
            # Si get_licence a été différé → inscription une seule fois (sync)
            if online.get("deferred"):
                try:
                    from .server import Network

                    Network().ensure_registered()
                except Exception as exc:
                    logger.warning("Inscription différée échouée: %s", exc)
            license_status = is_valide_mac()[1]
            license_blocked = license_status != CConstants.OK
            if license_blocked:
                logger.info(
                    "Licence invalide (statut=%s) : page de connexion avec lien produit",
                    license_status,
                )
        else:
            logger.info(
                "Démarrage sans contrôle de licence (COMMON_SKIP_LICENSE ou LICENSE_REQUIRED désactivé)."
            )

        # Contact serveur (desktop_client ; inscription seulement si pas déjà fait)
        _schedule_launch_report()

        # Login obligatoire si auth_required OU licence bloquée (pas d'auto-login)
        if settings.auth_required or license_blocked:
            logger.debug(
                "Authentification requise%s",
                " (licence bloquée)" if license_blocked else "",
            )
            login_dialog = LoginWidget(license_blocked=license_blocked)
            if hasattr(window, "refresh_menu_after_login"):
                login_dialog.login_successful.connect(window.refresh_menu_after_login)
            if login_dialog.exec() != QDialog.DialogCode.Accepted:
                logger.warning("Connexion annulée ou échouée")
                return False
            if license_required() and is_valide_mac()[1] != CConstants.OK:
                logger.warning("Licence toujours invalide après connexion")
                return False
            logger.info("Authentification réussie")
            if hasattr(window, "refresh_menu_after_login"):
                window.refresh_menu_after_login()
        else:
            logger.debug("Aucune authentification requise - Connexion automatique du dernier utilisateur")
            Owner.update(is_identified=False).where(Owner.is_identified == True).execute()
            
            last_user = Owner.select().where(Owner.isactive == True).order_by(Owner.last_login.desc()).first()
            
            if last_user:
                last_user.is_identified = True
                last_user.save()
                logger.info(f"✅ Utilisateur '{last_user.username}' connecté automatiquement")
                
                if hasattr(window, 'refresh_menu_after_login'):
                    window.refresh_menu_after_login()
            else:
                logger.warning("⚠️ Aucun utilisateur actif trouvé pour la connexion automatique")

        logger.info("Toutes les conditions initiales sont satisfaites")
        window.showMaximized()
        return True

    except Exception as e:
        logger.error(f"Erreur lors de la vérification des conditions initiales: {e}")
        report_uncaught_exception(sys.exc_info(), continue_app=False)
        return False

def cmain(test=False):
    logger.info("Démarrage de l'application")
    # --debug / -d : DEBUG=True et URL locale (si pas déjà consommé par l'app hôte)
    try:
        from .cstatic import apply_argv_debug_flag

        apply_argv_debug_flag()
    except Exception:
        pass
    install_exception_hooks()
    
    try:
        # Initialisation de l'application Qt
        app = SafeApplication(sys.argv)
        
        # Initialisation de la base de données
        if not init_database():
            logger.error("Impossible d'initialiser la base de données")
            show_startup_error("Impossible d'initialiser la base de données.")
            return False
            
        # Vérification de la connexion à la base de données
        if dbh is None:
            logger.error("La base de données n'est pas initialisée")
            show_startup_error("La base de données n'est pas initialisée.")
            return False
            
        if dbh.is_closed():
            logger.info("Connexion à la base de données")
            dbh.connect()
        
        # Vérification et exécution des migrations
        if not check_and_run_migrations():
            logger.error("Impossible de vérifier ou d'appliquer les migrations")
            show_startup_error("Impossible de vérifier ou d'appliquer les migrations.")
            return False

        ensure_application_database_tables()

        try:
            from .ui.util import remember_machine

            remember_machine()
        except Exception as e:
            logger.warning("Identifiant machine non mémorisé: %s", e)

        if dbh is not None and dbh.is_closed():
            logger.info("Connexion à la base de données (post-migrations)")
            dbh.connect()

        setup_localization()

        # Appliquer le thème déjà enregistré (« default » / vide → système ; déféré dans theme.apply_theme)
        try:
            from .ui.theme import THEME_NAMES, THEME_SYSTEM, apply_theme, attach_system_theme_listener

            if dbh is not None and dbh.is_closed():
                dbh.connect()
            _st = Settings.init_settings()
            _t_raw = getattr(_st, "theme", "") or ""
            if isinstance(_t_raw, str):
                _t = _t_raw.strip().lower()
            else:
                _t = str(_t_raw).strip().lower()
            if _t not in THEME_NAMES:
                _t = THEME_SYSTEM
            apply_theme(app, _t, save_to_settings=False)
            attach_system_theme_listener(app)
        except Exception as e:
            logger.warning("Thème au démarrage ignoré: %s", e)

        # Tentative d'initialisation de la fenêtre principale
        window = None

        if test:
            window = initialize_common_main_window()
        else:
            window = initialize_main_window()

        if window is None:
            logger.error("Aucune fenêtre n'a pu être initialisée")
            show_startup_error("Aucune fenêtre n'a pu être initialisée.")
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
        report_uncaught_exception(sys.exc_info(), continue_app=False)
        return False
