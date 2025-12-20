#!usr/bin/env python
# -*- coding: utf8 -*-
# maintainer: Fad

from datetime import datetime

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QSplitter,
    QStackedWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from ..cstatic import CConstants, logger
from .common import Button, FWidget


class HelpPageWidget(QDialog, FWidget):
    """Widget de page d'aide moderne avec navigation et recherche"""
    
    def __init__(self, parent=None, *args, **kwargs):
        QDialog.__init__(self, parent, *args, **kwargs)
        FWidget.__init__(self, parent, *args, **kwargs)
        
        self.setWindowTitle(f"📚 Aide - {CConstants.APP_NAME}")
        self.setMinimumSize(1000, 700)
        
        self.init_ui()
        self.load_help_content()
    
    def init_ui(self):
        """Initialise l'interface utilisateur"""
        main_layout = QVBoxLayout(self)
        
        # En-tête
        header = QLabel(f"📚 Centre d'aide - {CConstants.APP_NAME}")
        header.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            color: #2c3e50;
            padding: 15px;
            background-color: #f8f9fa;
            border-bottom: 2px solid #dee2e6;
        """)
        main_layout.addWidget(header)
        
        # Contenu principal avec splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Panneau de navigation (gauche)
        nav_widget = QWidget()
        nav_layout = QVBoxLayout(nav_widget)
        nav_layout.setContentsMargins(0, 0, 0, 0)
        
        nav_label = QLabel("📑 Sections")
        nav_label.setStyleSheet("font-weight: bold; font-size: 14px; padding: 10px;")
        nav_layout.addWidget(nav_label)
        
        self.nav_list = QListWidget()
        self.nav_list.setMaximumWidth(250)
        self.nav_list.currentRowChanged.connect(self.change_section)
        nav_layout.addWidget(self.nav_list)
        
        splitter.addWidget(nav_widget)
        
        # Zone de contenu (droite)
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        
        self.stacked_widget = QStackedWidget()
        content_layout.addWidget(self.stacked_widget)
        
        splitter.addWidget(content_widget)
        splitter.setStretchFactor(1, 1)
        
        main_layout.addWidget(splitter)
        
        # Bouton fermer
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        close_btn = Button("✅ Fermer")
        close_btn.clicked.connect(self.close)
        button_layout.addWidget(close_btn)
        main_layout.addLayout(button_layout)
    
    def load_help_content(self):
        """Charge le contenu d'aide"""
        sections = [
            ("🏠 Accueil", self.create_home_content),
            ("🚀 Démarrage rapide", self.create_quickstart_content),
            ("👤 Gestion des utilisateurs", self.create_users_help_content),
            ("🔐 Licences", self.create_license_help_content),
            ("⚙️ Paramètres", self.create_settings_help_content),
            ("🛠️ Outils", self.create_tools_help_content),
            ("❓ FAQ", self.create_faq_content),
            ("ℹ️ À propos", self.create_about_content),
        ]
        
        for title, content_func in sections:
            # Ajouter à la liste de navigation
            item = QListWidgetItem(title)
            item.setFont(QFont("Arial", 11))
            self.nav_list.addItem(item)
            
            # Créer le contenu
            content_widget = self.create_content_widget(content_func())
            self.stacked_widget.addWidget(content_widget)
        
        # Sélectionner la première section
        self.nav_list.setCurrentRow(0)
    
    def create_content_widget(self, html_content):
        """Crée un widget de contenu avec HTML"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(20, 20, 20, 20)
        
        text_edit = QTextEdit()
        text_edit.setReadOnly(True)
        text_edit.setHtml(html_content)
        text_edit.setStyleSheet("""
            QTextEdit {
                background-color: white;
                border: 1px solid #dee2e6;
                border-radius: 5px;
                font-size: 13px;
                line-height: 1.6;
            }
        """)
        
        layout.addWidget(text_edit)
        return widget
    
    def change_section(self, index):
        """Change la section affichée"""
        if index >= 0:
            self.stacked_widget.setCurrentIndex(index)
    
    def create_home_content(self):
        """Contenu de la page d'accueil"""
        return f"""
        <div style="max-width: 900px; margin: 0 auto;">
            <h1 style="color: #2c3e50; border-bottom: 3px solid #007bff; padding-bottom: 10px;">
                Bienvenue dans le centre d'aide
            </h1>
            
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 10px; margin: 20px 0;">
                <h2 style="color: white; margin-top: 0;">🎯 {CConstants.APP_NAME}</h2>
                <p style="font-size: 16px; margin-bottom: 0;">
                    Version {CConstants.APP_VERSION}<br>
                    Application de gestion complète et professionnelle
                </p>
            </div>
            
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin: 30px 0;">
                <div style="background-color: #f8f9fa; padding: 20px; border-radius: 8px; border-left: 4px solid #007bff;">
                    <h3 style="color: #007bff; margin-top: 0;">🚀 Démarrage rapide</h3>
                    <p>Découvrez comment utiliser rapidement les fonctionnalités principales de l'application.</p>
                </div>
                
                <div style="background-color: #f8f9fa; padding: 20px; border-radius: 8px; border-left: 4px solid #28a745;">
                    <h3 style="color: #28a745; margin-top: 0;">👤 Utilisateurs</h3>
                    <p>Gérez les utilisateurs, les permissions et les sessions.</p>
                </div>
                
                <div style="background-color: #f8f9fa; padding: 20px; border-radius: 8px; border-left: 4px solid #ffc107;">
                    <h3 style="color: #ffc107; margin-top: 0;">🔐 Licences</h3>
                    <p>Informations sur l'activation et la gestion des licences.</p>
                </div>
                
                <div style="background-color: #f8f9fa; padding: 20px; border-radius: 8px; border-left: 4px solid #dc3545;">
                    <h3 style="color: #dc3545; margin-top: 0;">⚙️ Paramètres</h3>
                    <p>Configurez l'application selon vos préférences.</p>
                </div>
            </div>
            
            <div style="background-color: #e7f3ff; border-left: 4px solid #2196F3; padding: 15px; margin: 20px 0; border-radius: 5px;">
                <h3 style="color: #1976D2; margin-top: 0;">💡 Astuce</h3>
                <p style="margin-bottom: 0;">
                    Utilisez le menu de navigation à gauche pour accéder rapidement aux différentes sections d'aide.
                </p>
            </div>
        </div>
        """
    
    def create_quickstart_content(self):
        """Contenu du démarrage rapide"""
        return """
        <div style="max-width: 900px; margin: 0 auto;">
            <h1 style="color: #2c3e50; border-bottom: 3px solid #28a745; padding-bottom: 10px;">
                🚀 Démarrage rapide
            </h1>
            
            <h2 style="color: #495057; margin-top: 30px;">Premiers pas</h2>
            <ol style="line-height: 2;">
                <li><strong>Activation de la licence</strong><br>
                    Au premier lancement, vous devrez activer votre licence. Suivez les instructions à l'écran.
                </li>
                <li><strong>Configuration de l'organisation</strong><br>
                    Renseignez les informations de votre organisation dans les paramètres.
                </li>
                <li><strong>Création d'utilisateurs</strong><br>
                    Créez vos comptes utilisateurs depuis le menu Administration.
                </li>
                <li><strong>Personnalisation</strong><br>
                    Configurez les paramètres selon vos besoins (thème, devise, etc.).
                </li>
            </ol>
            
            <h2 style="color: #495057; margin-top: 30px;">Raccourcis clavier utiles</h2>
            <div style="background-color: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0;">
                <table style="width: 100%; border-collapse: collapse;">
                    <tr style="background-color: #e9ecef;">
                        <th style="padding: 10px; text-align: left; border: 1px solid #dee2e6;">Action</th>
                        <th style="padding: 10px; text-align: left; border: 1px solid #dee2e6;">Raccourci</th>
                    </tr>
                    <tr>
                        <td style="padding: 10px; border: 1px solid #dee2e6;">Verrouiller l'application</td>
                        <td style="padding: 10px; border: 1px solid #dee2e6;"><code>Ctrl+V</code></td>
                    </tr>
                    <tr style="background-color: #f8f9fa;">
                        <td style="padding: 10px; border: 1px solid #dee2e6;">Administration</td>
                        <td style="padding: 10px; border: 1px solid #dee2e6;"><code>Ctrl+G</code></td>
                    </tr>
                    <tr>
                        <td style="padding: 10px; border: 1px solid #dee2e6;">Visualiser les logs</td>
                        <td style="padding: 10px; border: 1px solid #dee2e6;"><code>Ctrl+L</code></td>
                    </tr>
                    <tr style="background-color: #f8f9fa;">
                        <td style="padding: 10px; border: 1px solid #dee2e6;">Quitter</td>
                        <td style="padding: 10px; border: 1px solid #dee2e6;"><code>Ctrl+Q</code></td>
                    </tr>
                </table>
            </div>
        </div>
        """
    
    def create_users_help_content(self):
        """Contenu d'aide pour la gestion des utilisateurs"""
        return """
        <div style="max-width: 900px; margin: 0 auto;">
            <h1 style="color: #2c3e50; border-bottom: 3px solid #28a745; padding-bottom: 10px;">
                👤 Gestion des utilisateurs
            </h1>
            
            <h2 style="color: #495057; margin-top: 30px;">Créer un utilisateur</h2>
            <ol style="line-height: 2;">
                <li>Allez dans <strong>Préférences → Gestion Administration</strong></li>
                <li>Ouvrez l'onglet <strong>"Gestion d'utilisateurs"</strong></li>
                <li>Cliquez sur <strong>"➕ Ajouter"</strong></li>
                <li>Remplissez le formulaire :
                    <ul>
                        <li><strong>Identifiant</strong> : nom d'utilisateur unique</li>
                        <li><strong>Mot de passe</strong> : mot de passe sécurisé (min. 6 caractères)</li>
                        <li><strong>Téléphone</strong> : numéro de contact (optionnel)</li>
                        <li><strong>Groupe</strong> : Administrateur ou Utilisateur standard</li>
                    </ul>
                </li>
                <li>Cliquez sur <strong>"💾 Enregistrer"</strong></li>
            </ol>
            
            <h2 style="color: #495057; margin-top: 30px;">Modifier un utilisateur</h2>
            <ol style="line-height: 2;">
                <li>Sélectionnez l'utilisateur dans la liste de gauche</li>
                <li>Cliquez sur <strong>"✏️ Modifier"</strong></li>
                <li>Modifiez les informations souhaitées (le nom d'utilisateur ne peut pas être changé)</li>
                <li>Sauvegardez les modifications</li>
            </ol>
            
            <h2 style="color: #495057; margin-top: 30px;">Activer/Désactiver un compte</h2>
            <p>Pour activer ou désactiver un compte utilisateur :</p>
            <ol style="line-height: 2;">
                <li>Sélectionnez l'utilisateur dans la liste</li>
                <li>Cliquez sur le bouton <strong>"✅ Activer"</strong> ou <strong>"❌ Désactiver"</strong></li>
                <li>Confirmez l'action</li>
            </ol>
            <div style="background-color: #fff3cd; border-left: 4px solid #ffc107; padding: 15px; margin: 20px 0; border-radius: 5px;">
                <strong>⚠️ Note :</strong> Un compte désactivé ne pourra plus se connecter à l'application.
            </div>
            
            <h2 style="color: #495057; margin-top: 30px;">Rechercher un utilisateur</h2>
            <p>Utilisez la barre de recherche en haut de la liste pour filtrer les utilisateurs par :</p>
            <ul style="line-height: 2;">
                <li>Nom d'utilisateur</li>
                <li>Numéro de téléphone</li>
                <li>Groupe (Administrateur/Utilisateur)</li>
            </ul>
            
            <h2 style="color: #495057; margin-top: 30px;">Groupes d'utilisateurs</h2>
            <div style="background-color: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0;">
                <h3 style="color: #495057; margin-top: 0;">👑 Administrateur</h3>
                <ul style="line-height: 2;">
                    <li>Accès complet à toutes les fonctionnalités</li>
                    <li>Gestion des utilisateurs</li>
                    <li>Accès aux paramètres système</li>
                    <li>Export/Import de base de données</li>
                </ul>
                
                <h3 style="color: #495057; margin-top: 20px;">👤 Utilisateur standard</h3>
                <ul style="line-height: 2;">
                    <li>Accès aux fonctionnalités de base</li>
                    <li>Pas d'accès à l'administration</li>
                    <li>Pas de modification des paramètres système</li>
                </ul>
            </div>
        </div>
        """
    
    def create_license_help_content(self):
        """Contenu d'aide pour les licences"""
        return """
        <div style="max-width: 900px; margin: 0 auto;">
            <h1 style="color: #2c3e50; border-bottom: 3px solid #ffc107; padding-bottom: 10px;">
                🔐 Gestion des licences
            </h1>
            
            <h2 style="color: #495057; margin-top: 30px;">Activer une licence complète</h2>
            <ol style="line-height: 2;">
                <li>Allez dans <strong>Licence → Activation</strong></li>
                <li>Copiez le <strong>code d'identification de votre machine</strong></li>
                <li>Communiquez ce code au support technique</li>
                <li>Remplissez le formulaire avec :
                    <ul>
                        <li>Le nom du propriétaire de la licence</li>
                        <li>Le code de licence fourni par le support</li>
                    </ul>
                </li>
                <li>Cliquez sur <strong>"✅ Activer la licence"</strong></li>
            </ol>
            
            <h2 style="color: #495057; margin-top: 30px;">Activer une licence d'évaluation</h2>
            <p>Pour tester l'application gratuitement pendant 60 jours :</p>
            <ol style="line-height: 2;">
                <li>Allez dans <strong>Licence → Activation</strong></li>
                <li>Cliquez sur <strong>"🚀 Activer l'évaluation (60 jours)"</strong></li>
                <li>La licence d'évaluation sera activée automatiquement</li>
            </ol>
            <div style="background-color: #fff3cd; border-left: 4px solid #ffc107; padding: 15px; margin: 20px 0; border-radius: 5px;">
                <strong>⚠️ Note :</strong> La licence d'évaluation ne peut être utilisée qu'une seule fois par machine.
            </div>
            
            <h2 style="color: #495057; margin-top: 30px;">Vérifier le statut de votre licence</h2>
            <p>Dans la fenêtre de gestion de licence, vous pouvez voir :</p>
            <ul style="line-height: 2;">
                <li>Le type de licence (complète ou d'évaluation)</li>
                <li>Le propriétaire de la licence</li>
                <li>La date d'activation</li>
                <li>La date d'expiration (pour les licences d'évaluation)</li>
                <li>Le temps restant (avec barre de progression)</li>
            </ul>
            
            <h2 style="color: #495057; margin-top: 30px;">Exporter la licence</h2>
            <p>Pour sauvegarder vos informations de licence :</p>
            <ol style="line-height: 2;">
                <li>Dans la fenêtre de gestion de licence</li>
                <li>Cliquez sur <strong>"📄 Exporter la licence"</strong></li>
                <li>Le fichier de licence sera ouvert dans l'explorateur de fichiers</li>
            </ol>
            
            <h2 style="color: #495057; margin-top: 30px;">Révoquer une licence</h2>
            <div style="background-color: #f8d7da; border-left: 4px solid #dc3545; padding: 15px; margin: 20px 0; border-radius: 5px;">
                <strong>🚨 Attention :</strong> La révocation d'une licence est définitive. Vous devrez réactiver une licence pour continuer à utiliser l'application.
            </div>
            <p>Pour révoquer une licence :</p>
            <ol style="line-height: 2;">
                <li>Dans la fenêtre de gestion de licence</li>
                <li>Cliquez sur <strong>"🗑️ Révoquer la licence"</strong></li>
                <li>Confirmez l'action</li>
            </ol>
        </div>
        """
    
    def create_settings_help_content(self):
        """Contenu d'aide pour les paramètres"""
        return """
        <div style="max-width: 900px; margin: 0 auto;">
            <h1 style="color: #2c3e50; border-bottom: 3px solid #6c757d; padding-bottom: 10px;">
                ⚙️ Paramètres de l'application
            </h1>
            
            <h2 style="color: #495057; margin-top: 30px;">Accéder aux paramètres</h2>
            <p>Les paramètres sont accessibles depuis :</p>
            <ul style="line-height: 2;">
                <li><strong>Préférences → Gestion Administration</strong> (onglet Paramètre)</li>
                <li>Raccourci clavier : <code>Ctrl+G</code></li>
            </ul>
            
            <h2 style="color: #495057; margin-top: 30px;">Paramètres disponibles</h2>
            
            <h3 style="color: #495057; margin-top: 20px;">🌐 URL du serveur</h3>
            <p>L'adresse du serveur pour la synchronisation des données.</p>
            
            <h3 style="color: #495057; margin-top: 20px;">🔐 Identification</h3>
            <p>Active ou désactive la nécessité de se connecter pour utiliser l'application.</p>
            <div style="background-color: #e7f3ff; border-left: 4px solid #2196F3; padding: 15px; margin: 20px 0; border-radius: 5px;">
                <strong>💡 Astuce :</strong> Désactiver l'identification permet d'utiliser l'application sans connexion, mais réduit la sécurité.
            </div>
            
            <h3 style="color: #495057; margin-top: 20px;">📊 Menu vertical</h3>
            <p>Active ou désactive l'affichage du menu vertical dans l'interface.</p>
            
            <h3 style="color: #495057; margin-top: 20px;">🔢 Nombre de chiffres après la virgule</h3>
            <p>Définit la précision des nombres décimaux affichés dans l'application.</p>
            
            <h3 style="color: #495057; margin-top: 20px;">💰 Devise</h3>
            <p>Choisissez la devise par défaut (Euro, Dollar, XOF).</p>
            
            <h3 style="color: #495057; margin-top: 20px;">📍 Position du menu</h3>
            <p>Définit la position du menu vertical : Gauche, Droite, Haut ou Bas.</p>
        </div>
        """
    
    def create_tools_help_content(self):
        """Contenu d'aide pour les outils"""
        return """
        <div style="max-width: 900px; margin: 0 auto;">
            <h1 style="color: #2c3e50; border-bottom: 3px solid #17a2b8; padding-bottom: 10px;">
                🛠️ Outils disponibles
            </h1>
            
            <h2 style="color: #495057; margin-top: 30px;">📋 Visualiser les logs</h2>
            <p>Pour consulter les logs de l'application :</p>
            <ol style="line-height: 2;">
                <li>Allez dans <strong>Fichier → Outils → Visualiser les logs</strong></li>
                <li>Ou utilisez le raccourci <code>Ctrl+L</code></li>
            </ol>
            <p>Le visualiseur de logs permet de :</p>
            <ul style="line-height: 2;">
                <li>Filtrer les logs par niveau (DEBUG, INFO, WARNING, ERROR, CRITICAL)</li>
                <li>Rechercher du texte dans les logs</li>
                <li>Actualiser automatiquement les logs toutes les 5 secondes</li>
                <li>Exporter les logs dans un fichier</li>
            </ul>
            
            <h2 style="color: #495057; margin-top: 30px;">💾 Sauvegarder la base de données</h2>
            <p>Pour créer une sauvegarde de votre base de données :</p>
            <ol style="line-height: 2;">
                <li>Allez dans <strong>Fichier → Base de données → Sauvegarder</strong></li>
                <li>Ou utilisez le raccourci <code>Alt+E</code></li>
                <li>Choisissez l'emplacement de sauvegarde</li>
            </ol>
            
            <h2 style="color: #495057; margin-top: 30px;">📥 Importer une base de données</h2>
            <p>Pour restaurer une sauvegarde :</p>
            <ol style="line-height: 2;">
                <li>Allez dans <strong>Fichier → Base de données → Importation db</strong></li>
                <li>Ou utilisez le raccourci <code>Alt+I</code></li>
                <li>Sélectionnez le fichier de sauvegarde</li>
            </ol>
            <div style="background-color: #fff3cd; border-left: 4px solid #ffc107; padding: 15px; margin: 20px 0; border-radius: 5px;">
                <strong>⚠️ Attention :</strong> L'importation remplace la base de données actuelle. Assurez-vous d'avoir une sauvegarde récente.
            </div>
        </div>
        """
    
    def create_faq_content(self):
        """Contenu FAQ"""
        return """
        <div style="max-width: 900px; margin: 0 auto;">
            <h1 style="color: #2c3e50; border-bottom: 3px solid #6f42c1; padding-bottom: 10px;">
                ❓ Questions fréquentes (FAQ)
            </h1>
            
            <div style="margin-top: 30px;">
                <h2 style="color: #495057;">🔐 Licence</h2>
                
                <h3 style="color: #6c757d;">Q: Puis-je utiliser une licence d'évaluation plusieurs fois ?</h3>
                <p><strong>R:</strong> Non, la licence d'évaluation ne peut être activée qu'une seule fois par machine.</p>
                
                <h3 style="color: #6c757d; margin-top: 20px;">Q: Que faire si ma licence expire ?</h3>
                <p><strong>R:</strong> Contactez le support technique avec votre code de machine pour obtenir une licence complète.</p>
                
                <h3 style="color: #6c757d; margin-top: 20px;">Q: Puis-je transférer ma licence sur une autre machine ?</h3>
                <p><strong>R:</strong> Les licences sont liées à la machine. Contactez le support pour un transfert.</p>
            </div>
            
            <div style="margin-top: 40px;">
                <h2 style="color: #495057;">👤 Utilisateurs</h2>
                
                <h3 style="color: #6c757d;">Q: Comment réinitialiser un mot de passe oublié ?</h3>
                <p><strong>R:</strong> Un administrateur peut modifier le mot de passe d'un utilisateur depuis la gestion des utilisateurs.</p>
                
                <h3 style="color: #6c757d; margin-top: 20px;">Q: Puis-je supprimer un utilisateur connecté ?</h3>
                <p><strong>R:</strong> Non, vous devez d'abord vous déconnecter avant de pouvoir supprimer votre propre compte.</p>
                
                <h3 style="color: #6c757d; margin-top: 20px;">Q: Quelle est la différence entre Administrateur et Utilisateur ?</h3>
                <p><strong>R:</strong> Les administrateurs ont accès à toutes les fonctionnalités, y compris la gestion des utilisateurs et des paramètres système. Les utilisateurs standards ont un accès limité aux fonctionnalités de base.</p>
            </div>
            
            <div style="margin-top: 40px;">
                <h2 style="color: #495057;">💾 Données</h2>
                
                <h3 style="color: #6c757d;">Q: À quelle fréquence dois-je sauvegarder ?</h3>
                <p><strong>R:</strong> Il est recommandé de sauvegarder régulièrement, idéalement quotidiennement ou après des modifications importantes.</p>
                
                <h3 style="color: #6c757d; margin-top: 20px;">Q: Où sont stockées les données ?</h3>
                <p><strong>R:</strong> Les données sont stockées dans un fichier SQLite local (database.db) dans le répertoire de l'application.</p>
            </div>
            
            <div style="margin-top: 40px;">
                <h2 style="color: #495057;">🛠️ Problèmes techniques</h2>
                
                <h3 style="color: #6c757d;">Q: L'application ne démarre pas</h3>
                <p><strong>R:</strong> Vérifiez les logs de l'application (Ctrl+L) pour identifier l'erreur. Assurez-vous d'avoir les permissions nécessaires.</p>
                
                <h3 style="color: #6c757d; margin-top: 20px;">Q: Comment contacter le support ?</h3>
                <p><strong>R:</strong> Vous pouvez contacter le support technique via les coordonnées affichées dans la fenêtre d'activation de licence.</p>
            </div>
        </div>
        """
    
    def create_about_content(self):
        """Contenu À propos"""
        try:
            tel = getattr(CConstants, 'TEL_AUT', 'Non disponible')
            email = getattr(CConstants, 'EMAIL_AUT', 'Non disponible')
            autor = getattr(CConstants, 'AUTOR', 'Non disponible')
        except:
            tel = "Non disponible"
            email = "Non disponible"
            autor = "Non disponible"
        
        return f"""
        <div style="max-width: 900px; margin: 0 auto;">
            <h1 style="color: #2c3e50; border-bottom: 3px solid #6c757d; padding-bottom: 10px;">
                ℹ️ À propos
            </h1>
            
            <div style="text-align: center; margin: 40px 0;">
                <h2 style="color: #2c3e50; font-size: 32px;">{CConstants.APP_NAME}</h2>
                <p style="font-size: 18px; color: #6c757d;">Version {CConstants.APP_VERSION}</p>
            </div>
            
            <div style="background-color: #f8f9fa; padding: 30px; border-radius: 10px; margin: 30px 0;">
                <h3 style="color: #495057; margin-top: 0;">📝 Description</h3>
                <p style="font-size: 15px; line-height: 1.8;">
                    Application de gestion complète et professionnelle offrant une interface intuitive
                    pour la gestion des utilisateurs, des données et des paramètres système.
                </p>
            </div>
            
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; margin: 30px 0;">
                <div style="background-color: #e7f3ff; padding: 20px; border-radius: 8px;">
                    <h3 style="color: #1976D2; margin-top: 0;">👨‍💻 Développeur</h3>
                    <p style="margin-bottom: 0;">{autor}</p>
                </div>
                
                <div style="background-color: #fff3e0; padding: 20px; border-radius: 8px;">
                    <h3 style="color: #F57C00; margin-top: 0;">📞 Contact</h3>
                    <p style="margin-bottom: 5px;"><strong>Téléphone:</strong> {tel}</p>
                    <p style="margin-bottom: 0;"><strong>Email:</strong> {email}</p>
                </div>
            </div>
            
            <div style="background-color: #f0f0f0; padding: 20px; border-radius: 8px; margin: 30px 0; text-align: center;">
                <p style="margin: 0; color: #6c757d; font-size: 14px;">
                    © {datetime.now().year} {autor}. Tous droits réservés.
                </p>
            </div>
            
            <div style="background-color: #e7f3ff; border-left: 4px solid #2196F3; padding: 15px; margin: 20px 0; border-radius: 5px;">
                <h3 style="color: #1976D2; margin-top: 0;">💡 Suggestions et retours</h3>
                <p style="margin-bottom: 0;">
                    Votre avis compte ! N'hésitez pas à nous contacter pour des suggestions d'amélioration
                    ou pour signaler des problèmes.
                </p>
            </div>
        </div>
        """
