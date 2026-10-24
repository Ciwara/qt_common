#!usr/bin/env python
# -*- coding: utf8 -*-
# maintainer: Fad


from datetime import datetime

from PyQt6.QtCore import QTimer
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
from ..models import License
from .common import (
    Button,
    ButtonSave,
    DeletedBtt,
    FormLabel,
    FWidget,
    LineEdit,
    PyTextViewer,
)
from .util import (
    check_is_empty,
    register_activation_code,
    request_online_license,
    remember_evaluation_period,
    start_evaluation_once,
    is_valide_codition_field,
    make_lcse,
    persist_license_record,
    remove_lcse_files,
    write_lcse_file,
)


class LicenseViewWidget(QDialog, FWidget):
    def __init__(self, parent=0, *args, **kwargs):
        QDialog.__init__(self, parent=parent, *args, **kwargs)
        self.parent = parent

        self.intro = FormLabel(
            """<div style='text-align: center; padding: 20px;'>
                <h2 style='color: #2c3e50;'>🔐 Activation de licence requise</h2>
                <p style='font-size: 14px; color: #7f8c8d;'>
                    Cette application a sa propre clé de licence
                </p>
            </div>"""
        )
        vbox = QVBoxLayout()
        machine_hash = str(make_lcse())
        try:
            self.lcse = License.get(License.code == machine_hash)
        except License.DoesNotExist:
            self.lcse = License()
        except Exception:
            logger.exception("Erreur de lecture de la licence en base")
            self.lcse = License()
        rep = self.lcse.can_use()

        if rep == CConstants.IS_NOT_ACTIVATED or rep == CConstants.IS_EXPIRED:
            self.activation_group_box()
            vbox.addWidget(self.topLeftGroupBoxBtt)
            self.setLayout(vbox)
            QTimer.singleShot(0, self.ask_online_license)
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
        
        app_slug = str(getattr(CConstants, "APP_NAME", "") or "").strip() or "Non disponible"

        # Code montré au support : empreinte machine (MD5), alignée sur la validation de licence.
        try:
            org_code = make_lcse()
        except Exception as e:
            logger.error("Erreur lors de la génération du code machine: %s", e)
            org_code = "Code non disponible"

        slug_layout = QHBoxLayout()
        self.slug_field = LineEdit()
        self.slug_field.setText(app_slug)
        self.slug_field.setReadOnly(True)
        self.slug_field.setStyleSheet("font-family: 'Courier New', Courier, monospace; font-size: 12px; padding: 8px;")
        copy_slug_btn = Button("📋 Copier")
        copy_slug_btn.setToolTip("Copier le slug de l'application")
        copy_slug_btn.clicked.connect(lambda: self.copy_to_clipboard(app_slug))
        slug_layout.addWidget(self.slug_field)
        slug_layout.addWidget(copy_slug_btn)
            
        # Champ pour le code de machine avec bouton copier
        code_layout = QHBoxLayout()
        self.machine_code_field = LineEdit()
        self.machine_code_field.setText(org_code)
        self.machine_code_field.setReadOnly(True)
        self.machine_code_field.setStyleSheet("font-family: 'Courier New', Courier, monospace; font-size: 12px; padding: 8px;")
        
        copy_code_btn = Button("📋 Copier")
        copy_code_btn.setToolTip("Copier le code dans le presse-papiers")
        copy_code_btn.clicked.connect(lambda: self.copy_to_clipboard(org_code))
        
        code_layout.addWidget(self.machine_code_field)
        code_layout.addWidget(copy_code_btn)
        
        self.info_field = PyTextViewer(
            f"""<div style='padding: 15px; background-color: #f8f9fa; border-radius: 8px; border-left: 4px solid #007bff;'>
                <h3 style='color: #007bff; margin-bottom: 15px;'>📋 Informations d'activation</h3>
                
                <div style='background-color: white; padding: 15px; border-radius: 6px; margin: 10px 0;'>
                    <p style='margin-bottom: 10px; color: #495057;'>
                        <strong>Code de cette machine :</strong>
                    </p>
                    <p style='font-size: 12px; color: #6c757d; margin-top: 10px;'>
                        💡 Au lancement, l'application demande sa licence au serveur. Communiquez ce code machine pour qu'une licence soit émise en ligne.
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
        self.license_field = QTextEdit()
        self.license_field.setPlaceholderText("Ou collez un code de licence déjà fourni")

        self.online_status = QLabel("Demande de la licence en ligne…")
        self.online_status.setWordWrap(True)

        online_btn = Button("🌐 Demander la licence en ligne")
        online_btn.clicked.connect(self.ask_online_license)
        online_btn.setToolTip("Interroge le serveur de licences pour ce poste")

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
        formbox.addRow(FormLabel("📦 Slug application :"), slug_layout)
        formbox.addRow(FormLabel("🖥️ Code machine (pour générer la licence) :"), code_layout)
        formbox.addRow(FormLabel("🔑 Code de licence :"), self.license_field)
        formbox.addRow(FormLabel(""), self.online_status)
        formbox.addRow(FormLabel(""), online_btn)
        formbox.addRow(FormLabel(""), trial_lcse)
        formbox.addRow(cancel_but, self.butt)
        self.topLeftGroupBoxBtt.setLayout(formbox)

    def ask_online_license(self):
        """Récupère la licence émise sur le serveur pour cette machine."""
        if hasattr(self, "online_status"):
            self.online_status.setText("Demande de la licence en ligne…")
        result = request_online_license()
        message = result.get("message") or ""
        if hasattr(self, "online_status"):
            self.online_status.setText(message)
        if result.get("ok"):
            logger.info("Licence obtenue en ligne")
            self.accept()
            return
        logger.info("Licence en ligne non accordée : %s", message)

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
                remove_lcse_files()
                persist_license_record(self.lcse)
                if self.parent:
                    self.parent.Notify(
                        "🗑️ Licence révoquée avec succès\n"
                        "L'application nécessitera une nouvelle activation.", "warning"
                    )
                if hasattr(self, "topLeftGroupBox") and self.topLeftGroupBox:
                    self.topLeftGroupBox.setParent(None)
                    self.topLeftGroupBox.deleteLater()
                self.activation_group_box()
                layout = self.layout()
                if layout is None:
                    layout = QVBoxLayout()
                    self.setLayout(layout)
                else:
                    while layout.count():
                        item = layout.takeAt(0)
                        widget = item.widget()
                        if widget:
                            widget.deleteLater()
                layout.addWidget(self.topLeftGroupBoxBtt)
            except Exception as e:
                logger.exception("Erreur lors de la révocation de la licence: %s", e)
                if self.parent:
                    self.parent.Notify(
                        "❌ Erreur lors de la révocation de la licence", "error"
                    )
                else:
                    QMessageBox.critical(
                        self,
                        "Erreur",
                        f"❌ Erreur lors de la révocation de la licence.\n\n{str(e)}",
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
                self.lcse = existing_license
                if existing_license.evaluation and existing_license.expiration_date:
                    remember_evaluation_period(existing_license.expiration_date)
            except License.DoesNotExist:
                self.lcse = License()
                self.lcse.code = str(machine_code)

            expires = start_evaluation_once()
            logger.info("Activation de la licence d'évaluation")
            self.lcse.can_expired = True
            self.lcse.evaluation = True
            self.lcse.isactivated = False
            self.lcse.owner = "Évaluation"
            self.lcse.expiration_date = expires
            self.lcse.save()
            
            write_lcse_file(machine_code)
            persist_license_record(self.lcse)

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
        except ValueError as exc:
            if self.parent:
                self.parent.Notify(f"❌ {exc}", "warning")
            else:
                QMessageBox.warning(self, "Évaluation", str(exc))
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
        license = str(self.license_field.toPlainText()).strip()
        
        # Validation des champs
        if check_is_empty(self.license_field):
            if self.parent:
                self.parent.Notify("⚠️ Veuillez saisir le code de licence", "warning")
            return

        machine_code = str(make_lcse())
        app_slug = str(getattr(CConstants, "APP_NAME", "") or "").strip()
        try:
            days, expiration = register_activation_code(license, machine_code, app_slug)
        except ValueError as exc:
            # Déblocage de secours (affiche la clé du jour dans le terminal)
            d = datetime.now()
            key = int((d.year - d.day - d.month) / 2)
            self.cpt += 1
            print(f"Tentative {self.cpt}, clé de déblocage: {key}")

            if self.cpt > 2 and license == str(key):
                self.license_field.setText(machine_code)
                if self.parent:
                    self.parent.Notify("🔓 Code de déblocage accepté", "info")
                return

            is_valide_codition_field(
                self.license_field, "❌ Code de licence invalide", True
            )
            if self.parent:
                self.parent.Notify(
                    f"❌ {exc}\nVérifiez le code, l'application et la clé machine.",
                    "error",
                )
            return

        try:
            if not hasattr(self.lcse, "id") or not self.lcse.id:
                try:
                    self.lcse = License.get(License.code == machine_code)
                except License.DoesNotExist:
                    self.lcse = License()
                    self.lcse.code = machine_code

            self.lcse.code = machine_code
            self.lcse.activation_date = datetime.now()
            if days is None:
                self.lcse.evaluation = False
                self.lcse.expiration_date = None
                self.lcse.activation()
                kind = "Licence complète (illimitée)"
            else:
                self.lcse.isactivated = False
                self.lcse.can_expired = True
                self.lcse.evaluation = False
                self.lcse.expiration_date = expiration
                self.lcse.save()
                kind = f"Licence de {int(days)} jours"

            write_lcse_file(machine_code)
            persist_license_record(self.lcse)
            logger.info("Licence activée (%s)", kind)

            if self.parent:
                self.parent.Notify(
                    f"🎉 Licence activée avec succès !\n\n"
                    f"✅ Type : {kind}\n"
                    f"📅 Date d'activation : {datetime.now().strftime('%d/%m/%Y à %H:%M')}",
                    "success",
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
