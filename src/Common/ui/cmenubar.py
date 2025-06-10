#!/usr/bin/env python
# -*- coding: utf8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu
# maintainer: Fad

from datetime import datetime
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import QAction, QMenuBar, QMessageBox

from ..exports import export_backup, export_database_as_file, import_backup
from ..models import Owner, Settings
from .clean_db import DBCleanerWidget
from .common import FWidget
from .license_view import LicenseViewWidget
from ..cstatic import CConstants, logger



class FMenuBar(QMenuBar, FWidget):
    def __init__(self, parent=None, admin=False, *args, **kwargs):
        QMenuBar.__init__(self, parent=parent, *args, **kwargs)

        self.setWindowIcon(QIcon(QPixmap("{}".format(CConstants.APP_LOGO_ICO))))

        self.parent = parent

        exclude_mn = CConstants.EXCLUDE_MENU_ADMIN
        # Menu File
        self.file_ = self.addMenu("&Fichier")
        # Export
        backup = self.file_.addMenu("&Base de données")
        backup.setIcon(QIcon(f"{CConstants.img_cmedia}db.png"))
        # Sauvegarde
        savegarder = QAction(
            QIcon.fromTheme("", QIcon(f"{CConstants.img_cmedia}export.png")),
            "Sauvegarder",
            self,
        )
        savegarder.setShortcut("Alt+E")
        savegarder.triggered.connect(self.goto_export_db)
        backup.addAction(savegarder)

        # Importer db
        import_db = QAction(
            QIcon.fromTheme("", QIcon(f"{CConstants.img_cmedia}import_db.png")),
            "Importation db",
            self,
        )
        import_db.setShortcut("Alt+I")

        import_db.triggered.connect(self.goto_import_backup)
        backup.addAction(import_db)

        ow = Owner.select().where(Owner.islog == True)
        if ow.exists():
            if ow.get().group == Owner.ADMIN and "del_all" not in exclude_mn:
                backup.addAction(
                    "Suppression de tout les enregistrements", self.goto_clean_db
                )

        # Comptes utilisateur
        admin = self.file_.addMenu("&Outils")

        preference = self.addMenu("&Préference")

        if "theme" not in exclude_mn:
            _theme = preference.addMenu("Theme")
            
            # Récupération des thèmes disponibles depuis le nouveau système centralisé
            try:
                from .themes import get_available_themes
                available_themes = get_available_themes()
                logger.info(f"Thèmes disponibles: {available_themes}")
            except Exception as e:
                logger.warning(f"Erreur lors de la récupération des thèmes: {e}")
                # Fallback vers les thèmes de base
                available_themes = {
                    "default": "Défaut",
                    "light_modern": "Moderne Clair", 
                    "dark_modern": "Moderne Sombre"
                }
            
            # Récupération du thème actuel avec gestion d'erreur
            try:
                settings = Settings.init_settings()
                current_theme = settings.theme
                logger.info(f"Thème actuel: {current_theme}")
            except Exception as e:
                logger.warning(f"Erreur lors de la récupération des paramètres: {e}")
                current_theme = "default"   # Thème par défaut
            
            # Construction du menu des thèmes
            for theme_key, theme_display_name in available_themes.items():
                icon = ""
                if theme_key == current_theme:
                    icon = "accept"
                    
                el_menu = QAction(
                    QIcon("{}{}.png".format(CConstants.img_cmedia, icon)),
                    theme_display_name,  # Utiliser le nom d'affichage au lieu du code
                    self,
                )
                el_menu.setShortcut("")  # Pas de raccourci pour éviter les conflits
                el_menu.triggered.connect(
                    lambda checked, goto=theme_key: self.change_theme(goto)
                )
                _theme.addAction(el_menu)  # Pas de séparateur entre chaque thème
                
            _theme.setIcon(QIcon(f"{CConstants.img_cmedia}theme.png"))

        if ow.exists():
            if ow.get().group == Owner.ADMIN:
                admin_ = QAction(
                    QIcon.fromTheme("", QIcon(f"{CConstants.img_cmedia}settings.png")),
                    "Gestion Administration",
                    self,
                )
                admin_.setShortcut("Ctrl+G")
                admin_.triggered.connect(self.goto_admin)
                preference.addAction(admin_)
        # logout
        lock = QAction(QIcon(f"{CConstants.img_cmedia}login.png"), "Verrouiller", self)
        lock.setShortcut("Ctrl+V")
        lock.setToolTip("Verrouiller l'application")
        lock.triggered.connect(self.logout)
        self.file_.addAction(lock)
        # R
        log_file = QAction(QIcon(), "Log ", self)
        log_file.setShortcut("Ctrl+l")
        # log_file.setToolTip(u"Verrouiller l'application")
        log_file.triggered.connect(self.open_logo_file)
        admin.addAction(log_file)

        g_license = self.addMenu("&Licence")
        if "license" not in exclude_mn:
            license = QAction(
                QIcon.fromTheme(
                    "emblem-system",
                    QIcon(f"{CConstants.img_cmedia}licence.png"),
                ),
                "Activation",
                self,
            )
            license.setShortcut("Alt+A")
            license.triggered.connect(self.goto_license)
            g_license.addAction(license)

        # Exit
        exit_ = QAction(QIcon.fromTheme("application-exit", QIcon("")), "Exit", self)
        exit_.setShortcut("Ctrl+Q")
        exit_.setToolTip("Quiter l'application")
        exit_.triggered.connect(self.parent.close)
        self.file_.addAction(exit_)

    def logout(self):
        from .login import LoginWidget

        LoginWidget(hibernate=True).exec_()

    # Export the database.
    def goto_export_db(self):
        export_database_as_file()

    def goto_export_backup(self):
        export_backup(folder=CConstants.des_image_record, dst_folder=CConstants.ARMOIRE)

    def goto_import_backup(self):
        import_backup(folder=CConstants.des_image_record, dst_folder=CConstants.ARMOIRE)

    def goto_clean_db(self):
        self.open_dialog(DBCleanerWidget, modal=True)

    # Admin
    def goto_admin(self):
        from .admin import AdminViewWidget

        self.change_main_context(AdminViewWidget)

    # G. license
    def goto_license(self):
        self.open_dialog(LicenseViewWidget, modal=True)

    def change_theme(self, theme):
        try:
            # Utiliser init_settings qui crée l'enregistrement s'il n'existe pas
            settings = Settings.init_settings()
            settings.theme = theme
            settings.save()
            logger.info(f"Thème changé vers: {theme}")
            
            # Appliquer le nouveau thème dynamiquement sans redémarrage
            self.apply_theme_dynamically()
            
        except Exception as e:
            logger.error(f"Erreur lors du changement de thème: {e}")
            try:
                # Fallback: créer un nouvel enregistrement
                Settings.create(id=1, theme=theme)
                logger.info(f"Nouveau paramètre créé avec thème: {theme}")
                self.apply_theme_dynamically()
            except Exception as e2:
                logger.error(f"Impossible de créer les paramètres: {e2}")
                return

    def apply_theme_dynamically(self):
        """Applique le nouveau thème sans redémarrer l'application"""
        try:
            # Utiliser le nouveau gestionnaire de thèmes centralisé
            from .themes import apply_theme_immediately, get_theme_manager
            
            # Appliquer le thème à TOUTE l'application (toutes fenêtres et dialogues)
            success = apply_theme_immediately()
            
            if success:
                logger.info("Thème appliqué dynamiquement avec succès à toute l'application")
                
                # Utiliser le gestionnaire pour la notification
                manager = get_theme_manager()
                manager.notify_theme_change(self.parent, manager.get_current_theme())
                
            else:
                logger.warning("Échec de l'application du thème")
                
        except Exception as e:
            logger.error(f"Erreur lors de l'application dynamique du thème: {e}")
            # En cas d'erreur, proposer le redémarrage classique
            from PyQt5.QtWidgets import QMessageBox
            reply = QMessageBox.question(
                self.parent,
                "Changement de thème", 
                "Le thème a été sauvegardé mais n'a pas pu être appliqué dynamiquement.\n\n"
                "Voulez-vous redémarrer l'application pour voir les changements ?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                self.restart()
    
    def refresh_widgets_recursively(self, widget):
        """Rafraîchit récursivement tous les widgets enfants"""
        try:
            # Rafraîchir le widget actuel
            widget.update()
            widget.repaint()
            
            # Rafraîchir tous les widgets enfants
            for child in widget.findChildren(object):
                if hasattr(child, 'update') and hasattr(child, 'repaint'):
                    child.update()
                    child.repaint()
                    
                    # Si le widget enfant a une méthode refresh, l'appeler
                    if hasattr(child, 'refresh') and callable(getattr(child, 'refresh')):
                        try:
                            child.refresh()
                        except:
                            pass
                    
                    # Si le widget enfant a une méthode refresh_, l'appeler
                    if hasattr(child, 'refresh_') and callable(getattr(child, 'refresh_')):
                        try:
                            child.refresh_()
                        except:
                            pass
                            
        except Exception as e:
            logger.debug(f"Erreur lors du rafraîchissement récursif: {e}")
    
    def refresh_main_components(self):
        """Rafraîchit les composants principaux de l'interface"""
        try:
            # Rafraîchir la barre d'outils si elle existe
            if hasattr(self.parent, 'toolbar') and self.parent.toolbar:
                self.parent.toolbar.update()
                self.parent.toolbar.repaint()
            
            # Rafraîchir la barre de statut si elle existe
            if hasattr(self.parent, 'statusBar') and callable(self.parent.statusBar):
                status_bar = self.parent.statusBar()
                if status_bar:
                    status_bar.update()
                    status_bar.repaint()
            
            # Rafraîchir le widget central si il existe
            central_widget = self.parent.centralWidget()
            if central_widget:
                central_widget.update()
                central_widget.repaint()
                
                # Si le widget central a une méthode de rafraîchissement
                if hasattr(central_widget, 'refresh') and callable(getattr(central_widget, 'refresh')):
                    try:
                        central_widget.refresh()
                    except:
                        pass
                        
        except Exception as e:
            logger.debug(f"Erreur lors du rafraîchissement des composants principaux: {e}")
                
    def update_menu_icons(self):
        """Met à jour les icônes du menu selon le thème actuel"""
        try:
            # Cette méthode peut être étendue pour adapter les icônes au thème
            # Par exemple, utiliser des icônes claires pour les thèmes sombres
            
            # Rafraîchir la barre de menu actuelle
            self.update()
            self.repaint()
            
            # Optionnel: adapter les icônes selon le thème (fonctionnalité future)
            # from ..ui.style_qss import is_dark_theme
            # if is_dark_theme():
            #     # Utiliser des icônes adaptées aux thèmes sombres
            #     pass
            # else:
            #     # Utiliser des icônes adaptées aux thèmes clairs
            #     pass
            
        except Exception as e:
            logger.debug(f"Erreur lors de la mise à jour des icônes: {e}")

    def restart(self):
        """Méthode de redémarrage conservée pour les cas d'urgence"""
        import subprocess
        import sys
        import os

        self.parent.close()
        
        # Détection intelligente du fichier principal
        current_script = sys.argv[0]  # Fichier actuel en cours d'exécution
        
        # Si on a un script spécifique (comme exemples_common_widgets.py), on l'utilise
        if current_script and os.path.exists(current_script):
            main_file = current_script
            logger.info(f"Redémarrage avec le script actuel: {main_file}")
        else:
            # Fallback vers main.py ou lancer_projet.py
            possible_mains = [
                CConstants.NAME_MAIN,  # main.py
                "lancer_projet.py",    # Notre lanceur custom
                "exemples_common_widgets.py"  # Les exemples
            ]
            
            main_file = None
            for possible_main in possible_mains:
                full_path = os.path.join(os.getcwd(), possible_main)
                if os.path.exists(full_path):
                    main_file = full_path
                    logger.info(f"Fichier principal trouvé: {main_file}")
                    break
            
            if not main_file:
                logger.warning("Aucun fichier principal trouvé pour le redémarrage")
                # Afficher un message à l'utilisateur
                from PyQt5.QtWidgets import QMessageBox
                QMessageBox.information(
                    self.parent,
                    "Redémarrage",
                    "Le thème a été changé. Veuillez redémarrer l'application manuellement pour voir les changements."
                )
                return
        
        try:
            # Tentative de redémarrage avec Python
            logger.info(f"Tentative de redémarrage: {sys.executable} {main_file}")
            subprocess.Popen([sys.executable, main_file])
        except Exception as e:
            logger.error(f"Erreur lors du redémarrage: {e}")
            try:
                # Fallback avec shell
                if os.name == 'nt':  # Windows
                    subprocess.call(f"python.exe {main_file}", shell=True)
                else:  # Unix/Linux/MacOS
                    subprocess.call(f"python {main_file}", shell=True)
            except Exception as e2:
                logger.error(f"Erreur lors du redémarrage en fallback: {e2}")
                # Message d'information à l'utilisateur
                from PyQt5.QtWidgets import QMessageBox
                QMessageBox.information(
                    self.parent,
                    "Redémarrage requis",
                    f"""Le thème a été changé avec succès.
                    
Veuillez redémarrer l'application manuellement pour voir les changements.

Fichier à relancer: {main_file}"""
                )

    def goto(self, goto):
        self.change_main_context(goto)

    # Aide
    def goto_help(self):
        # html_view n'existe pas, on peut soit créer une aide simple, soit désactiver cette fonction
        from PyQt5.QtWidgets import QMessageBox
        QMessageBox.information(
            self.parent,
            "Aide",
            f"""
            <h2>Aide - {CConstants.APP_NAME}</h2>
            <hr>
            <p><b>Version:</b> {CConstants.APP_VERSION}</p>
            <p><b>Description:</b> Application de gestion</p>
            <p>Pour plus d'informations, consultez la documentation.</p>
            """
        )

    def open_logo_file(self):
        from .util import uopen_file

        try:
            uopen_file(CConstants.NAME_MAIN.replace(".py", ".log"))
        except Exception as e:
            logger.error(f"Erreur lors de l'ouverture du fichier log: {e}")

    # About
    def goto_about(self):
        QMessageBox.about(
            self,
            "À propos",
            """ <h2>{app_name}  version: {version_app} </h2>
                            <hr>
                            <h4><i>Logiciel de {app_name}.</i></h4>
                            <ul><li></li> <li><b>Developper par : </b>IBS-Mali </li>
                                <li><b>Adresse : </b>Bamako, Boulkassoumbougou Rue : 580 Porte : 388 </li>
                                <li><b>Tel: </b> +223 76 43 38 90 </li>
                                <li><b>E-mail : </b> info@ibsmali.ml <br/></li>
                                <li><a herf="https://ibsmali.ml"/> ibsmail.ml</li>
                            </ul>
                            """.format(
                app_name=CConstants.APP_NAME,
                autor=CConstants.AUTOR,
                version_app=CConstants.APP_VERSION,
            ),
        )
