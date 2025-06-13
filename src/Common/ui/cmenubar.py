#!/usr/bin/env python
# -*- coding: utf8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu
# maintainer: Fad

from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import QAction, QMenuBar, QMessageBox

from ..exports import export_backup, export_database_as_file, import_backup
from ..models import Owner, Settings
from .theme_manager import get_theme_manager
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
        
        # Menu Utilisateur
        self.user_menu = self.addMenu("👤 Utilisateur")
        
        # Ajouter les informations de l'utilisateur connecté
        try:
            # Récupérer l'utilisateur connecté une seule fois
            self.connected_owner = Owner.select().where(Owner.is_identified==True).first()
            
            if self.connected_owner:
                # Menu déroulant avec les informations de l'utilisateur
                user_info = QAction(
                    QIcon(f"{CConstants.img_cmedia}user_active.png"),
                    f"👤 {self.connected_owner.username}",
                    self
                )
                user_info.setEnabled(False)  # Non cliquable
                self.user_menu.addAction(user_info)
                
                # Séparateur
                self.user_menu.addSeparator()
                
                # Informations détaillées
                user_details = QAction(
                    QIcon(f"{CConstants.img_cmedia}info.png"),
                    f"Groupe: {'👑 Admin' if self.connected_owner.group == Owner.ADMIN else '👤 Utilisateur'}",
                    self
                )
                user_details.setEnabled(False)
                self.user_menu.addAction(user_details)
                
                if self.connected_owner.phone:
                    phone_action = QAction(
                        QIcon(f"{CConstants.img_cmedia}phone.png"),
                        f"📱 {self.connected_owner.phone}",
                        self
                    )
                    phone_action.setEnabled(False)
                    self.user_menu.addAction(phone_action)
                
                # Dernière connexion
                last_login = QAction(
                    QIcon(f"{CConstants.img_cmedia}time.png"),
                    f"🕒 Dernière connexion: {self.connected_owner.last_login.strftime('%d/%m/%Y %H:%M')}",
                    self
                )
                last_login.setEnabled(False)
                self.user_menu.addAction(last_login)
                
                # Séparateur
                self.user_menu.addSeparator()
                
                # Bouton de déconnexion
                logout_action = QAction(
                    QIcon(f"{CConstants.img_cmedia}logout.png"),
                    "🔒 Déconnexion",
                    self
                )
                logout_action.triggered.connect(self.logout)
                self.user_menu.addAction(logout_action)
        except Exception as e:
            logger.error(f"Erreur lors de l'ajout des informations utilisateur: {e}")
        
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

        try:
            ow = Owner.select().where(Owner.is_identified==True )
            logger.debug(f"Recherche des propriétaires connectés: {ow.exists()}")
            
            if ow.exists():
                owner = ow.get()
                logger.debug(f"Propriétaire trouvé - groupe: {owner.group}, Admin requis: {Owner.ADMIN}")
                
                if owner.group in [Owner.ADMIN, Owner.SUPERUSER] and "del_all" not in exclude_mn:
                    backup.addAction(
                        "Suppression de tout les enregistrements", self.goto_clean_db
                    )
                    logger.debug("Menu de suppression ajouté pour l'administrateur")
            else:
                logger.debug("Aucun propriétaire connecté trouvé")

        except Exception as e:
            logger.error(f"Erreur lors de la vérification des droits administrateur: {e}")

        # Comptes utilisateur
        admin = self.file_.addMenu("&Outils")

        preference = self.addMenu("&Préference")

        if "theme" not in exclude_mn:
            _theme = preference.addMenu("🎨 Thème")

            # Utiliser le nouveau gestionnaire de thèmes centralisé
            try:
                theme_manager = get_theme_manager()
                current_theme = theme_manager.get_current_theme()
                available_themes = theme_manager.get_available_themes()
                logger.info(f"Thème actuel: {current_theme}")
            except Exception as e:
                logger.warning(f"Erreur lors de la récupération du gestionnaire de thèmes: {e}")
                current_theme = "light_modern"  # Thème par défaut
                available_themes = {
                    "light_modern": "🌟 Moderne Clair",
                    "dark_modern": "🌙 Moderne Sombre"
                }
            
            # Construction du menu avec les 2 thèmes modernes
            for theme_key, theme_display_name in available_themes.items():
                icon = ""
                if theme_key == current_theme:
                    icon = "accept"
                    
                el_menu = QAction(  
                    QIcon("{}{}.png".format(CConstants.img_cmedia, icon)),
                    theme_display_name,
                    self,
                )
                el_menu.setShortcut("")
                el_menu.triggered.connect(
                    lambda checked, goto=theme_key: self.change_theme_modern(goto)
                )
                _theme.addAction(el_menu)
                
            _theme.setIcon(QIcon(f"{CConstants.img_cmedia}theme.png"))
        # Gestion du menu administrateur
        try:
            logger.debug(f"Vérification des droits admin: {ow.exists()}")
            if ow.exists():
                owner = ow.get()
                logger.debug(f"Utilisateur connecté - groupe: {owner.group}, Admin requis: {Owner.ADMIN}")
                
                if owner.group in [Owner.ADMIN, Owner.SUPERUSER]:
                    admin_ = QAction(
                        QIcon.fromTheme("", QIcon(f"{CConstants.img_cmedia}settings.png")),
                        "Gestion Administration",
                        self,
                    )
                    admin_.setShortcut("Ctrl+G")
                    admin_.triggered.connect(self.goto_admin)
                    preference.addAction(admin_)
                    logger.debug("Menu d'administration ajouté avec succès")
                else:
                    logger.debug("Accès administrateur refusé - droits insuffisants")
            else:
                logger.debug("Aucun utilisateur connecté - menu admin non ajouté")
        except Exception as e:
            logger.error(f"Erreur lors de l'ajout du menu administrateur: {e}")
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

    def change_theme_modern(self, theme_key):
        """Change le thème en utilisant le nouveau système centralisé"""
        try:
            # Utiliser le nouveau gestionnaire de thèmes
            theme_manager = get_theme_manager()
            theme_manager.apply_theme(theme_key)
            
            # Sauvegarder dans les paramètres pour persistance
            try:
                settings = Settings.init_settings()
                settings.theme = theme_key
                settings.save()
                logger.info(f"Thème sauvegardé: {theme_key}")
            except Exception as e:
                logger.warning(f"Erreur sauvegarde paramètres: {e}")
            
            # Notifier l'utilisateur
            self.parent.Notify(f"Thème changé vers: {theme_manager.get_available_themes().get(theme_key, theme_key)}", "success")
            
            logger.info(f"🎨 Thème moderne appliqué: {theme_key}")
            
        except Exception as e:
            logger.error(f"Erreur lors du changement de thème moderne: {e}")
            self.parent.Notify("Erreur lors du changement de thème", "error")

    def change_theme(self, theme):
        """Méthode de compatibilité avec l'ancien système"""
        # Rediriger vers la nouvelle méthode
        if theme in ["light_modern", "dark_modern"]:
            self.change_theme_modern(theme)
        else:
            # Mapper les anciens thèmes vers les nouveaux
            theme_mapping = {
                "default": "light_modern",
                "dark": "dark_modern",
                "light": "light_modern"
            }
            new_theme = theme_mapping.get(theme, "light_modern")
            self.change_theme_modern(new_theme)

    def apply_theme_dynamically(self):
        """Méthode de compatibilité - rediriger vers le nouveau système"""
        try:
            theme_manager = get_theme_manager()
            current_theme = theme_manager.get_current_theme()
            theme_manager.apply_theme(current_theme)
            logger.info("Thème appliqué via le système moderne")
        except Exception as e:
            logger.error(f"Erreur application thème dynamique: {e}")
    
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
