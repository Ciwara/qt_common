#!usr/bin/env python
# -*- coding: utf8 -*-
# maintainer: Fad


from datetime import datetime

from PyQt6.QtWidgets import (
    QDialog,
    QFormLayout,
    QGridLayout,
    QGroupBox,
    QMessageBox,
    QTextEdit,
    QVBoxLayout,
)

from ..cstatic import CConstants
from ..exports import export_license_as_file
from ..models import License, Organization
from .common import (
    Button,
    ButtonSave,
    DeletedBtt,
    FormLabel,
    FWidget,
    LineEdit,
    PyTextViewer,
)
from .util import check_is_empty, get_lcse_file, is_valide_codition_field, make_lcse


class LicenseViewWidget(QDialog, FWidget):
    def __init__(self, parent=0, *args, **kwargs):
        QDialog.__init__(self, parent=parent, *args, **kwargs)
        self.parent = parent

        self.intro = FormLabel(
            """<div style='text-align: center; padding: 20px;'>
                <h2 style='color: #2c3e50;'>🔐 Activation de licence requise</h2>
                <p style='font-size: 14px; color: #7f8c8d;'>
                    Vous devez activer votre licence pour utiliser l'application
                </p>
            </div>"""
        )
        vbox = QVBoxLayout()
        try:
            self.lcse = License.get(License.code == str(make_lcse()))
            rep = self.lcse.can_use()
        except Exception as e:
            print(e)
            self.lcse = License()
            rep = CConstants.IS_EXPIRED
            # self.lcse = License.create(
            #     can_expired=True, code=make_lcse(), owner="Demo")
        rep = self.lcse.can_use()

        if rep == CConstants.IS_NOT_ACTIVATED or rep == CConstants.IS_EXPIRED:
            self.activation_group_box()
            vbox.addWidget(self.topLeftGroupBoxBtt)
            self.setLayout(vbox)
        else:
            self.show_license_group_box()
            vbox.addWidget(self.topLeftGroupBox)
            self.setLayout(vbox)

    def show_license_group_box(self):
        v_type = "d'évaluation" if self.lcse.can_expired else "complète"
        expiration_text = ("Illimitée" if not self.lcse.can_expired 
                          else self.lcse.expiration_date.strftime("%d/%m/%Y à %H:%M"))
        
        self.intro = FormLabel(
            f"""<div style='padding: 20px; background-color: #f8f9fa; border-radius: 8px; border-left: 4px solid #28a745;'>
                <h2 style='color: #28a745; margin-bottom: 15px;'>✅ Licence {v_type} activée</h2>
                
                <div style='background-color: white; padding: 15px; border-radius: 6px; margin: 10px 0;'>
                    <h4 style='color: #495057; margin-bottom: 10px;'>📋 Informations de licence</h4>
                    <table style='width: 100%; font-size: 13px;'>
                        <tr><td style='padding: 5px; font-weight: bold; color: #6c757d;'>Propriétaire :</td>
                            <td style='padding: 5px; color: #495057;'>{self.lcse.owner}</td></tr>
                        <tr><td style='padding: 5px; font-weight: bold; color: #6c757d;'>Date d'activation :</td>
                            <td style='padding: 5px; color: #495057;'>{self.lcse.activation_date.strftime("%d/%m/%Y à %H:%M")}</td></tr>
                        <tr><td style='padding: 5px; font-weight: bold; color: #6c757d;'>Expiration :</td>
                            <td style='padding: 5px; color: #495057;'>{expiration_text}</td></tr>
                    </table>
                </div>
                
                <div style='background-color: #e9ecef; padding: 10px; border-radius: 6px; margin-top: 15px;'>
                    <p style='margin: 0; font-size: 12px; color: #6c757d; text-align: center;'>
                        ⚠️ Cette licence n'est valable que pour cette machine
                    </p>
                </div>
            </div>"""
        )
        self.topLeftGroupBox = QGroupBox(self.tr("Licence"))
        gridbox = QGridLayout()

        cancel_but = Button("✅ Fermer")
        cancel_but.clicked.connect(self.cancel)
        export_lcse = Button("📄 Exporter la licence")
        export_lcse.clicked.connect(self.export_license)
        remove_trial_lcse = DeletedBtt("🗑️ Révoquer la licence")
        remove_trial_lcse.clicked.connect(self.remove_trial)
        # grid layout
        gridbox.addWidget(self.intro, 0, 1)
        gridbox.addWidget(cancel_but, 0, 2)
        gridbox.addWidget(export_lcse, 4, 1)
        gridbox.addWidget(remove_trial_lcse, 4, 2)

        # gridbox.setColumnStretch(2, 1)
        # gridbox.setRowStretch(4, 1)
        gridbox.setRowStretch(4, 0)

        self.topLeftGroupBox.setLayout(gridbox)

    def activation_group_box(self):
        self.topLeftGroupBoxBtt = QGroupBox(self.tr("🔑 Activation de licence"))
        self.setWindowTitle("Activation de licence")
        self.cpt = 0
        
        # Récupérer le code d'activation de manière sécurisée
        try:
            org_code = Organization.get(id=1).slug
        except:
            org_code = "Code non disponible"
            
        self.info_field = PyTextViewer(
            f"""<div style='padding: 15px; background-color: #f8f9fa; border-radius: 8px; border-left: 4px solid #007bff;'>
                <h3 style='color: #007bff; margin-bottom: 15px;'>📋 Informations d'activation</h3>
                
                <div style='background-color: white; padding: 15px; border-radius: 6px; margin: 10px 0;'>
                    <p style='margin-bottom: 10px; color: #495057;'>
                        <strong>Code d'identification de votre machine :</strong>
                    </p>
                    <div style='background-color: #e9ecef; padding: 10px; border-radius: 4px; font-family: monospace; font-size: 14px; font-weight: bold; color: #495057; text-align: center;'>
                        {org_code}
                    </div>
                    <p style='font-size: 12px; color: #6c757d; margin-top: 10px; text-align: center;'>
                        💡 Communiquez ce code pour obtenir votre licence
                    </p>
                </div>
                
                <div style='background-color: #fff3cd; padding: 10px; border-radius: 6px; border-left: 3px solid #ffc107;'>
                    <h4 style='color: #856404; margin-bottom: 8px;'>📞 Support technique</h4>
                    <p style='margin: 0; color: #856404; font-size: 13px;'>
                        <strong>Téléphone :</strong> {CConstants.TEL_AUT}<br>
                        <strong>Email :</strong> {CConstants.EMAIL_AUT}
                    </p>
                </div>
            </div>"""
        )
        self.name_field = LineEdit()
        self.name_field.setPlaceholderText("Entrez le nom du propriétaire de la licence")
        
        self.license_field = QTextEdit()
        self.license_field.setPlaceholderText("Collez ici le code de licence fourni par le support technique")

        trial_lcse = Button("🚀 Activer l'évaluation (60 jours)")
        trial_lcse.clicked.connect(self.active_trial)
        trial_lcse.setToolTip("Active une licence d'évaluation gratuite de 60 jours")

        if self.lcse.is_expired and self.lcse.evaluation:
            trial_lcse.setEnabled(False)
            trial_lcse.setText("⏰ Évaluation expirée")
            trial_lcse.setToolTip("La période d'évaluation est terminée")

        self.butt = ButtonSave("✅ Activer la licence")
        self.butt.clicked.connect(self.add_lience)

        cancel_but = Button("❌ Annuler")
        cancel_but.clicked.connect(self.cancel)

        formbox = QFormLayout()
        formbox.addRow(FormLabel(""), self.info_field)
        formbox.addRow(FormLabel("👤 Nom du propriétaire :"), self.name_field)
        formbox.addRow(FormLabel("🔑 Code de licence :"), self.license_field)
        formbox.addRow(FormLabel(""), trial_lcse)
        formbox.addRow(cancel_but, self.butt)
        self.topLeftGroupBoxBtt.setLayout(formbox)

    def cancel(self):
        self.close()

    def remove_trial(self):
        from PyQt6.QtWidgets import QMessageBox
        
        # Demander confirmation avant révocation
        reply = QMessageBox.question(
            self, 
            "Confirmer la révocation",
            "⚠️ Êtes-vous sûr de vouloir révoquer cette licence ?\n\n"
            "Cette action est irréversible et vous devrez réactiver\n"
            "une licence pour continuer à utiliser l'application.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.lcse.remove_activation()
                if self.parent:
                    self.parent.Notify(
                        "🗑️ Licence révoquée avec succès\n"
                        "L'application nécessitera une nouvelle activation.", "warning"
                    )
                self.cancel()
                self.accept()
            except Exception as e:
                print(f"Erreur lors de la révocation: {e}")
                if self.parent:
                    self.parent.Notify(
                        "❌ Erreur lors de la révocation de la licence", "error"
                    )

    def export_license(self):
        try:
            export_license_as_file()
        except IOError as e:
            if hasattr(self, 'parent') and self.parent:
                self.parent.Notify(
                    f"❌ {str(e)}",
                    "error"
                )
            else:
                QMessageBox.warning(
                    self,
                    "Erreur",
                    f"❌ {str(e)}"
                )

    def active_trial(self):
        try:
            print("Activation de la licence d'évaluation")
            self.lcse = License(can_expired=True, code=make_lcse(), owner="Évaluation")
            self.lcse.get_evaluation()
            self.cancel()
            self.accept()

            print(f"Licence d'évaluation activée - parent: {self.parent}")
            if self.parent:
                self.parent.Notify(
                    "🎉 Licence d'évaluation activée avec succès !\n"
                    "Durée : 60 jours\n"
                    "Profitez bien de l'application.", "success"
                )
        except Exception as e:
            print(f"Erreur lors de l'activation de la licence d'évaluation: {e}")
            if self.parent:
                self.parent.Notify(
                    "❌ Erreur lors de l'activation de la licence d'évaluation.\n"
                    "Veuillez contacter le support technique.", "error"
                )

    def add_lience(self):
        name = str(self.name_field.text()).strip()
        license = str(self.license_field.toPlainText()).strip()
        
        # Validation des champs
        if check_is_empty(self.license_field):
            if self.parent:
                self.parent.Notify("⚠️ Veuillez saisir le code de licence", "warning")
            return
            
        if check_is_empty(self.name_field):
            if self.parent:
                self.parent.Notify("⚠️ Veuillez saisir le nom du propriétaire", "warning")
            return

        m_lcse = make_lcse()
        
        # Vérification de la validité de la licence
        if is_valide_codition_field(
            self.license_field, "❌ Code de licence invalide", license != m_lcse
        ):
            # Fonctionnalité de déblocage d'urgence (pour développement)
            d = datetime.now()
            key = int((d.year - d.day - d.month) / 2)
            self.cpt += 1
            print(f"Tentative {self.cpt}, clé de déblocage: {key}")
            
            if self.cpt > 2 and license == str(key):
                self.license_field.setText(m_lcse)
                if self.parent:
                    self.parent.Notify("🔓 Code de déblocage accepté", "info")
                return

            if self.parent:
                self.parent.Notify(
                    "❌ Code de licence invalide\n"
                    "Vérifiez que vous avez copié le code correctement.", "error"
                )
            return

        try:
            # Activation de la licence complète
            self.lcse.can_expired = False
            self.lcse.owner = name
            if not self.lcse.code:
                self.lcse.code = license
            self.lcse.activation()

            # Sauvegarde du fichier de licence
            with open(get_lcse_file(), "w") as flcse:
                flcse.write(license)
            
            if self.parent:
                self.parent.Notify(
                    f"🎉 Licence activée avec succès !\n"
                    f"Propriétaire : {name}\n"
                    f"Type : Licence complète (illimitée)", "success"
                )
            
            self.accept()
            
        except Exception as e:
            print(f"Erreur lors de l'activation de la licence: {e}")
            if self.parent:
                self.parent.Notify(
                    "❌ Erreur lors de l'activation de la licence.\n"
                    "Veuillez contacter le support technique.", "error"
                )
