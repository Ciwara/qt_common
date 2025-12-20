#!/usr/bin/env python
# -*- coding: utf8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu
# maintainer: Fad


from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QIcon, QPixmap
from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDoubleSpinBox,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QSplitter,
    QTextEdit,
    QVBoxLayout,
)

from ..models import Organization, Owner, Settings
from ..tabpane import tabbox
from .common import (
    Button,
    ButtonSave,
    FLabel,
    FormLabel,
    FWidget,
    IntLineEdit,
    LineEdit,
)
from .table import FTableWidget
from .user_add_or_edit import NewOrEditUserViewWidget
from .util import check_is_empty

try:
    from ..cstatic import CConstants, logger
except Exception as e:
    print(e)
try:
    unicode
except NameError:
    unicode = str

# Fonction d'internationalisation simple
def _(text):
    """Fonction d'internationalisation simple - peut être remplacée par gettext"""
    return text

class AdminViewWidget(FWidget):
    def __init__(self, parent=None, *args, **kwargs):
        super(AdminViewWidget, self).__init__(parent=parent, *args, **kwargs)

        self.parent = parent

        parent_widget = self.parentWidget()
        if parent_widget and hasattr(parent_widget, 'setWindowTitle'):
            parent_widget.setWindowTitle(CConstants.APP_NAME + "    ADMINISTRATION")

        self.bttrestor = Button("Restaurer")
        self.bttrestor.clicked.connect(self.restorseleted)
        self.bttrestor.setEnabled(False)
        self.bttempty = Button("Vide")
        self.bttempty.clicked.connect(self.deletedseleted)
        self.bttempty.setEnabled(False)
        
        # Layout séparé pour l'historique
        history_table = QVBoxLayout()
        self.history_table = TrashTableWidget(parent=self)
        history_table.addWidget(self.history_table)

        # Layout séparé pour les paramètres
        table_settings = QVBoxLayout()
        self.table_settings = SettingsTableWidget(parent=self)
        table_settings.addWidget(self.table_settings)

        # Layout séparé pour la gestion des utilisateurs
        table_login = QVBoxLayout()
        self.table_login = LoginManageWidget(parent=self)
        table_login.addWidget(self.table_login)

        tab_widget = tabbox(
            (table_settings, "Paramètre"),
            (history_table, "Historique"),
            (table_login, "Gestion d'utilisateurs"),
        )

        vbox = QVBoxLayout()
        vbox.addWidget(tab_widget)
        self.setLayout(vbox)

    def enablebtt(self):
        self.bttrestor.setEnabled(True)
        self.bttempty.setEnabled(True)

    def restorseleted(self):
        for doc in self.history_table.getSelectTableItems():
            doc.isnottrash()
            self.history_table.refresh_()

    def deletedseleted(self):
        reply = QMessageBox.question(
            self,
            "Suppression definitive",
            self.tr("Voulez vous vraiment le supprimer?"),
            QMessageBox.StandardButton.Yes,
            QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            for doc in self.history_table.getSelectTableItems():
                doc.remove_doc()
                self.history_table.refresh_()


class TrashTableWidget(FTableWidget):
    def __init__(self, parent, *args, **kwargs):
        FTableWidget.__init__(self, parent=parent, *args, **kwargs)

        self.parent = parent

        self.hheaders = [
            _("Selection"),
            _("Date"),
            _("categorie"),
            _("Description"),
        ]
        self.stretch_columns = [0]
        self.align_map = {0: "l"}
        self.ecart = -5
        self.display_vheaders = False
        self.display_fixed = True

        self.refresh_()

    def refresh_(self):
        self._reset()
        self.set_data_for()
        self.refresh()

    def set_data_for(self):
        self.data = []
        # self.data = [("", record.date, record.category, record.description)
        # for record in Records.select().where(Records.trash ==
        # True).order_by(Records.category.asc())]

    def getSelectTableItems(self):
        n = self.rowCount()
        ldata = []
        for i in range(n):
            item = self.cellWidget(i, 0)
            if not item:
                pass
            elif item.checkState() == Qt.CheckState.Checked:
                ldata.append("ee")
                # ldata.append(Records.filter(description=str(self.item(i,
                # 3).text())).get())
        return ldata

    def _item_for_data(self, row, column, data, context=None):
        if column == 0:
            # create check box as our editor.
            editor = QCheckBox()
            if data == 2:
                editor.setCheckState(2)
            editor.stateChanged.connect(self.parent.enablebtt)
            return editor
        return super(TrashTableWidget, self)._item_for_data(row, column, data, context)

    def click_item(self, row, column, *args):
        pass


class OrganizationTableWidget(FWidget):
    def __init__(self, parent, *args, **kwargs):
        super(FWidget, self).__init__(parent=parent, *args, **kwargs)

        # Récupération sécurisée de l'organisation
        try:
            self.organization = Organization.get(id=1)
        except Organization.DoesNotExist:
            logger.warning("Organisation avec id=1 non trouvée, création d'une nouvelle")
            self.organization = Organization.create(
                id=1,
                name_orga="Mon Organisation",
                phone=0,
                bp="",
                email_org="",
                adress_org="",
                logo_orga=""
            )
        except Exception as e:
            logger.error(f"Erreur lors de la récupération de l'organisation: {e}")
            # Valeurs par défaut
            self.organization = type('MockOrganization', (), {
                'logo_orga': '',
                'name_orga': 'Mon Organisation',
                'phone': 0,
                'bp': '',
                'email_org': '',
                'adress_org': ''
            })()
        
        self.parent = parent
        vbox = QVBoxLayout()
        # vbox.addWidget(FPageTitle(u"Utilisateur: %s " %
        # self.organisation.name_orga))

        # self.liste_devise = Organization.DEVISE
        # Combobox widget

        # self.checked = QCheckBox("Active")
        # if self.organization.auth_required:
        #     self.checked.setCheckState(Qt.CheckState.Checked)
        # self.checked.setToolTip(
        #     u"""Cocher si vous voulez pour deactive
        #                         le login continue à utiliser le systeme"""
        # )

        self.bn_upload = Button("logo de l'organisation")
        self.bn_upload.setIcon(
            QIcon.fromTheme("", QIcon("{}db.png".format(CConstants.img_cmedia)))
        )
        self.bn_upload.clicked.connect(self.upload_logo)

        self.logo_orga = LineEdit(str(self.organization.logo_orga or ""))
        self.name_orga = LineEdit(str(self.organization.name_orga or ""))
        self.phone = IntLineEdit(str(self.organization.phone or "0"))
        self.phone.setMaximumWidth(250)
        self.bp = LineEdit(str(self.organization.bp or ""))
        self.bp.setMaximumWidth(250)
        self.adress_org = QTextEdit(str(self.organization.adress_org or ""))
        self.email_org = LineEdit(str(self.organization.email_org or ""))
        self.email_org.setMaximumWidth(250)

        formbox = QFormLayout()
        formbox.addRow(self.bn_upload, self.logo_orga)
        formbox.addRow(FormLabel("Nom de l'organisation:"), self.name_orga)
        formbox.addRow(FormLabel("Tel:"), self.phone)
        formbox.addRow(FormLabel("B.P:"), self.bp)
        formbox.addRow(FormLabel("E-mail:"), self.email_org)
        formbox.addRow(FormLabel("Adresse complete:"), self.adress_org)

        butt = ButtonSave("Enregistrer")
        butt.clicked.connect(self.save_edit)
        formbox.addRow("", butt)

        vbox.addLayout(formbox)
        self.setLayout(vbox)

    def upload_logo(self):
        from exports import upload_file

        upload_file(folder="C://", dst_folder=CConstants.ARMOIRE)
        self.accept()

    def save_edit(self):
        """add operation"""
        name_orga = unicode(self.name_orga.text())
        if check_is_empty(self.name_orga):
            return

        if check_is_empty(self.phone):
            return

        try:
            orga = Organization.get(id=1)
        except Organization.DoesNotExist:
            orga = Organization.create(id=1)
        
        orga.name_orga = name_orga
        orga.phone = unicode(self.phone.text())
        orga.email_org = unicode(self.email_org.text())
        orga.bp = unicode(self.bp.text())
        orga.adress_org = unicode(self.adress_org.toPlainText())
        orga.save()

        print(f"{self.parent=}")
        if hasattr(self.parent, 'parent') and hasattr(self.parent.parent, 'Notify'):
            self.parent.parent.Notify(
                "Le Compte %s a été mise à jour" % orga.name_orga, "success"
            )
        else:
            logger.info(f"Organisation {orga.name_orga} mise à jour avec succès")


class LoginManageWidget(FWidget):
    def __init__(self, parent, *args, **kwargs):
        super(FWidget, self).__init__(parent=parent, *args, **kwargs)
        parent_widget = self.parentWidget()
        if parent_widget and hasattr(parent_widget, 'setWindowTitle'):
            parent_widget.setWindowTitle("Gestion des Utilisateurs")
        self.parent = parent

        # Widget pour la liste des utilisateurs avec recherche
        users_list_widget = QVBoxLayout()
        
        # Barre de recherche
        search_layout = QHBoxLayout()
        search_label = QLabel("🔍 Rechercher:")
        self.search_field = LineEdit()
        self.search_field.setPlaceholderText("Rechercher un utilisateur...")
        self.search_field.textChanged.connect(self.filter_users)
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.search_field)
        users_list_widget.addLayout(search_layout)
        
        # Statistiques
        self.stats_label = QLabel()
        self.stats_label.setStyleSheet("font-weight: bold; color: #2c3e50; padding: 5px;")
        users_list_widget.addWidget(self.stats_label)
        
        # Liste des utilisateurs
        self.table_owner = OwnerTableWidget(parent=self)
        self.table_owner.setFixedWidth(350)
        users_list_widget.addWidget(self.table_owner)
        
        # Container pour la liste
        users_container = FWidget()
        users_container.setLayout(users_list_widget)
        
        # Widget d'information et opérations
        self.table_info = InfoTableWidget(parent=self)
        self.operation = OperationWidget(parent=self)
        self.operation.setFixedHeight(120)

        splitterH = QSplitter(Qt.Orientation.Horizontal)
        splitterH.addWidget(users_container)

        splitterV = QSplitter(Qt.Orientation.Vertical)
        splitterV.addWidget(self.operation)
        splitterV.addWidget(self.table_info)
        splitterH.addWidget(splitterV)
        vbox = QHBoxLayout(self)
        vbox.addWidget(splitterH)
        self.setLayout(vbox)
        
        # Mettre à jour les statistiques
        self.update_stats()
    
    def filter_users(self, text):
        """Filtre les utilisateurs selon le texte de recherche"""
        search_text = text.lower().strip()
        for i in range(self.table_owner.count()):
            item = self.table_owner.item(i)
            if item:
                # Toujours afficher l'en-tête
                if isinstance(item, OwnerQListWidgetItem) and isinstance(item.owner, int):
                    item.setHidden(False)
                elif isinstance(item, OwnerQListWidgetItem):
                    owner = item.owner
                    if owner:
                        # Rechercher dans le nom d'utilisateur, téléphone, groupe
                        username_match = owner.username.lower() if owner.username else ""
                        phone_match = owner.phone.lower() if owner.phone else ""
                        group_match = owner.group.lower() if owner.group else ""
                        
                        matches = (
                            search_text in username_match or
                            search_text in phone_match or
                            search_text in group_match
                        )
                        item.setHidden(not matches)
    
    def update_stats(self):
        """Met à jour les statistiques des utilisateurs"""
        try:
            all_users = list(Owner.get_non_superusers())
            active_users = [u for u in all_users if u.isactive]
            inactive_users = [u for u in all_users if not u.isactive]
            admins = [u for u in all_users if u.group == Owner.ADMIN]
            regular_users = [u for u in all_users if u.group == Owner.USER]
            
            stats_text = (
                f"📊 Statistiques: "
                f"Total: {len(all_users)} | "
                f"✅ Actifs: {len(active_users)} | "
                f"❌ Inactifs: {len(inactive_users)} | "
                f"👑 Admins: {len(admins)} | "
                f"👤 Utilisateurs: {len(regular_users)}"
            )
            self.stats_label.setText(stats_text)
        except Exception as e:
            logger.error(f"Erreur lors de la mise à jour des statistiques: {e}")
            self.stats_label.setText("📊 Statistiques: Erreur de chargement")


class OperationWidget(FWidget):

    """Widget pour les opérations sur les utilisateurs"""

    def __init__(self, parent, *args, **kwargs):
        super(FWidget, self).__init__(parent=parent, *args, **kwargs)

        vbox = QVBoxLayout(self)
        hbox = QHBoxLayout()
        self.parent = parent

        # Bouton ajouter utilisateur
        self.add_ow_but = Button(_("➕ Ajouter"))
        self.add_ow_but.setIcon(
            QIcon.fromTheme("", QIcon("{}useradd.png".format(CConstants.img_cmedia)))
        )
        self.add_ow_but.setToolTip("Créer un nouvel utilisateur")
        self.add_ow_but.clicked.connect(self.add_owner)
        hbox.addWidget(self.add_ow_but)
        
        # Bouton rafraîchir
        self.refresh_but = Button(_("🔄 Actualiser"))
        self.refresh_but.setIcon(
            QIcon.fromTheme("", QIcon("{}find.png".format(CConstants.img_cmedia)))
        )
        self.refresh_but.setToolTip("Actualiser la liste des utilisateurs")
        self.refresh_but.clicked.connect(self.refresh_list)
        hbox.addWidget(self.refresh_but)
        
        vbox.addLayout(hbox)
        self.setLayout(vbox)

    def add_owner(self):
        self.parent.parent.open_dialog(
            NewOrEditUserViewWidget, modal=True, pp=self.parent.table_owner
        )
        # Mettre à jour les statistiques après ajout
        if hasattr(self.parent, 'update_stats'):
            self.parent.update_stats()
    
    def refresh_list(self):
        """Rafraîchit la liste des utilisateurs"""
        self.parent.table_owner.refresh_()
        if hasattr(self.parent, 'update_stats'):
            self.parent.update_stats()


class OwnerTableWidget(QListWidget):
    """Widget pour afficher la liste des utilisateurs"""

    def __init__(self, parent, *args, **kwargs):
        super(OwnerTableWidget, self).__init__(parent)
        self.parent = parent
        self.setAutoScroll(True)
        self.setAutoFillBackground(True)
        self.itemSelectionChanged.connect(self.handleClicked)
        self.refresh_()

    def refresh_(self):
        """Rafraîchit la liste des utilisateurs (sans les superusers)"""
        self.clear()
        # En-tête
        self.addItem(OwnerQListWidgetItem(-1))
        
        # Trier les utilisateurs : actifs d'abord, puis par nom
        owners = list(Owner.get_non_superusers())
        owners.sort(key=lambda x: (not x.isactive, x.username.lower()))
        
        for owner in owners:
            self.addItem(OwnerQListWidgetItem(owner))
        
        # Mettre à jour les statistiques si disponible
        if hasattr(self.parent, 'update_stats'):
            self.parent.update_stats()

    def handleClicked(self):
        owner_item = self.currentItem()
        if not owner_item or isinstance(owner_item.owner, int):
            return
        self.parent.table_info.edit_ow_but.setEnabled(True)
        self.parent.table_info.delete_ow_but.setEnabled(True)
        self.parent.table_info.toggle_active_but.setEnabled(True)
        self.parent.table_info.refresh_(owner_item.owner)


class OwnerQListWidgetItem(QListWidgetItem):
    def __init__(self, owner):
        super(OwnerQListWidgetItem, self).__init__()

        self.owner = owner

        if isinstance(owner, int):
            logo = ""
        else:
            logo = "user_active" if self.owner.isactive else "user_deactive"
        icon = QIcon()
        icon.addPixmap(
            QPixmap("{}{}.png".format(CConstants.img_cmedia, logo)),
            QIcon.Mode.Normal,
            QIcon.State.Off,
        )
        self.setIcon(icon)
        self.init_text()

    def init_text(self):
        try:
            # Afficher plus d'informations dans la liste
            status_icon = "✅" if self.owner.isactive else "❌"
            group_icon = "👑" if self.owner.group == Owner.ADMIN else "👤"
            connected_icon = "🔓" if self.owner.is_identified else ""
            
            display_text = f"{status_icon} {group_icon} {self.owner.username} {connected_icon}"
            self.setText(display_text)
            
            # Tooltip avec plus d'informations
            tooltip = (
                f"👤 {self.owner.username}\n"
                f"🎭 Groupe: {self.owner.group}\n"
                f"📞 Téléphone: {self.owner.phone or 'Non renseigné'}\n"
                f"✅ Statut: {'Actif' if self.owner.isactive else 'Inactif'}\n"
                f"🔢 Connexions: {self.owner.login_count}"
            )
            if self.owner.last_login:
                try:
                    tooltip += f"\n🕒 Dernière connexion: {self.owner.last_login.strftime('%d/%m/%Y %H:%M')}"
                except (AttributeError, ValueError, TypeError):
                    pass
            self.setToolTip(tooltip)
        except AttributeError:
            font = QFont()
            font.setBold(True)
            self.setFont(font)
            self.setTextAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignCenter)
            self.setText("👥 Utilisateurs")
            self.setToolTip("Liste des utilisateurs du système")

    @property
    def owner_id(self):
        try:
            return self.owner.id if hasattr(self.owner, 'id') else None
        except AttributeError:
            return None


class InfoTableWidget(FWidget):
    def __init__(self, parent, *args, **kwargs):
        super(FWidget, self).__init__(parent=parent, *args, **kwargs)

        self.parent = parent
        self.refresh()
        self.owner = None

        self.details = FLabel()
        
        # Boutons d'action
        buttons_layout = QHBoxLayout()
        
        self.edit_ow_but = Button("✏️ Modifier")
        self.edit_ow_but.setIcon(
            QIcon.fromTheme(
                "document-new", QIcon("{}edit_user.png".format(CConstants.img_cmedia))
            )
        )
        self.edit_ow_but.setEnabled(False)
        self.edit_ow_but.setToolTip("Modifier les informations de l'utilisateur")
        self.edit_ow_but.clicked.connect(self.edit_owner)
        buttons_layout.addWidget(self.edit_ow_but)
        
        # Bouton activer/désactiver
        self.toggle_active_but = Button("✅ Activer")
        self.toggle_active_but.setEnabled(False)
        self.toggle_active_but.setToolTip("Activer ou désactiver le compte utilisateur")
        self.toggle_active_but.clicked.connect(self.toggle_active)
        buttons_layout.addWidget(self.toggle_active_but)
        
        # Bouton supprimer
        self.delete_ow_but = Button("🗑️ Supprimer")
        self.delete_ow_but.setIcon(
            QIcon.fromTheme("", QIcon("{}del.png".format(CConstants.img_cmedia)))
        )
        self.delete_ow_but.setEnabled(False)
        self.delete_ow_but.setToolTip("Supprimer définitivement l'utilisateur")
        self.delete_ow_but.clicked.connect(self.delete_owner)
        self.delete_ow_but.setStyleSheet("background-color: #e74c3c; color: white;")
        buttons_layout.addWidget(self.delete_ow_but)

        vbox = QVBoxLayout()
        vbox.addLayout(buttons_layout)
        vbox.addWidget(self.details)
        self.setLayout(vbox)

    def refresh_(self, owner):
        self.refresh()
        self.owner = owner

        if isinstance(self.owner, int) or not self.owner:
            self.details.setText("<h3>Sélectionnez un utilisateur pour voir ses détails</h3>")
            return
        
        # Formatage amélioré des informations
        status_icon = "✅" if self.owner.isactive else "❌"
        status_text = "Actif" if self.owner.isactive else "Inactif"
        group_icon = "👑" if self.owner.group == Owner.ADMIN else "👤"
        
        # Formatage de la date de dernière connexion
        try:
            last_login_str = self.owner.last_login.strftime("%d/%m/%Y à %H:%M") if self.owner.last_login else "Jamais"
        except (AttributeError, ValueError, TypeError):
            last_login_str = "Non disponible"
        
        # Vérifier si l'utilisateur est actuellement connecté
        is_connected = "🔓 Connecté" if self.owner.is_identified else "🔒 Déconnecté"
        
        self.details.setText(
            f"""
            <div style="padding: 10px; background-color: #f8f9fa; border-radius: 5px;">
                <h2 style="color: #2c3e50; margin-bottom: 10px;">👤 {self.owner.username}</h2>
                <hr style="border: 1px solid #dee2e6;">
                <table style="width: 100%;">
                    <tr>
                        <td style="padding: 5px;"><b>Statut:</b></td>
                        <td style="padding: 5px;">{status_icon} {status_text}</td>
                    </tr>
                    <tr>
                        <td style="padding: 5px;"><b>Groupe:</b></td>
                        <td style="padding: 5px;">{group_icon} {self.owner.group}</td>
                    </tr>
                    <tr>
                        <td style="padding: 5px;"><b>📞 Téléphone:</b></td>
                        <td style="padding: 5px;">{self.owner.phone or 'Non renseigné'}</td>
                    </tr>
                    <tr>
                        <td style="padding: 5px;"><b>🕒 Dernière connexion:</b></td>
                        <td style="padding: 5px;">{last_login_str}</td>
                    </tr>
                    <tr>
                        <td style="padding: 5px;"><b>🔢 Nombre de connexions:</b></td>
                        <td style="padding: 5px;">{self.owner.login_count}</td>
                    </tr>
                    <tr>
                        <td style="padding: 5px;"><b>État de session:</b></td>
                        <td style="padding: 5px;">{is_connected}</td>
                    </tr>
                </table>
            </div>
            """
        )
        
        # Mettre à jour le bouton activer/désactiver
        if self.owner.isactive:
            self.toggle_active_but.setText("❌ Désactiver")
            self.toggle_active_but.setStyleSheet("background-color: #f39c12; color: white;")
        else:
            self.toggle_active_but.setText("✅ Activer")
            self.toggle_active_but.setStyleSheet("background-color: #27ae60; color: white;")

    def edit_owner(self):
        if not self.owner or isinstance(self.owner, int):
            return
        self.parent.parent.open_dialog(
            NewOrEditUserViewWidget,
            owner=self.owner,
            modal=True,
            pp=self.parent.table_owner,
        )
        # Rafraîchir après modification
        if hasattr(self.parent, 'update_stats'):
            self.parent.update_stats()
    
    def toggle_active(self):
        """Active ou désactive le compte utilisateur"""
        if not self.owner or isinstance(self.owner, int):
            return
        
        action = "désactiver" if self.owner.isactive else "activer"
        reply = QMessageBox.question(
            self,
            f"{'Désactiver' if self.owner.isactive else 'Activer'} le compte",
            f"Voulez-vous vraiment {action} le compte de l'utilisateur '{self.owner.username}' ?\n\n"
            f"{'Un compte désactivé ne pourra plus se connecter.' if self.owner.isactive else 'Le compte pourra à nouveau se connecter.'}",
            QMessageBox.StandardButton.Yes,
            QMessageBox.StandardButton.No,
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.owner.isactive = not self.owner.isactive
            self.owner.save()
            
            status_text = "activé" if self.owner.isactive else "désactivé"
            if hasattr(self.parent.parent, 'Notify'):
                self.parent.parent.Notify(
                    f"✅ Le compte de '{self.owner.username}' a été {status_text} avec succès",
                    "success"
                )
            
            # Rafraîchir l'affichage
            self.refresh_(self.owner)
            self.parent.table_owner.refresh_()
            if hasattr(self.parent, 'update_stats'):
                self.parent.update_stats()
    
    def delete_owner(self):
        """Supprime définitivement un utilisateur"""
        if not self.owner or isinstance(self.owner, int):
            return
        
        # Empêcher la suppression de l'utilisateur connecté
        if self.owner.is_identified:
            QMessageBox.warning(
                self,
                "⚠️ Suppression impossible",
                f"Impossible de supprimer l'utilisateur '{self.owner.username}' car il est actuellement connecté.\n\n"
                "Veuillez vous déconnecter avant de supprimer ce compte."
            )
            return
        
        reply = QMessageBox.question(
            self,
            "🗑️ Suppression définitive",
            f"⚠️ ATTENTION : Cette action est irréversible !\n\n"
            f"Voulez-vous vraiment supprimer définitivement l'utilisateur '{self.owner.username}' ?\n\n"
            f"Toutes les données associées à cet utilisateur seront perdues.",
            QMessageBox.StandardButton.Yes,
            QMessageBox.StandardButton.No,
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                username = self.owner.username
                self.owner.delete_instance()
                
                if hasattr(self.parent.parent, 'Notify'):
                    self.parent.parent.Notify(
                        f"✅ L'utilisateur '{username}' a été supprimé avec succès",
                        "success"
                    )
                
                # Réinitialiser l'affichage
                self.owner = None
                self.details.setText("<h3>Sélectionnez un utilisateur pour voir ses détails</h3>")
                self.edit_ow_but.setEnabled(False)
                self.delete_ow_but.setEnabled(False)
                self.toggle_active_but.setEnabled(False)
                
                # Rafraîchir la liste
                self.parent.table_owner.refresh_()
                if hasattr(self.parent, 'update_stats'):
                    self.parent.update_stats()
                    
            except Exception as e:
                logger.error(f"Erreur lors de la suppression de l'utilisateur: {e}")
                QMessageBox.critical(
                    self,
                    "❌ Erreur",
                    f"Une erreur est survenue lors de la suppression :\n{str(e)}"
                )


class SettingsTableWidget(FWidget):
    def __init__(self, parent, *args, **kwargs):
        super(FWidget, self).__init__(parent=parent, *args, **kwargs)

        # Utilisation sécurisée de Settings.init_settings()
        try:
            self.settings = Settings.init_settings()
            logger.debug("Paramètres chargés avec succès pour l'administration")
        except Exception as e:
            logger.error(f"Erreur lors du chargement des paramètres: {e}")
            # Créer un objet mock avec des valeurs par défaut
            self.settings = type('MockSettings', (), {
                'url': 'http://file-repo.ml',
                'theme': "default",
                'auth_required': True,
                'after_cam': 1,
                'devise': Settings.XOF,
                'toolbar_position': Settings.LEFT,
                'toolbar': True
            })()
        
        self.parent = parent
        vbox = QVBoxLayout()
        # self.slug_field =
        self.url_field = LineEdit(str(self.settings.url or "http://file-repo.ml"))
        
        # Thèmes désactivés - pas de sélection disponible
        self.list_theme = {}
        
        # Combobox widget désactivé
        self.box_theme = QComboBox()
        self.box_theme.setEnabled(False)
        self.box_theme.addItem("Non disponible")

        self.box_vilgule = QDoubleSpinBox()

        self.box_vilgule.setMaximum(4)
        after_cam_value = getattr(self.settings, 'after_cam', 1)
        self.after_cam = self.box_vilgule.setValue(float(after_cam_value))

        self.liste_devise = Settings.DEVISE
        # Combobox widget
        self.box_devise = QComboBox()
        for index, value in enumerate(self.liste_devise):
            self.box_devise.addItem("{}".format(self.liste_devise[value]), value)
            if hasattr(self.settings, 'devise') and self.settings.devise == value:
                self.box_devise.setCurrentIndex(index)

        self.liste_position = Settings.POSITION
        # Combobox widget
        self.box_position = QComboBox()
        for index, value in enumerate(self.liste_position):
            self.box_position.addItem("{}".format(self.liste_position[value]), value)
            if hasattr(self.settings, 'toolbar_position') and self.settings.toolbar_position == value:
                self.box_position.setCurrentIndex(index)

        self.checked = QCheckBox("Active")
        if hasattr(self.settings, 'auth_required') and self.settings.auth_required:
            self.checked.setCheckState(Qt.CheckState.Checked)
        self.checked.setToolTip(
            """Cocher si vous voulez pour deactive
                                le login continue à utiliser le systeme"""
        )
        self.toolbar_checked = QCheckBox("Active")
        toolbar_value = getattr(self.settings, 'toolbar', True)
        print("toolbar ", toolbar_value)
        if toolbar_value:
            self.toolbar_checked.setCheckState(Qt.CheckState.Checked)
        self.toolbar_checked.setToolTip(
            """Cocher si vous voulez pour deactive
                                le menu toolbar"""
        )

        formbox = QFormLayout()
        formbox.addRow(FormLabel("URL :*"), self.url_field)
        # formbox.addRow(FormLabel("Theme :"), self.box_theme)  # Thème désactivé
        formbox.addRow(FormLabel("Identification"), self.checked)
        formbox.addRow(FormLabel("Menu vertical"), self.toolbar_checked)
        formbox.addRow(
            FormLabel("Nombre de chiffre après la vilgule :"), self.box_vilgule
        )
        formbox.addRow(FormLabel("Devise :"), self.box_devise)
        formbox.addRow(FormLabel("Position du menu :"), self.box_position)

        butt = ButtonSave("Enregistrer")
        butt.clicked.connect(self.save_edit)
        formbox.addRow("", butt)

        vbox.addLayout(formbox)
        self.setLayout(vbox)

    def save_edit(self):
        """add operation"""
        # if check_is_empty(self.url_field):
        #     return

        try:
            # Utiliser init_settings pour récupérer/créer les paramètres
            settings = Settings.init_settings()
            
            settings.url = str(self.url_field.text())
            settings.auth_required = (
                True if self.checked.checkState() == Qt.CheckState.Checked else False
            )
            settings.toolbar = (
                True if self.toolbar_checked.checkState() == Qt.CheckState.Checked else False
            )
            print("settings.toolbar", settings.toolbar)
            settings.after_cam = int(self.box_vilgule.value())
            # Thème désactivé - garder la valeur existante
            if not hasattr(settings, 'theme') or not settings.theme:
                settings.theme = "default"
            settings.devise = self.box_devise.itemData(self.box_devise.currentIndex())
            settings.toolbar_position = self.box_position.itemData(
                self.box_position.currentIndex()
            )
            settings.save()

            logger.info("Paramètres mis à jour avec succès")
            if hasattr(self.parent, 'parent') and hasattr(self.parent.parent, 'Notify'):
                self.parent.parent.Notify("Paramètre mise à jour avec success", "success")
        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde des paramètres: {e}")
