#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu
# maintainer: Fad

from PyQt5.QtCore import Qt, QTimer, QSettings
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (
    QToolBar, 
    QVBoxLayout, 
    QHBoxLayout, 
    QLabel, 
    QPushButton, 
    QLineEdit, 
    QCheckBox, 
    QTextEdit,
    QGroupBox,
    QFormLayout,
    QMessageBox,
    QMainWindow,
    QDockWidget
)

from ..cstatic import CConstants, logger
from .cmenubar import FMenuBar
from .cmenutoolbar import FMenuToolBar
from .common import FMainWindow, FWidget
from .statusbar import GStatusBar
from ..updater import UpdaterInit
from .window import FWindow
from .login import LoginWidget


class TestViewWidget(FWidget):
    """Shows the home page"""

    def __init__(self, parent=0, *args, **kwargs):
        super(TestViewWidget, self).__init__(parent=parent, *args, **kwargs)
        self.parent = parent
        self.parentWidget().setWindowTitle(" Test")
        self.title = "Common page"
        logger.debug("Initialisation de TestViewWidget")


class ExamplePageWidget(FWidget):
    """Page exemple avec différents widgets de démonstration"""

    def __init__(self, parent=0, *args, **kwargs):
        super(ExamplePageWidget, self).__init__(parent=parent, *args, **kwargs)
        self.parent = parent
        self.parentWidget().setWindowTitle("Page Exemple")
        self.title = "Page Exemple"
        
        self.setup_ui()
        logger.debug("Initialisation de ExamplePageWidget")

    def setup_ui(self):
        """Configuration de l'interface utilisateur"""
        main_layout = QVBoxLayout()
        
        # Titre principal
        title_label = QLabel("Page Exemple - Démonstration des Widgets")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; margin: 10px;")
        main_layout.addWidget(title_label)
        
        # Groupe de widgets de base
        self.create_basic_widgets_group(main_layout)
        
        # Groupe de formulaire
        self.create_form_group(main_layout)
        
        # Groupe de boutons d'action
        self.create_action_buttons_group(main_layout)
        
        self.setLayout(main_layout)

    def create_basic_widgets_group(self, parent_layout):
        """Créer le groupe des widgets de base"""
        group_box = QGroupBox("Widgets de Base")
        layout = QVBoxLayout()
        
        # Checkbox
        self.checkbox = QCheckBox("Option activée")
        self.checkbox.setChecked(True)
        layout.addWidget(self.checkbox)
        
        # Champ de texte simple
        h_layout = QHBoxLayout()
        h_layout.addWidget(QLabel("Texte simple:"))
        self.line_edit = QLineEdit()
        self.line_edit.setPlaceholderText("Saisissez du texte ici...")
        h_layout.addWidget(self.line_edit)
        layout.addLayout(h_layout)
        
        group_box.setLayout(layout)
        parent_layout.addWidget(group_box)

    def create_form_group(self, parent_layout):
        """Créer le groupe de formulaire"""
        group_box = QGroupBox("Formulaire Exemple")
        form_layout = QFormLayout()
        
        # Champ nom
        self.name_field = QLineEdit()
        form_layout.addRow("Nom:", self.name_field)
        
        # Champ email
        self.email_field = QLineEdit()
        self.email_field.setPlaceholderText("exemple@email.com")
        form_layout.addRow("Email:", self.email_field)
        
        # Zone de texte
        self.text_area = QTextEdit()
        self.text_area.setMaximumHeight(100)
        self.text_area.setPlaceholderText("Commentaires ou notes...")
        form_layout.addRow("Commentaires:", self.text_area)
        
        group_box.setLayout(form_layout)
        parent_layout.addWidget(group_box)

    def create_action_buttons_group(self, parent_layout):
        """Créer le groupe de boutons d'action"""
        group_box = QGroupBox("Actions")
        layout = QHBoxLayout()
        
        # Bouton de validation
        validate_btn = QPushButton("Valider")
        validate_btn.setStyleSheet("background-color: #4CAF50; color: white;")
        validate_btn.clicked.connect(self.on_validate)
        layout.addWidget(validate_btn)
        
        # Bouton d'effacement
        clear_btn = QPushButton("Effacer")
        clear_btn.setStyleSheet("background-color: #f44336; color: white;")
        clear_btn.clicked.connect(self.on_clear)
        layout.addWidget(clear_btn)
        
        # Bouton d'information
        info_btn = QPushButton("Info")
        info_btn.setStyleSheet("background-color: #2196F3; color: white;")
        info_btn.clicked.connect(self.on_info)
        layout.addWidget(info_btn)
        
        group_box.setLayout(layout)
        parent_layout.addWidget(group_box)

    def on_validate(self):
        """Action de validation"""
        name = self.name_field.text()
        email = self.email_field.text()
        comments = self.text_area.toPlainText()
        is_checked = self.checkbox.isChecked()
        
        if not name:
            QMessageBox.warning(self, "Attention", "Le champ nom est requis!")
            return
        
        message = f"Données validées:\n\nNom: {name}\nEmail: {email}\nOption activée: {'Oui' if is_checked else 'Non'}"
        if comments:
            message += f"\nCommentaires: {comments}"
        
        QMessageBox.information(self, "Validation", message)
        logger.info(f"Données validées pour {name}")

    def on_clear(self):
        """Action d'effacement"""
        self.name_field.clear()
        self.email_field.clear()
        self.text_area.clear()
        self.line_edit.clear()
        self.checkbox.setChecked(False)
        
        QMessageBox.information(self, "Effacement", "Tous les champs ont été effacés!")
        logger.info("Champs effacés dans ExamplePageWidget")

    def on_info(self):
        """Action d'information"""
        info_text = """
        Cette page exemple démontre l'utilisation de différents widgets PyQt5:
        
        • QGroupBox pour organiser les widgets
        • QLabel pour afficher du texte
        • QLineEdit pour la saisie de texte simple
        • QTextEdit pour la saisie de texte multiligne
        • QCheckBox pour les options booléennes
        • QPushButton pour les actions
        • QFormLayout pour les formulaires
        • QMessageBox pour les dialogues
        
        Développé avec PyQt5 et Python.
        """
        
        QMessageBox.about(self, "À propos de cette page", info_text)
        logger.info("Information affichée dans ExamplePageWidget")


class CommonMainWindow(QMainWindow, FWindow):
    def __init__(self, parent=None, *args, **kwargs):
        super().__init__(parent=parent, *args, **kwargs)

        self.setWindowIcon(QIcon(f"{CConstants.APP_LOGO}"))
        self.setWindowTitle(f"{CConstants.APP_NAME} {CConstants.APP_VERSION}")

        # Vérifier si un utilisateur est connecté

     
        # Initialiser le timer de vérification de session
        self.session_timer = QTimer(self)
        self.session_timer.timeout.connect(self.check_session)
        self.session_timer.start(60000)  # Vérifier toutes les minutes

        # NOTE:
        # - `self.toolBar` (QToolBar) et `self.toolbar` (FMenuToolBar) co-existent dans ce projet.
        # - On leur donne des objectName stables pour permettre saveState/restoreState.
        self.toolBar = QToolBar()
        self.toolBar.setObjectName("CommonMainWindow.toolBar")
        self.addToolBar(Qt.LeftToolBarArea, self.toolBar)

        # Pour statusBar
        try:
            self.status_bar = GStatusBar(self)
            self.setStatusBar(self.status_bar)
            # Enregistrer l'instance pour le nettoyage
            try:
                from ..cmain import register_statusbar_instance
                register_statusbar_instance(self.status_bar)
            except ImportError:
                logger.warning("Impossible d'enregistrer la statusbar pour le nettoyage")
        except Exception as exc:
            logger.warning(f"Impossible d'initialiser la barre de statut: {exc}")
            self.status_bar = None

        # Pour l'updater
        try:
            self.updater = UpdaterInit()
            # Enregistrer l'instance pour le nettoyage
            try:
                from ..cmain import register_updater_instance
                register_updater_instance(self.updater)
            except ImportError:
                logger.warning("Impossible d'enregistrer l'updater pour le nettoyage")
        except Exception as exc:
            logger.warning(f"Impossible d'initialiser l'updater: {exc}")
            self.updater = None

        self.menubar = FMenuBar(self)
        self.setMenuBar(self.menubar)
        logger.debug("Barre de menu initialisée")

        self.toolbar = FMenuToolBar(self)
        self.toolbar.setObjectName("CommonMainWindow.menuToolBar")
        self.addToolBar(Qt.LeftToolBarArea, self.toolbar)
        logger.debug("Barre d'outils initialisée")

        # Appliquer la configuration (position/visibilité) puis restaurer l'état sauvegardé (si existe)
        self._apply_toolbar_settings()
        QTimer.singleShot(0, self._restore_window_state)

        # Sauvegarde "à chaud" dès qu'un élément bouge (au mieux-effort)
        self._connect_state_persistence_signals()

        # Changer cette ligne pour utiliser ExamplePageWidget au lieu de TestViewWidget
        self.page = ExamplePageWidget  # ou TestViewWidget pour la page de test basique
        self.change_context(self.page)
        logger.debug("Contexte initial changé vers ExamplePageWidget")

    def _settings(self) -> QSettings:
        # Garder un nom stable (évite que le changement de APP_NAME casse la restauration)
        return QSettings("qt_common", "qt_common")

    def _toolbar_area_from_settings_value(self, value: str) -> Qt.ToolBarArea:
        try:
            from ..models import Settings
        except Exception:
            Settings = None

        v = (value or "").lower().strip()
        if Settings is not None:
            if v == Settings.RIGHT:
                return Qt.RightToolBarArea
            if v == Settings.TOP:
                return Qt.TopToolBarArea
            if v == Settings.BOTTOM:
                return Qt.BottomToolBarArea
        # Défaut / gauche
        return Qt.LeftToolBarArea

    def _apply_toolbar_settings(self):
        """Applique les paramètres en base: visibilité + position du menu vertical."""
        try:
            from ..models import Settings

            st = Settings.init_settings()
            toolbar_enabled = bool(getattr(st, "toolbar", True))
            toolbar_pos = getattr(st, "toolbar_position", Settings.LEFT)

            # Visibilité
            self.toolbar.setVisible(toolbar_enabled)

            # Position (uniquement si la toolbar est visible)
            if toolbar_enabled:
                area = self._toolbar_area_from_settings_value(toolbar_pos)
                # Déplacer la toolbar (remove/add pour forcer l'area)
                try:
                    self.removeToolBar(self.toolbar)
                except Exception:
                    pass
                self.addToolBar(area, self.toolbar)

        except Exception as e:
            logger.debug(f"Impossible d'appliquer les paramètres de toolbar: {e}")

    def _restore_window_state(self):
        """Restaure la géométrie + l'état (toolbars/docks) si disponible."""
        try:
            s = self._settings()
            geo = s.value("CommonMainWindow/geometry")
            state = s.value("CommonMainWindow/state")

            if geo is not None:
                # PyQt peut retourner QByteArray ou str selon backend; restoreGeometry gère QByteArray
                self.restoreGeometry(geo)
            if state is not None:
                self.restoreState(state)
        except Exception as e:
            logger.debug(f"Restauration état fenêtre ignorée: {e}")

    def _save_window_state(self):
        """Sauvegarde la géométrie + l'état (toolbars/docks)."""
        try:
            s = self._settings()
            s.setValue("CommonMainWindow/geometry", self.saveGeometry())
            s.setValue("CommonMainWindow/state", self.saveState())
            s.sync()
        except Exception as e:
            logger.debug(f"Sauvegarde état fenêtre ignorée: {e}")

    def _connect_state_persistence_signals(self):
        """Connecte des signaux pour sauvegarder dès qu'on déplace/masque la toolbar."""
        try:
            for tb in (getattr(self, "toolBar", None), getattr(self, "toolbar", None)):
                if tb is None:
                    continue
                # Changements courants
                try:
                    tb.topLevelChanged.connect(lambda _=None: self._save_window_state())
                except Exception:
                    pass
                try:
                    tb.visibilityChanged.connect(lambda _=None: self._save_window_state())
                except Exception:
                    pass
                try:
                    tb.orientationChanged.connect(lambda _=None: self._save_window_state())
                except Exception:
                    pass

            # Si le signal existe côté QMainWindow (selon binding/Qt), on l'utilise aussi
            sig = getattr(self, "toolBarAreaChanged", None)
            if sig is not None:
                try:
                    sig.connect(lambda *args: self._save_window_state())
                except Exception:
                    pass
        except Exception as e:
            logger.debug(f"Impossible de connecter les signaux de persistance: {e}")
        
    def logout(self):
        """Déconnecte l'utilisateur actuel"""
        from ..models import Owner
        try:
            # Mise à jour atomique de tous les utilisateurs connectés
            Owner.update(is_identified=False).where(Owner.is_identified == True).execute()
            logger.info("Déconnexion réussie de tous les utilisateurs")
        except Exception as e:
            logger.error(f"Erreur lors de la déconnexion: {e}")

    def exit(self):
        """Ferme l'application en effectuant les nettoyages nécessaires"""
        import sys
        logger.info("Fermeture de l'application")
        from ..models import Settings
        try:
            settings = Settings.select().where(Settings.id == 1).first()
            if settings and settings.auth_required:
                logger.info("Déconnexion avant fermeture")
                self.logout()
        except Exception as e:
            logger.error(f"Erreur lors de la vérification des paramètres: {e}")
        
        self.close()
        sys.exit(0)

    def check_session(self):
        """Vérifie la validité de la session active"""
        from ..models import Owner, Settings
        settings = Settings.select().where(Settings.id == 1).first()
        
        if settings and settings.auth_required:
            connected_owner = Owner.select().where(Owner.is_identified == True).first()
            if connected_owner and not connected_owner.is_session_valid():
                logger.warning(f"Session expirée pour l'utilisateur: {connected_owner.username}")
                self.logout()
                self.show_login_dialog()

    def closeEvent(self, event):
        """Override closeEvent pour nettoyer les threads avant fermeture"""
        try:
            logger.info("Fermeture de la fenêtre principale - nettoyage des threads")

            # Sauvegarder la position/état avant fermeture
            self._save_window_state()
            
            # Nettoyer manuellement les instances si elles existent
            if hasattr(self, 'status_bar') and self.status_bar:
                if hasattr(self.status_bar, 'cleanup'):
                    self.status_bar.cleanup()
                    
            if hasattr(self, 'updater') and self.updater:
                if hasattr(self.updater, 'cleanup'):
                    self.updater.cleanup()
                    
            # Arrêter le timer de session
            if hasattr(self, 'session_timer'):
                self.session_timer.stop()
        except Exception as e:
            logger.error(f"Erreur lors du nettoyage de la fenêtre principale: {e}")
        finally:
            super().closeEvent(event)

    def page_width(self):
        return self.width() - 100

    def show_login_dialog(self):
        """Affiche la boîte de dialogue de connexion"""
        login_dialog = LoginWidget(self)
        # Connecter le signal de connexion réussie
        login_dialog.login_successful.connect(lambda: self.refresh_interface())
        return login_dialog.exec_()

    def refresh_menu_bar(self):
        """Rafraîchit la barre de menu après la connexion"""
        # Supprimer les menus existants
        self.menubar.clear()
        
        # Recréer les menus avec les permissions mises à jour
        self.create_menus()

    def refresh_interface(self):
        """Rafraîchit l'interface complète après la connexion"""
        try:
            # Rafraîchir la barre de menu
            self.refresh_menu_bar()
            
            # Rafraîchir la barre de statut
            if hasattr(self, 'status_bar') and self.status_bar:
                # Vérifier si la méthode refresh existe avant de l'appeler
                if hasattr(self.status_bar, 'refresh') and callable(getattr(self.status_bar, 'refresh')):
                    try:
                        self.status_bar.refresh()
                    except Exception as e:
                        logger.debug(f"Erreur lors du rafraîchissement de la barre de statut: {e}")
                else:
                    # Si la méthode refresh n'existe pas, faire juste un update/repaint
                    try:
                        self.status_bar.update()
                        self.status_bar.repaint()
                    except Exception as e:
                        logger.debug(f"Erreur lors de la mise à jour de la barre de statut: {e}")
            
            # Rafraîchir le widget central si nécessaire
            if hasattr(self, 'central_widget'):
                self.central_widget.refresh()
            
            # Rafraîchir les dock widgets si présents
            for dock in self.findChildren(QDockWidget):
                if hasattr(dock.widget(), 'refresh'):
                    dock.widget().refresh()
            
            # Forcer la mise à jour de l'interface
            self.update()
            
            logger.info("✅ Interface rafraîchie avec succès")
        except Exception as e:
            logger.error(f"❌ Erreur lors du rafraîchissement de l'interface: {e}")

    def change_context(self, context=None):
        """Change le contexte de l'application"""
        try:
            if context:
                self.current_context = context
                logger.info(f"✅ Contexte changé: {context}")
                
                # Rafraîchir l'interface avec le nouveau contexte
                self.refresh_interface()
                
                # Mettre à jour la barre de statut si elle existe
                if hasattr(self, 'status_bar'):
                    self.status_bar.set_context(context)
                    
                return True
            return False
        except Exception as e:
            logger.error(f"❌ Erreur lors du changement de contexte: {e}")
            return False

    def create_menus(self):
        """Crée les menus de la barre de menu"""
        # Menu Fichier
        file_menu = self.menubar.addMenu("📁 Fichier")
        file_menu.addAction("🆕 Nouveau")
        file_menu.addAction("📂 Ouvrir")
        file_menu.addAction("💾 Enregistrer")
        file_menu.addSeparator()
        file_menu.addAction("🚪 Quitter")
        
        # Menu Édition
        edit_menu = self.menubar.addMenu("✏️ Édition")
        edit_menu.addAction("↩️ Annuler")
        edit_menu.addAction("↪️ Rétablir")
        edit_menu.addSeparator()
        edit_menu.addAction("✂️ Couper")
        edit_menu.addAction("📋 Copier")
        edit_menu.addAction("📝 Coller")
        
        # Menu Affichage
        view_menu = self.menubar.addMenu("👁️ Affichage")
        view_menu.addAction("🔍 Zoom avant")
        view_menu.addAction("🔍 Zoom arrière")
        view_menu.addAction("🔍 Zoom par défaut")
        
        # Menu Outils
        tools_menu = self.menubar.addMenu("🛠️ Outils")
        pref_action = tools_menu.addAction("⚙️ Préférences")
        pref_action.triggered.connect(self.open_preferences)
        tools_menu.addAction("🔄 Rafraîchir")
        
        # Menu Aide
        help_menu = self.menubar.addMenu("❓ Aide")
        help_menu.addAction("📚 Documentation")
        help_menu.addAction("ℹ️ À propos")

    def open_preferences(self):
        """Ouvre la fenêtre des préférences (qt_common)."""
        try:
            from .preferences import PreferencesDialog

            dlg = PreferencesDialog(self)
            dlg.exec_()
        except Exception as e:
            logger.error(f"❌ Impossible d'ouvrir les préférences: {e}")