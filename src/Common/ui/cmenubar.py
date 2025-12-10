#!/usr/bin/env python
# -*- coding: utf8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu
# maintainer: Fad

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
        
        # Menu Utilisateur - Afficher le nom de l'utilisateur connecté dans le titre
        # Ne pas utiliser de fallback pour éviter d'afficher le superuser par défaut
        try:
            # Récupérer uniquement l'utilisateur connecté (is_identified == True)
            # Normalement il ne devrait y avoir qu'un seul utilisateur connecté à la fois
            self.connected_owner = Owner.select().where(Owner.is_identified == True).order_by(Owner.last_login.desc()).first()
            
            # Afficher le nom de l'utilisateur dans le titre du menu
            if self.connected_owner:
                menu_title = f"👤 {self.connected_owner.username}"
            else:
                menu_title = "👤 Utilisateur"
            
            self.user_menu = self.addMenu(menu_title)
            
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
                
                # Dernière connexion (si disponible)
                if hasattr(self.connected_owner, 'last_login') and self.connected_owner.last_login:
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
            else:
                # Afficher un message si aucun utilisateur n'est connecté
                no_user_action = QAction(
                    QIcon(f"{CConstants.img_cmedia}user_deactive.png"),
                    "Aucun utilisateur connecté",
                    self
                )
                no_user_action.setEnabled(False)
                self.user_menu.addAction(no_user_action)
        except Exception as e:
            logger.error(f"Erreur lors de l'ajout des informations utilisateur: {e}")
            # Créer le menu même en cas d'erreur
            if not hasattr(self, 'user_menu'):
                self.user_menu = self.addMenu("👤 Utilisateur")
        
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
            # Utiliser is_identified pour trouver l'utilisateur connecté
            ow = Owner.select().where(Owner.is_identified == True)
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
        # Gestion du menu administrateur - Tous les administrateurs doivent avoir accès
        try:
            # Récupérer l'utilisateur connecté
            connected_owner = Owner.select().where(Owner.is_identified == True).first()
            
            if connected_owner:
                logger.debug(f"Utilisateur connecté - groupe: {connected_owner.group}, Admin requis: {Owner.ADMIN}")
                
                # Vérifier si l'utilisateur est administrateur (ADMIN ou SUPERUSER)
                if connected_owner.group in [Owner.ADMIN, Owner.SUPERUSER]:
                    admin_ = QAction(
                        QIcon.fromTheme("", QIcon(f"{CConstants.img_cmedia}settings.png")),
                        "Gestion Administration",
                        self,
                    )
                    admin_.setShortcut("Ctrl+G")
                    admin_.triggered.connect(self.goto_admin)
                    preference.addAction(admin_)
                    logger.debug("Menu d'administration ajouté avec succès pour l'administrateur")
                else:
                    logger.debug(f"Accès administrateur refusé - groupe: {connected_owner.group}, requis: {Owner.ADMIN} ou {Owner.SUPERUSER}")
            else:
                logger.debug("Aucun utilisateur connecté - menu admin non ajouté")
        except Exception as e:
            logger.error(f"Erreur lors de l'ajout du menu administrateur: {e}")
            # En cas d'erreur, essayer quand même d'ajouter le menu si un utilisateur existe
            try:
                connected_owner = Owner.select().where(Owner.is_identified == True).first()
                if connected_owner and connected_owner.group in [Owner.ADMIN, Owner.SUPERUSER]:
                    admin_ = QAction(
                        QIcon.fromTheme("", QIcon(f"{CConstants.img_cmedia}settings.png")),
                        "Gestion Administration",
                        self,
                    )
                    admin_.setShortcut("Ctrl+G")
                    admin_.triggered.connect(self.goto_admin)
                    preference.addAction(admin_)
            except:
                pass
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
    def update_user_menu(self):
        """Met à jour le menu utilisateur avec l'utilisateur connecté"""
        try:
            # Récupérer l'utilisateur connecté avec is_identified
            # Si plusieurs utilisateurs sont identifiés (ne devrait pas arriver), prendre celui avec la dernière connexion
            self.connected_owner = Owner.select().where(Owner.is_identified == True).order_by(Owner.last_login.desc()).first()
            
            # Ne pas utiliser de fallback - afficher uniquement l'utilisateur réellement connecté
            # Le fallback vers le premier utilisateur actif causait l'affichage du superuser au lieu de l'utilisateur connecté
            
            # Afficher le nom de l'utilisateur dans le titre du menu (toujours afficher quelque chose)
            if self.connected_owner:
                menu_title = f"👤 {self.connected_owner.username}"
            else:
                menu_title = "👤 Utilisateur"
            
            # Créer ou mettre à jour le menu
            if not hasattr(self, 'user_menu'):
                self.user_menu = self.addMenu(menu_title)
            else:
                self.user_menu.setTitle(menu_title)
            
            # Vider le menu existant
            self.user_menu.clear()
            
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
                
                # Dernière connexion (si disponible)
                if hasattr(self.connected_owner, 'last_login') and self.connected_owner.last_login:
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
            else:
                # Afficher un message si aucun utilisateur n'est connecté
                no_user_action = QAction(
                    QIcon(f"{CConstants.img_cmedia}user_deactive.png"),
                    "Aucun utilisateur connecté",
                    self
                )
                no_user_action.setEnabled(False)
                self.user_menu.addAction(no_user_action)
        except Exception as e:
            logger.error(f"Erreur lors de la mise à jour du menu utilisateur: {e}")
            # Créer le menu même en cas d'erreur
            if not hasattr(self, 'user_menu'):
                self.user_menu = self.addMenu("👤 Utilisateur")
        
        # Mettre à jour le menu administration après la mise à jour du menu utilisateur
        self.update_admin_menu()

    def update_admin_menu(self):
        """Met à jour le menu administration selon les droits de l'utilisateur connecté"""
        try:
            # Trouver le menu Préférence
            preference_menu = None
            for action in self.actions():
                if action.menu() and action.text() == "&Préference":
                    preference_menu = action.menu()
                    break
            
            if not preference_menu:
                logger.warning("Menu Préférence non trouvé")
                return
            
            # Supprimer l'ancien menu administration s'il existe
            if hasattr(self, 'admin_menu_action'):
                try:
                    preference_menu.removeAction(self.admin_menu_action)
                except:
                    pass
            
            # Récupérer l'utilisateur connecté
            connected_owner = Owner.select().where(Owner.is_identified == True).order_by(Owner.last_login.desc()).first()
            
            if connected_owner:
                # Vérifier si l'utilisateur est administrateur (ADMIN ou SUPERUSER)
                if connected_owner.group in [Owner.ADMIN, Owner.SUPERUSER]:
                    # Ajouter le menu administration
                    admin_ = QAction(
                        QIcon.fromTheme("", QIcon(f"{CConstants.img_cmedia}settings.png")),
                        "Gestion Administration",
                        self,
                    )
                    admin_.setShortcut("Ctrl+G")
                    admin_.triggered.connect(self.goto_admin)
                    preference_menu.addAction(admin_)
                    self.admin_menu_action = admin_
                    logger.debug(f"Menu d'administration ajouté pour l'utilisateur {connected_owner.username} (groupe: {connected_owner.group})")
                else:
                    logger.debug(f"Accès administrateur refusé - groupe: {connected_owner.group}, requis: {Owner.ADMIN} ou {Owner.SUPERUSER}")
            else:
                logger.debug("Aucun utilisateur connecté - menu admin non ajouté")
        except Exception as e:
            logger.error(f"Erreur lors de la mise à jour du menu administration: {e}")

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
