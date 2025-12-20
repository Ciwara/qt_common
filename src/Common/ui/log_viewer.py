#!/usr/bin/env python
# -*- coding: utf8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu
# maintainer: Fad

import re
from pathlib import Path
from datetime import datetime
from collections import Counter

from PyQt6.QtCore import Qt, QTimer, QDate, QRegularExpression
from PyQt6.QtGui import (
    QTextCharFormat, QColor, QTextCursor, QFont,
    QSyntaxHighlighter
)
from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QComboBox,
    QLineEdit,
    QLabel,
    QTextEdit,
    QCheckBox,
    QMessageBox,
    QDateEdit,
    QSpinBox,
    QGroupBox,
    QFileDialog,
)

from .common import FWidget, Button
from ..cstatic import logger


class LogHighlighter(QSyntaxHighlighter):
    """Highlighter pour mettre en évidence les termes de recherche"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.search_pattern = None
        self.regex = None  # Initialiser regex pour éviter AttributeError
        self.highlight_format = QTextCharFormat()
        self.highlight_format.setBackground(QColor(255, 255, 0, 100))  # Jaune transparent
        self.highlight_format.setForeground(QColor(0, 0, 0))
        
    def set_search_pattern(self, pattern):
        """Définit le motif de recherche à mettre en évidence"""
        self.search_pattern = pattern
        if pattern:
            try:
                self.regex = QRegularExpression(
                    QRegularExpression.escape(pattern),
                    QRegularExpression.PatternOption.CaseInsensitiveOption
                )
            except Exception as e:
                from ..cstatic import logger
                logger.error(f"Erreur lors de la création de la regex: {e}")
                self.regex = None
        else:
            self.regex = None
        try:
            self.rehighlight()
        except Exception as e:
            from ..cstatic import logger
            logger.debug(f"Erreur lors du rehighlight (document peut-être non initialisé): {e}")
    
    def highlightBlock(self, text):
        """Applique le highlighting sur un bloc de texte"""
        if self.regex and self.search_pattern:
            try:
                iterator = self.regex.globalMatch(text)
                while iterator.hasNext():
                    match = iterator.next()
                    if match.isValid():
                        self.setFormat(
                            match.capturedStart(),
                            match.capturedLength(),
                            self.highlight_format
                        )
            except Exception as e:
                from ..cstatic import logger
                logger.debug(f"Erreur lors du highlighting: {e}")


class LogViewerWidget(QDialog, FWidget):
    """Widget amélioré pour visualiser les logs de l'application"""
    
    # Limite de lignes pour les gros fichiers (performance)
    MAX_LINES_DISPLAY = 10000
    MAX_LINES_LOAD = 50000
    
    def __init__(self, parent=None, *args, **kwargs):
        QDialog.__init__(self, parent, *args, **kwargs)
        FWidget.__init__(self, parent, *args, **kwargs)
        
        self.setWindowTitle("📋 Visualiseur de logs amélioré")
        self.setMinimumSize(1200, 700)
        self.resize(1400, 800)
        
        # Variables d'état
        self.log_file_path = None
        self.raw_logs = ""
        self.all_log_lines = []
        self.log_stats = {}
        self.current_search_index = -1
        self.search_matches = []
        self.font_size = 9
        self.max_lines_to_display = self.MAX_LINES_DISPLAY
        
        # Timer pour l'auto-refresh
        self.auto_refresh = False
        self.refresh_timer = QTimer(self)
        self.refresh_timer.timeout.connect(self.refresh_logs)
        
        self.init_ui()
        self.load_log_file_path()
        self.refresh_logs()
    
    def init_ui(self):
        """Initialise l'interface utilisateur améliorée"""
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        # ========== BARRE D'OUTILS PRINCIPALE ==========
        toolbar = QHBoxLayout()
        toolbar.setSpacing(8)
        
        # Bouton actualiser
        self.refresh_btn = Button("🔄 Actualiser")
        self.refresh_btn.setToolTip("Actualiser les logs depuis le fichier")
        self.refresh_btn.clicked.connect(self.refresh_logs)
        toolbar.addWidget(self.refresh_btn)
        
        # Sélection de fichier
        self.file_btn = Button("📁 Fichier")
        self.file_btn.setToolTip("Choisir un autre fichier de log")
        self.file_btn.clicked.connect(self.select_log_file)
        toolbar.addWidget(self.file_btn)
        
        toolbar.addWidget(QLabel("|"))
        
        # Filtre par niveau
        toolbar.addWidget(QLabel("📊 Niveau:"))
        self.level_filter = QComboBox()
        self.level_filter.addItems(["Tous", "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"])
        self.level_filter.currentTextChanged.connect(self.filter_logs)
        self.level_filter.setMinimumWidth(100)
        toolbar.addWidget(self.level_filter)
        
        # Filtre par date
        toolbar.addWidget(QLabel("📅 Depuis:"))
        self.date_filter = QDateEdit()
        self.date_filter.setDate(QDate.currentDate().addDays(-7))  # 7 derniers jours par défaut
        self.date_filter.setCalendarPopup(True)
        self.date_filter.setDisplayFormat("dd/MM/yyyy")
        self.date_filter.dateChanged.connect(self.filter_logs)
        self.date_filter.setToolTip("Afficher les logs depuis cette date")
        toolbar.addWidget(self.date_filter)
        
        toolbar.addWidget(QLabel("|"))
        
        # Recherche améliorée
        toolbar.addWidget(QLabel("🔍 Rechercher:"))
        self.search_field = QLineEdit()
        self.search_field.setPlaceholderText("Rechercher dans les logs...")
        self.search_field.setMinimumWidth(200)
        self.search_field.textChanged.connect(self.on_search_changed)
        self.search_field.returnPressed.connect(self.search_next)
        toolbar.addWidget(self.search_field)
        
        # Navigation de recherche
        self.search_prev_btn = Button("⬆️")
        self.search_prev_btn.setToolTip("Résultat précédent")
        self.search_prev_btn.setMaximumWidth(40)
        self.search_prev_btn.clicked.connect(self.search_previous)
        self.search_prev_btn.setEnabled(False)
        toolbar.addWidget(self.search_prev_btn)
        
        self.search_next_btn = Button("⬇️")
        self.search_next_btn.setToolTip("Résultat suivant")
        self.search_next_btn.setMaximumWidth(40)
        self.search_next_btn.clicked.connect(self.search_next)
        self.search_next_btn.setEnabled(False)
        toolbar.addWidget(self.search_next_btn)
        
        self.search_count_label = QLabel("")
        self.search_count_label.setMinimumWidth(80)
        toolbar.addWidget(self.search_count_label)
        
        toolbar.addWidget(QLabel("|"))
        
        # Contrôles de zoom
        toolbar.addWidget(QLabel("🔍 Zoom:"))
        self.zoom_out_btn = Button("➖")
        self.zoom_out_btn.setMaximumWidth(35)
        self.zoom_out_btn.setToolTip("Réduire la taille de police")
        self.zoom_out_btn.clicked.connect(self.zoom_out)
        toolbar.addWidget(self.zoom_out_btn)
        
        self.zoom_label = QLabel(f"{self.font_size}pt")
        self.zoom_label.setMinimumWidth(45)
        self.zoom_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        toolbar.addWidget(self.zoom_label)
        
        self.zoom_in_btn = Button("➕")
        self.zoom_in_btn.setMaximumWidth(35)
        self.zoom_in_btn.setToolTip("Augmenter la taille de police")
        self.zoom_in_btn.clicked.connect(self.zoom_in)
        toolbar.addWidget(self.zoom_in_btn)
        
        toolbar.addWidget(QLabel("|"))
        
        # Limite de lignes
        toolbar.addWidget(QLabel("📄 Max lignes:"))
        self.max_lines_spin = QSpinBox()
        self.max_lines_spin.setMinimum(100)
        self.max_lines_spin.setMaximum(100000)
        self.max_lines_spin.setValue(self.MAX_LINES_DISPLAY)
        self.max_lines_spin.setSuffix(" lignes")
        self.max_lines_spin.valueChanged.connect(self.on_max_lines_changed)
        self.max_lines_spin.setToolTip("Nombre maximum de lignes à afficher (performance)")
        toolbar.addWidget(self.max_lines_spin)
        
        toolbar.addStretch()
        
        # Auto-refresh
        self.auto_refresh_cb = QCheckBox("⏱️ Auto (5s)")
        self.auto_refresh_cb.setToolTip("Actualisation automatique toutes les 5 secondes")
        self.auto_refresh_cb.toggled.connect(self.toggle_auto_refresh)
        toolbar.addWidget(self.auto_refresh_cb)
        
        # Scroll automatique
        self.auto_scroll_cb = QCheckBox("⬇️ Scroll auto")
        self.auto_scroll_cb.setChecked(True)
        self.auto_scroll_cb.setToolTip("Scroller automatiquement vers les dernières lignes")
        toolbar.addWidget(self.auto_scroll_cb)
        
        main_layout.addLayout(toolbar)
        
        # ========== STATISTIQUES ==========
        stats_group = QGroupBox("📊 Statistiques")
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(15)
        
        self.stats_labels = {}
        for level in ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']:
            label = QLabel(f"{level}: 0")
            label.setStyleSheet(self.get_stat_style(level))
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.stats_labels[level] = label
            stats_layout.addWidget(label)
        
        stats_layout.addStretch()
        
        self.total_lines_label = QLabel("Total: 0 lignes")
        self.total_lines_label.setStyleSheet("font-weight: bold; padding: 5px;")
        stats_layout.addWidget(self.total_lines_label)
        
        stats_group.setLayout(stats_layout)
        main_layout.addWidget(stats_group)
        
        # ========== ZONE DE LOGS ==========
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setFont(QFont("Courier New", self.font_size))
        self.log_text.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)
        
        # Configuration des couleurs pour les niveaux de log
        self.setup_text_formats()
        
        # Ajouter le highlighter
        self.highlighter = LogHighlighter(self.log_text.document())
        
        main_layout.addWidget(self.log_text)
        
        # ========== BARRE DE STATUT ==========
        status_layout = QHBoxLayout()
        
        self.status_label = QLabel("📋 Prêt")
        self.status_label.setStyleSheet("padding: 5px; background-color: #f0f0f0; border-radius: 3px;")
        status_layout.addWidget(self.status_label)
        
        # Boutons d'action
        action_layout = QHBoxLayout()
        action_layout.setSpacing(5)
        
        self.export_btn = Button("💾 Exporter")
        self.export_btn.setToolTip("Exporter les logs filtrés dans un fichier")
        self.export_btn.clicked.connect(self.export_logs)
        action_layout.addWidget(self.export_btn)
        
        self.clear_btn = Button("🗑️ Effacer")
        self.clear_btn.setToolTip("Effacer l'affichage (ne supprime pas le fichier)")
        self.clear_btn.clicked.connect(self.clear_display)
        action_layout.addWidget(self.clear_btn)
        
        status_layout.addLayout(action_layout)
        main_layout.addLayout(status_layout)
    
    def get_stat_style(self, level):
        """Retourne le style CSS pour les statistiques selon le niveau"""
        colors = {
            'DEBUG': 'color: #808080;',
            'INFO': 'color: #0000FF;',
            'WARNING': 'color: #FFA500;',
            'ERROR': 'color: #FF0000; font-weight: bold;',
            'CRITICAL': 'color: #8B0000; font-weight: bold;',
        }
        return f"padding: 5px 10px; border-radius: 5px; background-color: #f5f5f5; {colors.get(level, '')}"
    
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
        self.formats['WARNING'].setFontWeight(QFont.Weight.Bold)
        
        # ERROR - rouge
        self.formats['ERROR'].setForeground(QColor(255, 0, 0))
        self.formats['ERROR'].setFontWeight(QFont.Weight.Bold)
        
        # CRITICAL - rouge foncé
        self.formats['CRITICAL'].setForeground(QColor(139, 0, 0))
        self.formats['CRITICAL'].setFontWeight(QFont.Weight.Bold)
        self.formats['CRITICAL'].setBackground(QColor(255, 200, 200))
    
    def load_log_file_path(self):
        """Charge le chemin du fichier log"""
        try:
            log_dir = Path(__file__).parent.parent.parent / 'logs'
            log_dir.mkdir(exist_ok=True)
            self.log_file_path = log_dir / 'app.log'
            
            if not self.log_file_path.exists():
                backup_files = sorted(
                    [f for f in log_dir.glob('app.log.*') if f.is_file()],
                    key=lambda x: x.stat().st_mtime,
                    reverse=True
                )
                if backup_files:
                    self.log_file_path = backup_files[0]
                    logger.debug(f"Utilisation du fichier de backup: {self.log_file_path}")
            
            if not self.log_file_path.exists():
                current_dir_log = Path.cwd() / 'logs' / 'app.log'
                if current_dir_log.exists():
                    self.log_file_path = current_dir_log
                else:
                    logger.warning(f"Fichier de log introuvable dans {log_dir}")
                    
        except Exception as e:
            logger.error(f"Erreur lors du chargement du chemin du log: {e}")
            self.log_file_path = None
    
    def select_log_file(self):
        """Permet de sélectionner un autre fichier de log"""
        log_dir = Path(__file__).parent.parent.parent / 'logs'
        if not log_dir.exists():
            log_dir = Path.cwd() / 'logs'
        
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Sélectionner un fichier de log",
            str(log_dir),
            "Fichiers de log (*.log *.txt);;Tous les fichiers (*)"
        )
        
        if file_path:
            self.log_file_path = Path(file_path)
            self.refresh_logs()
    
    def refresh_logs(self):
        """Charge et affiche les logs avec gestion des gros fichiers"""
        if not self.log_file_path or not self.log_file_path.exists():
            self.log_text.setPlainText(
                f"❌ Fichier de log introuvable.\n\n"
                f"Chemin recherché: {self.log_file_path if self.log_file_path else 'Non défini'}"
            )
            self.status_label.setText("❌ Fichier de log introuvable")
            self.update_stats({})
            return
        
        try:
            file_size = self.log_file_path.stat().st_size
            size_mb = file_size / (1024 * 1024)
            
            # Pour les gros fichiers, lire seulement les dernières lignes
            if size_mb > 10:  # Plus de 10 MB
                self.status_label.setText(
                    f"⏳ Chargement du fichier volumineux ({size_mb:.1f} MB)..."
                )
                self.log_text.setPlainText("⏳ Chargement en cours...")
                QTimer.singleShot(100, lambda: self.load_large_file())
            else:
                self.load_normal_file()
                
        except PermissionError:
            self.log_text.setPlainText("❌ Permission refusée pour lire le fichier de log.")
            self.status_label.setText("❌ Permission refusée")
            self.update_stats({})
        except Exception as e:
            error_msg = f"❌ Erreur lors de la lecture du fichier de log:\n{str(e)}"
            self.log_text.setPlainText(error_msg)
            self.status_label.setText(f"❌ Erreur: {str(e)}")
            logger.error(f"Erreur lors de la lecture des logs: {e}")
            self.update_stats({})
    
    def load_normal_file(self):
        """Charge un fichier de taille normale"""
        try:
            with open(self.log_file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            self.raw_logs = content
            self.all_log_lines = content.split('\n')
            
            # Calculer les statistiques
            self.calculate_stats()
            
            # Appliquer les filtres
            self.filter_logs()
            
            # Mettre à jour le statut
            self.update_status()
            
        except Exception as e:
            logger.error(f"Erreur lors du chargement normal: {e}")
            self.log_text.setPlainText(f"❌ Erreur: {str(e)}")
    
    def load_large_file(self):
        """Charge un gros fichier en lisant seulement les dernières lignes"""
        try:
            # Lire les dernières lignes du fichier
            with open(self.log_file_path, 'rb') as f:
                # Aller à la fin du fichier
                f.seek(0, 2)  # 2 = fin du fichier
                file_size = f.tell()
                
                # Lire les derniers X MB (ou tout si plus petit)
                bytes_to_read = min(5 * 1024 * 1024, file_size)  # 5 MB max
                f.seek(max(0, file_size - bytes_to_read))
                
                # Lire et décoder
                raw_bytes = f.read()
                content = raw_bytes.decode('utf-8', errors='ignore')
                
                # Prendre seulement les dernières lignes
                lines = content.split('\n')
                if len(lines) > self.MAX_LINES_LOAD:
                    lines = lines[-self.MAX_LINES_LOAD:]
                    content = '\n'.join(lines)
            
            self.raw_logs = content
            self.all_log_lines = lines
            
            # Calculer les statistiques
            self.calculate_stats()
            
            # Appliquer les filtres
            self.filter_logs()
            
            # Mettre à jour le statut
            self.update_status()
            
            self.status_label.setText(
                f"⚠️ Fichier volumineux - Affichage des {len(lines)} dernières lignes"
            )
            
        except Exception as e:
            logger.error(f"Erreur lors du chargement du gros fichier: {e}")
            self.log_text.setPlainText(f"❌ Erreur: {str(e)}")
    
    def calculate_stats(self):
        """Calcule les statistiques sur les logs"""
        stats = Counter()
        total = 0
        
        for line in self.all_log_lines:
            total += 1
            for level in ['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG']:
                if f" - {level} - " in line:
                    stats[level] += 1
                    break
        
        self.log_stats = dict(stats)
        self.log_stats['TOTAL'] = total
        self.update_stats(self.log_stats)
    
    def update_stats(self, stats):
        """Met à jour l'affichage des statistiques"""
        for level in ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']:
            count = stats.get(level, 0)
            self.stats_labels[level].setText(f"{level}: {count}")
        
        total = stats.get('TOTAL', 0)
        self.total_lines_label.setText(f"Total: {total} lignes")
    
    def update_status(self):
        """Met à jour la barre de statut"""
        if not self.log_file_path or not self.log_file_path.exists():
            return
        
        try:
            file_size = self.log_file_path.stat().st_size
            size_mb = file_size / (1024 * 1024)
            last_modified = datetime.fromtimestamp(self.log_file_path.stat().st_mtime)
            
            displayed_lines = len(self.log_text.toPlainText().split('\n'))
            
            self.status_label.setText(
                f"📋 {self.log_file_path.name} | "
                f"Taille: {size_mb:.2f} MB | "
                f"Lignes affichées: {displayed_lines} | "
                f"Dernière modif: {last_modified.strftime('%d/%m/%Y %H:%M:%S')}"
            )
        except Exception as e:
            logger.error(f"Erreur lors de la mise à jour du statut: {e}")
    
    def filter_logs(self):
        """Filtre les logs selon les critères sélectionnés"""
        if not hasattr(self, 'all_log_lines') or not self.all_log_lines:
            return
        
        level_filter = self.level_filter.currentText()
        search_text = self.search_field.text().lower()
        filter_date = self.date_filter.date().toPython()
        
        # Obtenir la position de scroll actuelle
        scrollbar = self.log_text.verticalScrollBar()
        was_at_bottom = scrollbar.value() >= scrollbar.maximum() - 10
        
        # Vider le texte actuel
        self.log_text.clear()
        
        filtered_count = 0
        displayed_count = 0
        
        for line in self.all_log_lines:
            # Filtrer par niveau
            if level_filter != "Tous":
                if f" - {level_filter} - " not in line:
                    continue
            
            # Filtrer par date (extraire la date de la ligne de log)
            try:
                # Format attendu: "YYYY-MM-DD HH:MM:SS"
                date_match = re.search(r'(\d{4}-\d{2}-\d{2})', line)
                if date_match:
                    line_date = datetime.strptime(date_match.group(1), '%Y-%m-%d').date()
                    if line_date < filter_date:
                        continue
            except (ValueError, AttributeError):
                pass  # Si on ne peut pas parser la date, on garde la ligne
            
            # Filtrer par recherche
            if search_text and search_text not in line.lower():
                continue
            
            filtered_count += 1
            
            # Limiter le nombre de lignes affichées
            if displayed_count >= self.max_lines_to_display:
                break
            
            # Ajouter la ligne avec le formatage approprié
            self.append_log_line(line)
            displayed_count += 1
        
        # Mettre à jour le highlighter
        if search_text:
            self.highlighter.set_search_pattern(search_text)
        else:
            self.highlighter.set_search_pattern(None)
        
        # Scroll vers le bas si c'était le cas avant
        if was_at_bottom and self.auto_scroll_cb.isChecked():
            cursor = self.log_text.textCursor()
            cursor.movePosition(QTextCursor.MoveOperation.End)
            self.log_text.setTextCursor(cursor)
            scrollbar.setValue(scrollbar.maximum())
        
        # Mettre à jour le statut
        if displayed_count >= self.max_lines_to_display:
            self.status_label.setText(
                f"⚠️ Limite atteinte: {displayed_count} lignes affichées sur {filtered_count} correspondantes"
            )
        else:
            self.update_status()
    
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
            format_default = QTextCharFormat()
            format_default.setForeground(QColor(0, 0, 0))
            cursor.setCharFormat(format_default)
        
        # Ajouter la ligne
        cursor.insertText(line + '\n')
    
    def on_search_changed(self, text):
        """Appelé quand le texte de recherche change"""
        self.current_search_index = -1
        self.search_matches = []
        
        if text:
            # Trouver toutes les occurrences
            content = self.log_text.toPlainText()
            pattern = re.compile(re.escape(text), re.IGNORECASE)
            for match in pattern.finditer(content):
                self.search_matches.append(match.start())
            
            # Mettre à jour le highlighter
            self.highlighter.set_search_pattern(text)
            
            # Mettre à jour les boutons de navigation
            count = len(self.search_matches)
            self.search_count_label.setText(f"{count} résultat{'s' if count != 1 else ''}")
            self.search_prev_btn.setEnabled(count > 0)
            self.search_next_btn.setEnabled(count > 0)
            
            if count > 0:
                self.search_next()  # Aller au premier résultat
        else:
            self.highlighter.set_search_pattern(None)
            self.search_count_label.setText("")
            self.search_prev_btn.setEnabled(False)
            self.search_next_btn.setEnabled(False)
        
        # Re-filtrer pour appliquer la recherche
        self.filter_logs()
    
    def search_next(self):
        """Aller au résultat de recherche suivant"""
        if not self.search_matches:
            return
        
        self.current_search_index = (self.current_search_index + 1) % len(self.search_matches)
        self.go_to_search_result()
    
    def search_previous(self):
        """Aller au résultat de recherche précédent"""
        if not self.search_matches:
            return
        
        self.current_search_index = (self.current_search_index - 1) % len(self.search_matches)
        self.go_to_search_result()
    
    def go_to_search_result(self):
        """Va au résultat de recherche actuel"""
        if not self.search_matches or self.current_search_index < 0:
            return
        
        position = self.search_matches[self.current_search_index]
        cursor = self.log_text.textCursor()
        cursor.setPosition(position)
        self.log_text.setTextCursor(cursor)
        self.log_text.centerCursor()
        
        # Mettre à jour le compteur
        count = len(self.search_matches)
        self.search_count_label.setText(
            f"{self.current_search_index + 1}/{count}"
        )
    
    def zoom_in(self):
        """Augmente la taille de police"""
        self.font_size = min(self.font_size + 1, 20)
        self.update_font_size()
    
    def zoom_out(self):
        """Réduit la taille de police"""
        self.font_size = max(self.font_size - 1, 6)
        self.update_font_size()
    
    def update_font_size(self):
        """Met à jour la taille de police"""
        font = QFont("Courier New", self.font_size)
        self.log_text.setFont(font)
        self.zoom_label.setText(f"{self.font_size}pt")
    
    def on_max_lines_changed(self, value):
        """Appelé quand la limite de lignes change"""
        self.max_lines_to_display = value
        self.filter_logs()
    
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
            self.update_stats({})
    
    def export_logs(self):
        """Exporte les logs affichés dans un fichier"""
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
                QMessageBox.information(
                    self,
                    "Export réussi",
                    f"Les logs ont été exportés vers:\n{file_path}\n\n"
                    f"Lignes exportées: {len(content.split(chr(10)))}"
                )
            except Exception as e:
                QMessageBox.critical(self, "Erreur d'export", f"Erreur lors de l'export:\n{str(e)}")
                logger.error(f"Erreur lors de l'export des logs: {e}")
    
    def closeEvent(self, event):
        """Arrête le timer lors de la fermeture"""
        if self.refresh_timer.isActive():
            self.refresh_timer.stop()
        event.accept()
