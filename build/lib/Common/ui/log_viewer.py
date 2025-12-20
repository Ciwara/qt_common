#!/usr/bin/env python
# -*- coding: utf8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu
# maintainer: Fad

import os
from pathlib import Path
from datetime import datetime

from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QTextCharFormat, QColor, QTextCursor, QFont
from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QComboBox,
    QLineEdit,
    QLabel,
    QTextEdit,
    QCheckBox,
    QMessageBox,
)

from .common import FWidget, Button, FLabel
from ..cstatic import CConstants, logger


class LogViewerWidget(QDialog, FWidget):
    """Widget pour visualiser les logs de l'application"""
    
    def __init__(self, parent=None, *args, **kwargs):
        QDialog.__init__(self, parent, *args, **kwargs)
        FWidget.__init__(self, parent, *args, **kwargs)
        
        self.setWindowTitle("📋 Visualiseur de logs")
        self.setMinimumSize(900, 600)
        self.log_file_path = None
        self.auto_refresh = False
        self.refresh_timer = QTimer(self)
        self.refresh_timer.timeout.connect(self.refresh_logs)
        
        self.init_ui()
        self.load_log_file_path()
        self.refresh_logs()
    
    def init_ui(self):
        """Initialise l'interface utilisateur"""
        layout = QVBoxLayout(self)
        
        # Barre d'outils
        toolbar = QHBoxLayout()
        
        # Bouton actualiser
        self.refresh_btn = Button("🔄 Actualiser")
        self.refresh_btn.setToolTip("Actualiser les logs")
        self.refresh_btn.clicked.connect(self.refresh_logs)
        toolbar.addWidget(self.refresh_btn)
        
        # Filtre par niveau
        toolbar.addWidget(QLabel("📊 Niveau:"))
        self.level_filter = QComboBox()
        self.level_filter.addItems(["Tous", "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"])
        self.level_filter.currentTextChanged.connect(self.filter_logs)
        toolbar.addWidget(self.level_filter)
        
        # Recherche
        toolbar.addWidget(QLabel("🔍 Rechercher:"))
        self.search_field = QLineEdit()
        self.search_field.setPlaceholderText("Rechercher dans les logs...")
        self.search_field.textChanged.connect(self.filter_logs)
        toolbar.addWidget(self.search_field)
        
        # Auto-refresh
        self.auto_refresh_cb = QCheckBox("⏱️ Actualisation auto (5s)")
        self.auto_refresh_cb.toggled.connect(self.toggle_auto_refresh)
        toolbar.addWidget(self.auto_refresh_cb)
        
        # Scroll automatique
        self.auto_scroll_cb = QCheckBox("⬇️ Scroll auto")
        self.auto_scroll_cb.setChecked(True)
        self.auto_scroll_cb.setToolTip("Scroller automatiquement vers les dernières lignes")
        toolbar.addWidget(self.auto_scroll_cb)
        
        # Bouton exporter
        self.export_btn = Button("💾 Exporter")
        self.export_btn.setToolTip("Exporter les logs dans un fichier")
        self.export_btn.clicked.connect(self.export_logs)
        toolbar.addWidget(self.export_btn)
        
        # Bouton effacer
        self.clear_btn = Button("🗑️ Effacer")
        self.clear_btn.setToolTip("Effacer le contenu affiché (ne supprime pas le fichier)")
        self.clear_btn.clicked.connect(self.clear_display)
        toolbar.addWidget(self.clear_btn)
        
        toolbar.addStretch()
        layout.addLayout(toolbar)
        
        # Zone de texte pour les logs
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setFont(QFont("Courier", 9))
        self.log_text.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)
        
        # Configuration des couleurs pour les niveaux de log
        self.setup_text_formats()
        
        layout.addWidget(self.log_text)
        
        # Statut
        self.status_label = QLabel("📋 Prêt")
        self.status_label.setStyleSheet("padding: 5px; background-color: #f0f0f0;")
        layout.addWidget(self.status_label)
    
    def setup_text_formats(self):
        """Configure les formats de texte pour colorer les logs"""
        self.formats = {
            'DEBUG': QTextCharFormat(),
            'INFO': QTextCharFormat(),
            'WARNING': QTextCharFormat(),
            'ERROR': QTextCharFormat(),
            'CRITICAL': QTextCharFormat(),
        }
        
        # DEBUG - gris
        self.formats['DEBUG'].setForeground(QColor(128, 128, 128))
        
        # INFO - bleu
        self.formats['INFO'].setForeground(QColor(0, 0, 255))
        
        # WARNING - orange
        self.formats['WARNING'].setForeground(QColor(255, 165, 0))
        
        # ERROR - rouge
        self.formats['ERROR'].setForeground(QColor(255, 0, 0))
        self.formats['ERROR'].setFontWeight(QFont.Weight.Bold)
        
        # CRITICAL - rouge foncé
        self.formats['CRITICAL'].setForeground(QColor(139, 0, 0))
        self.formats['CRITICAL'].setFontWeight(QFont.Weight.Bold)
    
    def load_log_file_path(self):
        """Charge le chemin du fichier log"""
        try:
            # Chemin du fichier log depuis cstatic (même logique que dans cstatic.py)
            log_dir = Path(__file__).parent.parent.parent / 'logs'
            log_dir.mkdir(exist_ok=True)  # Créer le dossier s'il n'existe pas
            self.log_file_path = log_dir / 'app.log'
            
            # Si le fichier principal n'existe pas, chercher les fichiers de backup
            if not self.log_file_path.exists():
                # Chercher les fichiers de backup (app.log.1, app.log.2, etc.)
                backup_files = sorted(
                    [f for f in log_dir.glob('app.log.*') if f.is_file()],
                    key=lambda x: x.stat().st_mtime,
                    reverse=True
                )
                if backup_files:
                    self.log_file_path = backup_files[0]
                    logger.debug(f"Utilisation du fichier de backup: {self.log_file_path}")
            
            # Si toujours pas trouvé, essayer un autre emplacement
            if not self.log_file_path.exists():
                # Essayer avec le répertoire courant
                current_dir_log = Path.cwd() / 'logs' / 'app.log'
                if current_dir_log.exists():
                    self.log_file_path = current_dir_log
                else:
                    logger.warning(f"Fichier de log introuvable dans {log_dir}")
                    
        except Exception as e:
            logger.error(f"Erreur lors du chargement du chemin du log: {e}")
            self.log_file_path = None
    
    def refresh_logs(self):
        """Charge et affiche les logs"""
        if not self.log_file_path or not self.log_file_path.exists():
            self.log_text.setPlainText("❌ Fichier de log introuvable.\n\nChemin recherché: {}".format(
                self.log_file_path if self.log_file_path else "Non défini"
            ))
            self.status_label.setText("❌ Fichier de log introuvable")
            return
        
        try:
            # Lire le fichier de log
            with open(self.log_file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Stocker le contenu brut pour le filtrage
            self.raw_logs = content
            
            # Appliquer les filtres
            self.filter_logs()
            
            # Mettre à jour le statut
            file_size = self.log_file_path.stat().st_size
            size_mb = file_size / (1024 * 1024)
            last_modified = datetime.fromtimestamp(self.log_file_path.stat().st_mtime)
            self.status_label.setText(
                f"📋 {self.log_file_path.name} | "
                f"Taille: {size_mb:.2f} MB | "
                f"Dernière modification: {last_modified.strftime('%d/%m/%Y %H:%M:%S')}"
            )
            
        except PermissionError:
            self.log_text.setPlainText("❌ Permission refusée pour lire le fichier de log.")
            self.status_label.setText("❌ Permission refusée")
        except Exception as e:
            error_msg = f"❌ Erreur lors de la lecture du fichier de log:\n{str(e)}"
            self.log_text.setPlainText(error_msg)
            self.status_label.setText(f"❌ Erreur: {str(e)}")
            logger.error(f"Erreur lors de la lecture des logs: {e}")
    
    def filter_logs(self):
        """Filtre les logs selon les critères sélectionnés"""
        if not hasattr(self, 'raw_logs'):
            return
        
        lines = self.raw_logs.split('\n')
        filtered_lines = []
        level_filter = self.level_filter.currentText()
        search_text = self.search_field.text().lower()
        
        # Obtenir la position de scroll actuelle
        scrollbar = self.log_text.verticalScrollBar()
        was_at_bottom = scrollbar.value() >= scrollbar.maximum() - 10
        
        # Vider le texte actuel
        self.log_text.clear()
        
        for line in lines:
            # Filtrer par niveau
            if level_filter != "Tous":
                if f" - {level_filter} - " not in line:
                    continue
            
            # Filtrer par recherche
            if search_text and search_text not in line.lower():
                continue
            
            # Ajouter la ligne avec le formatage approprié
            self.append_log_line(line)
        
        # Scroll vers le bas si c'était le cas avant
        if was_at_bottom and self.auto_scroll_cb.isChecked():
            cursor = self.log_text.textCursor()
            cursor.movePosition(QTextCursor.MoveOperation.End)
            self.log_text.setTextCursor(cursor)
            scrollbar.setValue(scrollbar.maximum())
    
    def append_log_line(self, line):
        """Ajoute une ligne de log avec le formatage approprié"""
        cursor = self.log_text.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        
        # Déterminer le niveau de log
        level = None
        for log_level in ['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG']:
            if f" - {log_level} - " in line:
                level = log_level
                break
        
        # Appliquer le formatage
        if level and level in self.formats:
            cursor.setCharFormat(self.formats[level])
        else:
            # Format par défaut
            format_default = QTextCharFormat()
            format_default.setForeground(QColor(0, 0, 0))
            cursor.setCharFormat(format_default)
        
        # Ajouter la ligne
        cursor.insertText(line + '\n')
    
    def toggle_auto_refresh(self, checked):
        """Active ou désactive l'actualisation automatique"""
        self.auto_refresh = checked
        if checked:
            self.refresh_timer.start(5000)  # 5 secondes
            self.refresh_btn.setText("🔄 Actualiser (auto)")
        else:
            self.refresh_timer.stop()
            self.refresh_btn.setText("🔄 Actualiser")
    
    def clear_display(self):
        """Efface l'affichage (ne supprime pas le fichier)"""
        reply = QMessageBox.question(
            self,
            "Effacer l'affichage",
            "Voulez-vous effacer l'affichage des logs ?\n\n(Cela ne supprime pas le fichier de log)",
            QMessageBox.StandardButton.Yes,
            QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.log_text.clear()
            self.status_label.setText("📋 Affichage effacé")
    
    def export_logs(self):
        """Exporte les logs affichés dans un fichier"""
        from PyQt6.QtWidgets import QFileDialog
        
        if not hasattr(self, 'raw_logs'):
            QMessageBox.warning(self, "Export", "Aucun log à exporter")
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Exporter les logs",
            f"logs_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            "Fichiers texte (*.txt);;Tous les fichiers (*)"
        )
        
        if file_path:
            try:
                # Exporter les logs filtrés actuellement affichés
                content = self.log_text.toPlainText()
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                QMessageBox.information(self, "Export réussi", f"Les logs ont été exportés vers:\n{file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Erreur d'export", f"Erreur lors de l'export:\n{str(e)}")
                logger.error(f"Erreur lors de l'export des logs: {e}")
    
    def closeEvent(self, event):
        """Arrête le timer lors de la fermeture"""
        if self.refresh_timer.isActive():
            self.refresh_timer.stop()
        event.accept()

