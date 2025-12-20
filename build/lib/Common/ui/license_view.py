#!usr/bin/env python
# -*- coding: utf8 -*-
# maintainer: Fad


from datetime import datetime, timedelta

from PyQt6.QtWidgets import (
    QDialog,
    QFormLayout,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
)

from ..cstatic import CConstants, logger
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
        """Affiche les informations de la licence avec statistiques détaillées"""
        v_type = "d'évaluation" if self.lcse.can_expired else "complète"
        v_type_icon = "⏰" if self.lcse.can_expired else "✅"
        
        # Calcul du temps restant pour les licences d'évaluation
        time_remaining_html = ""
        progress_bar_html = ""
        alert_html = ""
        
        if self.lcse.can_expired and self.lcse.expiration_date:
            try:
                now = datetime.now()
                expiration = self.lcse.expiration_date
                remaining = expiration - now
                
                if remaining.total_seconds() > 0:
                    days = remaining.days
                    hours = remaining.seconds // 3600
                    minutes = (remaining.seconds % 3600) // 60
                    
                    # Calcul du pourcentage restant (sur 60 jours)
                    total_days = 60
                    elapsed_days = total_days - days
                    percentage = max(0, min(100, (days / total_days) * 100))
                    
                    # Couleur selon le temps restant
                    if days <= 7:
                        color = "#dc3545"  # Rouge - Urgent
                        alert_icon = "🚨"
                    elif days <= 15:
                        color = "#ffc107"  # Orange - Attention
                        alert_icon = "⚠️"
                    else:
                        color = "#28a745"  # Vert - OK
                        alert_icon = "✅"
                    
                    time_remaining_html = f"""
                        <tr>
                            <td style='padding: 5px; font-weight: bold; color: #6c757d;'>⏱️ Temps restant :</td>
                            <td style='padding: 5px; color: {color}; font-weight: bold;'>
                                {days} jour{'s' if days > 1 else ''}, {hours}h {minutes}min
                            </td>
                        </tr>
                    """
                    
                    progress_bar_html = f"""
                        <tr>
                            <td colspan='2' style='padding: 10px 5px;'>
                                <div style='background-color: #e9ecef; border-radius: 4px; padding: 2px;'>
                                    <div style='background-color: {color}; width: {percentage}%; height: 20px; border-radius: 3px; transition: width 0.3s;'></div>
                                </div>
                                <div style='text-align: center; margin-top: 5px; font-size: 11px; color: #6c757d;'>
                                    {days} jours restants sur {total_days} jours
                                </div>
                            </td>
                        </tr>
                    """
                    
                    # Alerte si expiration proche
                    if days <= 7:
                        alert_html = f"""
                            <div style='background-color: #f8d7da; border-left: 4px solid {color}; padding: 15px; border-radius: 6px; margin-top: 15px;'>
                                <h4 style='color: #721c24; margin: 0 0 10px 0;'>{alert_icon} Expiration proche !</h4>
                                <p style='margin: 0; color: #721c24; font-size: 13px;'>
                                    Votre licence d'évaluation expire dans <strong>{days} jour{'s' if days > 1 else ''}</strong>.<br>
                                    Contactez le support technique pour obtenir une licence complète.
                                </p>
                            </div>
                        """
                else:
                    # Licence expirée
                    time_remaining_html = """
                        <tr>
                            <td style='padding: 5px; font-weight: bold; color: #6c757d;'>⏱️ Statut :</td>
                            <td style='padding: 5px; color: #dc3545; font-weight: bold;'>❌ Expirée</td>
                        </tr>
                    """
                    alert_html = """
                        <div style='background-color: #f8d7da; border-left: 4px solid #dc3545; padding: 15px; border-radius: 6px; margin-top: 15px;'>
                            <h4 style='color: #721c24; margin: 0 0 10px 0;'>🚨 Licence expirée</h4>
                            <p style='margin: 0; color: #721c24; font-size: 13px;'>
                                Votre licence d'évaluation a expiré. Veuillez contacter le support technique.
                            </p>
                        </div>
                    """
            except Exception as e:
                logger.error(f"Erreur lors du calcul du temps restant: {e}")
        
        expiration_text = ("Illimitée" if not self.lcse.can_expired 
                          else (self.lcse.expiration_date.strftime("%d/%m/%Y à %H:%M") 
                                if self.lcse.expiration_date else "Non définie"))
        
        # Code de licence tronqué pour l'affichage
        code_display = self.lcse.code[:16] + "..." if len(self.lcse.code) > 16 else self.lcse.code
        
        self.intro = FormLabel(
            f"""<div style='padding: 20px; background-color: #f8f9fa; border-radius: 8px; border-left: 4px solid #28a745;'>
                <h2 style='color: #28a745; margin-bottom: 15px;'>{v_type_icon} Licence {v_type} activée</h2>
                
                <div style='background-color: white; padding: 15px; border-radius: 6px; margin: 10px 0;'>
                    <h4 style='color: #495057; margin-bottom: 10px;'>📋 Informations de licence</h4>
                    <table style='width: 100%; font-size: 13px;'>
                        <tr>
                            <td style='padding: 5px; font-weight: bold; color: #6c757d;'>👤 Propriétaire :</td>
                            <td style='padding: 5px; color: #495057;'>{self.lcse.owner}</td>
                        </tr>
                        <tr>
                            <td style='padding: 5px; font-weight: bold; color: #6c757d;'>📅 Date d'activation :</td>
                            <td style='padding: 5px; color: #495057;'>{self.lcse.activation_date.strftime("%d/%m/%Y à %H:%M")}</td>
                        </tr>
                        <tr>
                            <td style='padding: 5px; font-weight: bold; color: #6c757d;'>🔑 Code de licence :</td>
                            <td style='padding: 5px; color: #495057; font-family: "Courier New", Courier, monospace;'>{code_display}</td>
                        </tr>
                        <tr>
                            <td style='padding: 5px; font-weight: bold; color: #6c757d;'>📆 Expiration :</td>
                            <td style='padding: 5px; color: #495057;'>{expiration_text}</td>
                        </tr>
                        {time_remaining_html}
                        <tr>
                            <td style='padding: 5px; font-weight: bold; color: #6c757d;'>🔄 Dernière mise à jour :</td>
                            <td style='padding: 5px; color: #495057;'>{self.lcse.update_date.strftime("%d/%m/%Y à %H:%M") if self.lcse.update_date else 'Non disponible'}</td>
                        </tr>
                        {progress_bar_html}
                    </table>
                </div>
                
                {alert_html}
                
                <div style='background-color: #e9ecef; padding: 10px; border-radius: 6px; margin-top: 15px;'>
                    <p style='margin: 0; font-size: 12px; color: #6c757d; text-align: center;'>
                        ⚠️ Cette licence n'est valable que pour cette machine
                    </p>
                </div>
            </div>"""
        )
        self.topLeftGroupBox = QGroupBox(self.tr("Gestion de la licence"))
        gridbox = QGridLayout()

        cancel_but = Button("✅ Fermer")
        cancel_but.setToolTip("Fermer la fenêtre de gestion de licence")
        cancel_but.clicked.connect(self.cancel)
        
        export_lcse = Button("📄 Exporter la licence")
        export_lcse.setToolTip("Exporter les informations de licence dans un fichier")
        export_lcse.clicked.connect(self.export_license)
        
        remove_trial_lcse = DeletedBtt("🗑️ Révoquer la licence")
        remove_trial_lcse.setToolTip("Révoquer cette licence (nécessitera une réactivation)")
        remove_trial_lcse.clicked.connect(self.remove_trial)
        
        # Layout amélioré
        gridbox.addWidget(self.intro, 0, 0, 1, 3)
        
        buttons_layout = QHBoxLayout()
        buttons_layout.addWidget(export_lcse)
        buttons_layout.addWidget(remove_trial_lcse)
        buttons_layout.addStretch()
        buttons_layout.addWidget(cancel_but)
        
        gridbox.addLayout(buttons_layout, 1, 0, 1, 3)

        self.topLeftGroupBox.setLayout(gridbox)

    def activation_group_box(self):
        self.topLeftGroupBoxBtt = QGroupBox(self.tr("🔑 Activation de licence"))
        self.setWindowTitle("Activation de licence")
        self.cpt = 0
        
        # Récupérer le code d'activation de manière sécurisée
        try:
            org_code = Organization.get(id=1).slug
            if not org_code:
                # Si slug n'existe pas, utiliser le code de machine
                from .util import make_lcse
                org_code = make_lcse()
        except Exception as e:
            logger.warning(f"Erreur lors de la récupération du code d'organisation: {e}")
            # Fallback vers le code de machine
            try:
                from .util import make_lcse
                org_code = make_lcse()
            except Exception as e2:
                logger.error(f"Erreur lors de la génération du code de machine: {e2}")
                org_code = "Code non disponible"
            
        # Champ pour le code de machine avec bouton copier
        code_layout = QHBoxLayout()
        self.machine_code_field = LineEdit()
        self.machine_code_field.setText(org_code)
        self.machine_code_field.setReadOnly(True)
        self.machine_code_field.setStyleSheet("font-family: 'Courier New', Courier, monospace; font-size: 12px; padding: 8px;")
        
        copy_code_btn = Button("📋 Copier")
        copy_code_btn.setToolTip("Copier le code dans le presse-papiers")
        copy_code_btn.clicked.connect(lambda: self.copy_to_clipboard(org_code))
        copy_code_btn.setMaximumWidth(100)
        
        code_layout.addWidget(self.machine_code_field)
        code_layout.addWidget(copy_code_btn)
        
        self.info_field = PyTextViewer(
            f"""<div style='padding: 15px; background-color: #f8f9fa; border-radius: 8px; border-left: 4px solid #007bff;'>
                <h3 style='color: #007bff; margin-bottom: 15px;'>📋 Informations d'activation</h3>
                
                <div style='background-color: white; padding: 15px; border-radius: 6px; margin: 10px 0;'>
                    <p style='margin-bottom: 10px; color: #495057;'>
                        <strong>Code d'identification de votre machine :</strong>
                    </p>
                    <p style='font-size: 12px; color: #6c757d; margin-top: 10px;'>
                        💡 Communiquez ce code au support technique pour obtenir votre licence complète
                    </p>
                </div>
                
                <div style='background-color: #fff3cd; padding: 10px; border-radius: 6px; border-left: 3px solid #ffc107;'>
                    <h4 style='color: #856404; margin-bottom: 8px;'>📞 Support technique</h4>
                    <p style='margin: 0; color: #856404; font-size: 13px;'>
                        <strong>Téléphone :</strong> {getattr(CConstants, 'TEL_AUT', 'Non disponible')}<br>
                        <strong>Email :</strong> {getattr(CConstants, 'EMAIL_AUT', 'Non disponible')}
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
        formbox.addRow(FormLabel("🖥️ Code de votre machine :"), code_layout)
        formbox.addRow(FormLabel("👤 Nom du propriétaire :"), self.name_field)
        formbox.addRow(FormLabel("🔑 Code de licence :"), self.license_field)
        formbox.addRow(FormLabel(""), trial_lcse)
        formbox.addRow(cancel_but, self.butt)
        self.topLeftGroupBoxBtt.setLayout(formbox)

    def copy_to_clipboard(self, text):
        """Copie le texte dans le presse-papiers"""
        from PyQt6.QtWidgets import QApplication
        clipboard = QApplication.clipboard()
        clipboard.setText(text)
        
        if self.parent:
            self.parent.Notify("✅ Code copié dans le presse-papiers", "success")
        else:
            QMessageBox.information(self, "Copié", "✅ Code copié dans le presse-papiers")
    
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
        """Active une licence d'évaluation de 60 jours"""
        try:
            # Vérifier si une licence d'évaluation a déjà été utilisée
            machine_code = make_lcse()
            try:
                existing_license = License.get(License.code == str(machine_code))
                if existing_license.evaluation and existing_license.is_expired:
                    reply = QMessageBox.question(
                        self,
                        "⚠️ Évaluation déjà utilisée",
                        "Une période d'évaluation a déjà été utilisée sur cette machine.\n\n"
                        "Voulez-vous vraiment réactiver une nouvelle période d'évaluation ?",
                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                        QMessageBox.StandardButton.No
                    )
                    if reply != QMessageBox.StandardButton.Yes:
                        return
                    # Réutiliser la licence existante
                    self.lcse = existing_license
                else:
                    self.lcse = existing_license
            except License.DoesNotExist:
                # Créer une nouvelle licence
                self.lcse = License()
                self.lcse.code = str(machine_code)
            
            logger.info("Activation de la licence d'évaluation")
            self.lcse.can_expired = True
            self.lcse.owner = "Évaluation"
            self.lcse.get_evaluation()
            
            # Sauvegarde du fichier de licence
            try:
                with open(get_lcse_file(), "w") as flcse:
                    flcse.write(str(machine_code))
            except Exception as e:
                logger.warning(f"Impossible de sauvegarder le fichier de licence: {e}")
            
            self.cancel()
            self.accept()

            logger.info(f"Licence d'évaluation activée avec succès")
            if self.parent:
                expiration_date = self.lcse.expiration_date.strftime("%d/%m/%Y")
                self.parent.Notify(
                    f"🎉 Licence d'évaluation activée avec succès !\n\n"
                    f"📅 Durée : 60 jours\n"
                    f"📆 Expiration : {expiration_date}\n\n"
                    f"Profitez bien de l'application !", "success"
                )
        except Exception as e:
            logger.error(f"Erreur lors de l'activation de la licence d'évaluation: {e}")
            if self.parent:
                self.parent.Notify(
                    f"❌ Erreur lors de l'activation de la licence d'évaluation.\n\n"
                    f"Détails : {str(e)}\n\n"
                    f"Veuillez contacter le support technique.", "error"
                )
            else:
                QMessageBox.critical(
                    self,
                    "Erreur",
                    f"❌ Erreur lors de l'activation de la licence d'évaluation.\n\n{str(e)}"
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
            machine_code = make_lcse()
            
            # Vérifier si la licence existe déjà ou créer une nouvelle
            if not hasattr(self.lcse, 'id') or not self.lcse.id:
                try:
                    self.lcse = License.get(License.code == str(machine_code))
                except License.DoesNotExist:
                    self.lcse = License()
                    self.lcse.code = str(machine_code)
            
            self.lcse.can_expired = False
            self.lcse.owner = name
            self.lcse.code = str(machine_code)
            self.lcse.activation()

            # Sauvegarde du fichier de licence
            try:
                with open(get_lcse_file(), "w") as flcse:
                    flcse.write(str(machine_code))
                logger.info(f"Fichier de licence sauvegardé: {get_lcse_file()}")
            except Exception as e:
                logger.warning(f"Impossible de sauvegarder le fichier de licence: {e}")
            
            logger.info(f"Licence complète activée pour: {name}")
            
            if self.parent:
                self.parent.Notify(
                    f"🎉 Licence activée avec succès !\n\n"
                    f"👤 Propriétaire : {name}\n"
                    f"✅ Type : Licence complète (illimitée)\n"
                    f"📅 Date d'activation : {datetime.now().strftime('%d/%m/%Y à %H:%M')}", 
                    "success"
                )
            
            self.accept()
            
        except Exception as e:
            logger.error(f"Erreur lors de l'activation de la licence: {e}")
            error_msg = (
                f"❌ Erreur lors de l'activation de la licence.\n\n"
                f"Détails techniques : {str(e)}\n\n"
                f"Veuillez contacter le support technique."
            )
            if self.parent:
                self.parent.Notify(error_msg, "error")
            else:
                QMessageBox.critical(self, "Erreur d'activation", error_msg)
