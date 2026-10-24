#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu
# maintainer: Fad

from PyQt6.QtCore import Qt, QTimer, QEvent
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import (
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
from ..models import Settings
from .cmenubar import FMenuBar
from .cmenutoolbar import FMenuToolBar
from .common import FWidget
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

        # Charger les paramètres (créés si absents)
        self._settings = None
        try:
            self._settings = Settings.init_settings()
        except Exception as exc:
            logger.error(f"Impossible de charger Settings: {exc}")

        # Vérifier si un utilisateur est connecté

     
        # Initialiser le timer de vérification de session
        self.session_timer = QTimer(self)
        self.session_timer.timeout.connect(self.check_session)
        self.session_timer.start(60000)  # Vérifier toutes les minutes

        self.toolBar = QToolBar()
        self.toolBar.setMovable(True)

        # Pour statusBar
        try:
            self.status_bar = GStatusBar(self)
            self.setStatusBar(self.status_bar)
            # GStatusBar s'affiche seule si une mise à jour est disponible
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
        self.toolbar.setMovable(True)
        logger.debug("Barre d'outils initialisée")

        # Appliquer (position + visibilité) depuis Settings, puis écouter les déplacements
        self._apply_toolbar_settings()
        # Debounce pour éviter des écritures multiples pendant le drag
        self._pending_toolbar_position_save = False

        # Détection robuste (compatible PyQt5/Qt5): eventFilter sur les toolbars
        # + sauvegarde au closeEvent
        try:
            self.toolBar.installEventFilter(self)
            self.toolbar.installEventFilter(self)
        except Exception as exc:
            logger.debug(f"Impossible d'installer eventFilter sur toolbars: {exc}")

        # En plus de l'eventFilter, écouter les signaux Qt (selon plateformes, c'est parfois le seul fiable)
        try:
            self.toolBarAreaChanged.connect(self._on_tool_bar_area_changed)
        except Exception as exc:
            logger.debug(f"Impossible de connecter toolBarAreaChanged: {exc}")
        for tb in (self.toolBar, self.toolbar):
            try:
                tb.topLevelChanged.connect(lambda *_: self._schedule_toolbar_position_save())
            except Exception:
                pass
            try:
                tb.orientationChanged.connect(lambda *_: self._schedule_toolbar_position_save())
            except Exception:
                pass

        # Changer cette ligne pour utiliser ExamplePageWidget au lieu de TestViewWidget
        self.page = ExamplePageWidget  # ou TestViewWidget pour la page de test basique
        self.change_context(self.page)
        logger.debug("Contexte initial changé vers ExamplePageWidget")

    def _qt_area_from_settings(self, position: str) -> Qt.ToolBarArea:
        """Convertit Settings.toolbar_position en Qt.ToolBarArea."""
        if position == Settings.RIGHT:
            return Qt.ToolBarArea.RightToolBarArea
        if position == Settings.TOP:
            return Qt.ToolBarArea.TopToolBarArea
        if position == Settings.BOTTOM:
            return Qt.ToolBarArea.BottomToolBarArea
        return Qt.ToolBarArea.LeftToolBarArea

    def _settings_position_from_qt(self, area: Qt.ToolBarArea) -> str:
        """Convertit Qt.ToolBarArea en Settings.toolbar_position."""
        if area == Qt.ToolBarArea.RightToolBarArea:
            return Settings.RIGHT
        if area == Qt.ToolBarArea.TopToolBarArea:
            return Settings.TOP
        if area == Qt.ToolBarArea.BottomToolBarArea:
            return Settings.BOTTOM
        return Settings.LEFT

    def _apply_toolbar_settings(self):
        """Restaure l'état des toolbars depuis Settings."""
        try:
            settings = self._settings or Settings.init_settings()
        except Exception as exc:
            logger.error(f"Impossible d'initialiser Settings: {exc}")
            settings = None

        # Position
        pos = getattr(settings, "toolbar_position", Settings.LEFT) if settings else Settings.LEFT
        area = self._qt_area_from_settings(pos)
        self.addToolBar(area, self.toolBar)
        self.addToolBar(area, self.toolbar)

        # Visibilité
        toolbar_enabled = bool(getattr(settings, "toolbar", True)) if settings else True
        self.toolBar.setVisible(toolbar_enabled)
        self.toolbar.setVisible(toolbar_enabled)

    def eventFilter(self, obj, event):
        """Capture le déplacement/reattachement des toolbars pour persister la position."""
        try:
            if obj in (getattr(self, "toolBar", None), getattr(self, "toolbar", None)):
                et = event.type()
                if et in (QEvent.Move, QEvent.ParentChange, QEvent.Show, QEvent.Hide):
                    self._schedule_toolbar_position_save()
        except Exception:
            pass
        return super().eventFilter(obj, event)

    def _schedule_toolbar_position_save(self):
        if self._pending_toolbar_position_save:
            return
        self._pending_toolbar_position_save = True
        QTimer.singleShot(200, self._persist_toolbar_position_from_ui)

    def _on_tool_bar_area_changed(self, *args):
        """Slot tolérant (signature PyQt5 variable selon build)."""
        try:
            # Qt5: (QToolBar*, Qt.ToolBarArea) ou parfois seulement (Qt.ToolBarArea)
            if len(args) == 2:
                toolbar, area = args
                if toolbar in (getattr(self, "toolBar", None), getattr(self, "toolbar", None)):
                    # Orientation cohérente
                    try:
                        orient = Qt.Orientation.Horizontal if area in (Qt.ToolBarArea.TopToolBarArea, Qt.ToolBarArea.BottomToolBarArea) else Qt.Orientation.Vertical
                        if getattr(self, "toolbar", None):
                            self.toolbar.setOrientation(orient)
                        if getattr(self, "toolBar", None):
                            self.toolBar.setOrientation(orient)
                    except Exception:
                        pass
            self._schedule_toolbar_position_save()
        except Exception:
            self._schedule_toolbar_position_save()

    def _persist_toolbar_position_from_ui(self):
        """Lit la position actuelle dans l'UI et l'enregistre dans Settings."""
        self._pending_toolbar_position_save = False
        try:
            # On prend la position de la toolbar principale de menu (FMenuToolBar) si possible.
            tb = getattr(self, "toolbar", None) or getattr(self, "toolBar", None)
            if tb is None:
                return

            area = self.toolBarArea(tb)

            # Orientation cohérente
            try:
                orient = Qt.Orientation.Horizontal if area in (Qt.ToolBarArea.TopToolBarArea, Qt.ToolBarArea.BottomToolBarArea) else Qt.Orientation.Vertical
                if getattr(self, "toolbar", None):
                    self.toolbar.setOrientation(orient)
                if getattr(self, "toolBar", None):
                    self.toolBar.setOrientation(orient)
            except Exception:
                pass

            settings = self._settings or Settings.init_settings()
            new_pos = self._settings_position_from_qt(area)
            if getattr(settings, "toolbar_position", None) == new_pos:
                return

            settings.toolbar_position = new_pos
            settings.save()
            self._settings = settings
            logger.info(f"✅ Position du menu enregistrée: {new_pos}")
        except Exception as exc:
            logger.error(f"Erreur sauvegarde position menu: {exc}")
        
    def logout(self):
        """Déconnecte l'utilisateur actuel"""
        from ..models import Owner
        try:
            # Mise à jour atomique de tous les utilisateurs connectés
            Owner.update(is_identified=False).where(Owner.is_identified).execute()
            logger.info("Déconnexion réussie de tous les utilisateurs")
        except Exception as e:
            logger.error(f"Erreur lors de la déconnexion: {e}")

    def exit(self):
        """Bouton Exit / Quitter : même flux que la fermeture de la fenêtre."""
        logger.info("Fermeture de l'application (Exit)")
        self.close()

    def check_session(self):
        """Vérifie la validité de la session active"""
        from ..models import Owner, Settings
        settings = Settings.select().where(Settings.id == 1).first()
        
        if settings and settings.auth_required:
            connected_owner = Owner.select().where(Owner.is_identified).first()
            if connected_owner and not connected_owner.is_session_valid():
                logger.warning(f"Session expirée pour l'utilisateur: {connected_owner.username}")
                self.logout()
                self.show_login_dialog()

    def closeEvent(self, event):
        """Fermeture (croix / Quitter) : déconnexion + sauvegarde locale/USB + nettoyage."""
        try:
            logger.info("Fermeture de la fenêtre principale - nettoyage des threads")

            try:
                settings = Settings.select().where(Settings.id == 1).first()
                if settings and settings.auth_required:
                    logger.info("Déconnexion avant fermeture")
                    self.logout()
            except Exception as e:
                logger.error(f"Erreur lors de la déconnexion avant fermeture: {e}")

            if not getattr(self, "_exit_backup_done", False):
                try:
                    from ..exports import save_database_on_exit
                    self._exit_backup_done = True
                    logger.info("💾 Sauvegarde de la base de données avant fermeture...")
                    save_database_on_exit(max_backups=10, parent=self)
                except Exception as backup_error:
                    logger.warning(
                        f"Impossible d'effectuer la sauvegarde automatique: {backup_error}"
                    )

            # Sauvegarde finale (au cas où aucun event n'a été capturé pendant le drag)
            try:
                self._persist_toolbar_position_from_ui()
            except Exception:
                pass
            
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
        return login_dialog.exec()

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
            dlg.exec()
        except Exception as e:
            logger.error(f"❌ Impossible d'ouvrir les préférences: {e}")