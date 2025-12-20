#!/usr/bin/env python
# -*- coding: utf-8 -*-
# maintainer: Fad


import errno
import os
import platform
import shutil
import sqlite3
from datetime import datetime

import psutil
from PyQt6.QtWidgets import QFileDialog, QMessageBox, QWidget

from .models import DB_FILE, Organization, Version, dbh, init_database
from .ui.util import get_lcse_file, raise_error, raise_success, uopen_file
from .cstatic import logger

DATETIME = f"{datetime.now().strftime('%m-%d-%Y_%Hh%Mm%Ss')}"


def export_database_as_file():
    file_dialog = QFileDialog()
    file_path, _ = file_dialog.getSaveFileName(
        QWidget(),
        "Sauvegarder la base de Donnée.",
        "Sauvegarde du {} {}.db".format(DATETIME, Organization.get(id=1).name_orga),
        "*.db",
    )
    if not file_path:  # Check if the user canceled the dialog
        return None

    try:
        shutil.copyfile(DB_FILE, file_path)
        Version().get(id=1).update_v()
        raise_success(
            "Les données ont été exportées correctement.",
            "Conservez ce fichier précieusement car il contient toutes vos données.\n"
            "Exportez vos données régulièrement.",
        )
    except IOError:
        raise_error(
            "La base de données n'a pas pu être exportée.",
            "Vérifiez le chemin de destination puis re-essayez.\n\n                   "
            "Demandez de l'aide si le problème persiste.",
        )


def export_backup(folder=None, dst_folder=None):
    print("Exporting ...")
    directory = str(QFileDialog.getExistingDirectory(QWidget(), "Select Directory"))
    path_backup = "{path}-{date}-{name}".format(
        path=os.path.join(directory, "BACKUP"),
        date=DATETIME,
        name=Organization.get(id=1).name_orga,
    )

    if not directory:
        return None
    try:
        # TODO Savegarde version incremat de in db
        shutil.copyfile(DB_FILE, os.path.join(path_backup, DB_FILE))
        Version().get(id=1).update_v()
    except IOError:
        print("Error of copy database file")
    except Exception as e:
        print(e)

    try:
        if folder:
            copyanything(folder, os.path.join(path_backup, dst_folder))
        raise_success(
            "Le backup à été fait correctement.",
            """Conservez le dossier {} précieusement car il contient toutes vos données. Exportez vos données régulièrement.
            """.format(
                path_backup
            ),
        )
    except OSError:
        raise_error(
            "Le backup n'a pas pu être fait correctement.",
            "Vérifiez le chemin de destination puis re-essayez.\n"
            "\n Demandez de l'aide si le problème persiste.",
        )


def validate_sqlite_database(db_path):
    """
    Valide qu'un fichier est une base de données SQLite valide et vérifie son intégrité.
    
    Args:
        db_path (str): Chemin vers le fichier de base de données
        
    Returns:
        tuple: (is_valid: bool, integrity_check: str, error_message: str)
    """
    try:
        # Vérifier que le fichier existe
        if not os.path.exists(db_path):
            return False, None, "Le fichier n'existe pas"
        
        # Vérifier que c'est un fichier (pas un répertoire)
        if not os.path.isfile(db_path):
            return False, None, "Le chemin spécifié n'est pas un fichier"
        
        # Vérifier la taille du fichier (doit être > 0)
        if os.path.getsize(db_path) == 0:
            return False, None, "Le fichier est vide"
        
        # Vérifier que c'est une base SQLite valide en essayant de l'ouvrir
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Vérifier l'intégrité de la base de données
            cursor.execute("PRAGMA integrity_check")
            integrity_result = cursor.fetchone()
            
            # Vérifier que la base de données contient des tables
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            
            conn.close()
            
            # Vérifier l'intégrité
            if integrity_result and integrity_result[0] != "ok":
                return False, integrity_result[0], f"La base de données est corrompue: {integrity_result[0]}"
            
            # Vérifier qu'il y a au moins une table
            if not tables:
                return False, None, "La base de données ne contient aucune table"
            
            return True, "ok", None
            
        except sqlite3.Error as e:
            return False, None, f"Erreur SQLite: {str(e)}"
        except Exception as e:
            return False, None, f"Erreur lors de la validation: {str(e)}"
            
    except Exception as e:
        return False, None, f"Erreur lors de la validation du fichier: {str(e)}"


def get_database_info(db_path):
    """
    Récupère des informations sur une base de données SQLite.
    
    Args:
        db_path (str): Chemin vers le fichier de base de données
        
    Returns:
        dict: Dictionnaire contenant les informations (taille, date, nombre de tables, etc.)
    """
    info = {
        'path': db_path,
        'size': 0,
        'size_mb': 0,
        'modified': None,
        'tables_count': 0,
        'tables': [],
        'version': None,
        'organization': None
    }
    
    try:
        # Informations sur le fichier
        if os.path.exists(db_path):
            stat = os.stat(db_path)
            info['size'] = stat.st_size
            info['size_mb'] = round(stat.st_size / (1024 * 1024), 2)
            info['modified'] = datetime.fromtimestamp(stat.st_mtime)
        
        # Informations sur la base de données
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Compter les tables
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            info['tables_count'] = len(tables)
            info['tables'] = [table[0] for table in tables]
            
            # Essayer de récupérer la version et l'organisation si les tables existent
            try:
                cursor.execute("SELECT display_name FROM version WHERE id=1")
                version_result = cursor.fetchone()
                if version_result:
                    info['version'] = version_result[0]
            except:
                pass
            
            try:
                cursor.execute("SELECT name_orga FROM organization WHERE id=1")
                org_result = cursor.fetchone()
                if org_result:
                    info['organization'] = org_result[0]
            except:
                pass
            
            conn.close()
        except:
            pass
            
    except Exception as e:
        logger.warning(f"Erreur lors de la récupération des informations de la base de données: {e}")
    
    return info


def import_backup(folder=None, dst_folder=None):
    """
    Importe une sauvegarde de base de données avec validation et vérification d'intégrité.
    
    Args:
        folder: Dossier source (non utilisé actuellement)
        dst_folder: Dossier de destination (non utilisé actuellement)
    """
    try:
        # Déterminer le chemin absolu du fichier de base de données actuel
        # Utiliser DB_FILE directement qui devrait être un chemin absolu ou relatif
        if os.path.isabs(DB_FILE):
            path_db_file = DB_FILE
        else:
            # Si c'est un chemin relatif, le résoudre depuis le répertoire de travail
            path_db_file = os.path.abspath(DB_FILE)
        
        logger.info(f"Import de la base de données - Fichier actuel: {path_db_file}")
        
        # Vérifier que le fichier de base de données actuel existe
        if not os.path.exists(path_db_file):
            logger.warning(f"Le fichier de base de données actuel n'existe pas: {path_db_file}")
            # Créer le répertoire parent si nécessaire
            os.makedirs(os.path.dirname(path_db_file), exist_ok=True)
        
        # Ouvrir le dialogue de sélection de fichier
        file_dialog = QFileDialog()
        name_select_f, _ = file_dialog.getOpenFileName(
            QWidget(), 
            "📂 Sélectionner le fichier de sauvegarde à importer", 
            "", 
            "Fichiers de base de données (*.db);;Tous les fichiers (*)"
        )

        # Si l'utilisateur n'a pas sélectionné de fichier
        if not name_select_f:
            logger.info("Import annulé - aucun fichier sélectionné")
            return

        logger.info(f"Fichier sélectionné pour l'import: {name_select_f}")
        
        # Valider le fichier sélectionné
        is_valid, integrity_check, error_msg = validate_sqlite_database(name_select_f)
        
        if not is_valid:
            raise_error(
                "❌ Fichier de base de données invalide",
                f"Le fichier sélectionné n'est pas une base de données SQLite valide.\n\n"
                f"Erreur: {error_msg}\n\n"
                f"Veuillez sélectionner un fichier de sauvegarde valide."
            )
            return
        
        logger.info(f"Validation réussie - Intégrité: {integrity_check}")
        
        # Récupérer les informations sur la base de données à importer
        db_info = get_database_info(name_select_f)
        
        # Récupérer les informations sur la base de données actuelle (si elle existe)
        current_db_info = None
        if os.path.exists(path_db_file):
            current_db_info = get_database_info(path_db_file)
        
        # Préparer le message de confirmation avec les informations
        confirm_message = f"📊 Informations sur la sauvegarde à importer:\n\n"
        confirm_message += f"📁 Fichier: {os.path.basename(name_select_f)}\n"
        confirm_message += f"💾 Taille: {db_info['size_mb']} MB\n"
        if db_info['modified']:
            confirm_message += f"📅 Date de modification: {db_info['modified'].strftime('%d/%m/%Y %H:%M:%S')}\n"
        confirm_message += f"📋 Nombre de tables: {db_info['tables_count']}\n"
        if db_info['version']:
            confirm_message += f"🔖 Version: {db_info['version']}\n"
        if db_info['organization']:
            confirm_message += f"🏢 Organisation: {db_info['organization']}\n"
        
        if current_db_info:
            confirm_message += f"\n⚠️ ATTENTION:\n"
            confirm_message += f"• La base de données actuelle sera remplacée\n"
            confirm_message += f"• Une sauvegarde sera créée avant l'import\n"
            confirm_message += f"• Cette action ne peut pas être annulée\n"
        else:
            confirm_message += f"\n⚠️ ATTENTION:\n"
            confirm_message += f"• Une nouvelle base de données sera créée\n"
            confirm_message += f"• Cette action ne peut pas être annulée\n"
        
        confirm_message += f"\n💡 Voulez-vous continuer avec l'import ?"
        
        # Demander confirmation à l'utilisateur
        reply = QMessageBox.question(
            QWidget(),
            "💾 Confirmer l'import de la base de données",
            confirm_message,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply != QMessageBox.StandardButton.Yes:
            logger.info("Import annulé par l'utilisateur")
            return
        
        # Fermer la connexion à la base de données actuelle si elle est ouverte
        if dbh is not None and not dbh.is_closed():
            logger.info("Fermeture de la connexion à la base de données actuelle")
            try:
                dbh.close()
            except Exception as e:
                logger.warning(f"Erreur lors de la fermeture de la base de données: {e}")
        
        # Créer une sauvegarde de la base de données actuelle (si elle existe)
        backup_file_path = None
        if os.path.exists(path_db_file):
            try:
                backup_file_name = "Avant-{}-{}.db".format(
                    os.path.basename(DB_FILE).replace('.db', ''), 
                    DATETIME
                )
                backup_dir = os.path.dirname(path_db_file)
                backup_file_path = os.path.join(backup_dir, backup_file_name)
                
                logger.info(f"Création d'une sauvegarde: {backup_file_path}")
                shutil.copy2(path_db_file, backup_file_path)
                logger.info("✅ Sauvegarde créée avec succès")
            except Exception as e:
                logger.error(f"Erreur lors de la création de la sauvegarde: {e}")
                raise_error(
                    "❌ Erreur de sauvegarde",
                    f"Impossible de créer une sauvegarde de la base de données actuelle.\n\n"
                    f"Erreur: {str(e)}\n\n"
                    f"L'import a été annulé pour éviter la perte de données."
                )
                return
        
        # Copier le fichier sélectionné vers la base de données actuelle
        try:
            logger.info(f"Copie du fichier de sauvegarde vers: {path_db_file}")
            # Créer le répertoire parent si nécessaire
            os.makedirs(os.path.dirname(path_db_file), exist_ok=True)
            shutil.copy2(name_select_f, path_db_file)
            logger.info("✅ Fichier copié avec succès")
        except Exception as e:
            logger.error(f"Erreur lors de la copie du fichier: {e}")
            
            # Essayer de restaurer la sauvegarde si elle existe
            if backup_file_path and os.path.exists(backup_file_path):
                try:
                    logger.warning("Tentative de restauration de la sauvegarde")
                    shutil.copy2(backup_file_path, path_db_file)
                except:
                    pass
            
            raise_error(
                "❌ Erreur lors de l'import",
                f"Une erreur s'est produite lors de la copie du fichier.\n\n"
                f"Erreur: {str(e)}\n\n"
                f"Vérifiez que:\n"
                f"• Vous avez les droits d'écriture\n"
                f"• Il y a suffisamment d'espace disque\n"
                f"• Le fichier n'est pas utilisé par une autre application"
            )
            return
        
        # Réinitialiser la connexion à la base de données
        try:
            logger.info("Réinitialisation de la connexion à la base de données")
            # Réinitialiser la variable globale dbh
            init_database()
            logger.info("✅ Base de données réinitialisée")
        except Exception as e:
            logger.error(f"Erreur lors de la réinitialisation de la base de données: {e}")
            raise_error(
                "⚠️ Import réussi mais erreur de réinitialisation",
                f"Le fichier a été importé avec succès, mais une erreur s'est produite lors de la réinitialisation.\n\n"
                f"Erreur: {str(e)}\n\n"
                f"Veuillez redémarrer l'application."
            )
            return
        
        # Récupérer la version de la base de données importée
        try:
            version_info = Version.get(id=1).display_name()
        except Exception as e:
            logger.warning(f"Impossible de récupérer la version: {e}")
            version_info = "Version inconnue"
        
        # Message de succès
        success_message = f"✅ Les données ont été correctement importées.\n\n"
        success_message += f"📊 Informations:\n"
        success_message += f"• Version: {version_info}\n"
        if db_info['organization']:
            success_message += f"• Organisation: {db_info['organization']}\n"
        if backup_file_path:
            success_message += f"• Sauvegarde créée: {os.path.basename(backup_file_path)}\n"
        success_message += f"\n💡 Vous pouvez maintenant utiliser l'application avec les nouvelles données."
        
        raise_success(
            "✅ Importation réussie",
            success_message
        )
        
        logger.info("✅ Import de la base de données terminé avec succès")

    except IOError as e:
        logger.error(f"Erreur IO lors de l'import: {e}")
        raise_error(
            "❌ Erreur de fichier",
            f"Une erreur s'est produite lors de l'accès aux fichiers.\n\n"
            f"Erreur: {str(e)}\n\n"
            f"Vérifiez que:\n"
            f"• Le fichier sélectionné est accessible\n"
            f"• Vous avez les droits de lecture/écriture\n"
            f"• Le fichier n'est pas corrompu"
        )
    except Exception as e:
        logger.error(f"Erreur inattendue lors de l'import: {e}", exc_info=True)
        raise_error(
            "❌ Erreur lors de l'import",
            f"Une erreur inattendue s'est produite.\n\n"
            f"Erreur: {str(e)}\n\n"
            f"Veuillez contacter le support si le problème persiste."
        )


def upload_file(folder=None, dst_folder=None, type_f=None):
    path_db_file = os.path.join(folder, DB_FILE)
    name_select_f = QFileDialog.getOpenFileName(
        QWidget(),
        "Open Data File",
        "./",
        "Image Files (*.png *.jpg *.bmp)",
    )
    shutil.copy(name_select_f, path_db_file)

    raise_success(
        "Importation.", "Import du fichier '{}' terminé.".format(name_select_f)
    )


def copyanything(src, dest):
    try:
        shutil.copytree(src, dest, ignore=None)
    except OSError as e:
        # If the error was caused because the source wasn't a directory
        if e.errno == errno.ENOTDIR:
            shutil.copy(src, dest)
        else:
            print("Directory not copied. Error: %s" % e)


def export_license_as_file():
    """Exporte le fichier de licence en l'ouvrant dans le système de fichiers"""
    fil = get_lcse_file()
    if not os.path.exists(fil):
        raise IOError(f"Le fichier de licence n'existe pas : {fil}\nVeuillez d'abord activer une licence.")
    uopen_file(fil)


def get_usb_drives():
    """
    Détecte les périphériques USB/amovibles disponibles sur le système.
    
    Returns:
        list: Liste des chemins de périphériques amovibles détectés
    """
    from .cstatic import logger
    
    usb_drives = []
    try:
        partitions = psutil.disk_partitions(all=True)
        
        for partition in partitions:
            try:
                # Vérifier si c'est un périphérique amovible
                # Sur Windows: 'removable' dans opts
                # Sur Linux/Mac: vérifier si c'est un périphérique externe
                is_removable = False
                
                if platform.system() == "Windows":
                    # Sur Windows, vérifier 'removable' dans opts
                    if 'removable' in partition.opts.lower():
                        is_removable = True
                else:
                    # Sur Linux/Mac, utiliser une heuristique basée sur le type de fichiersystem
                    # et le point de montage pour détecter les périphériques amovibles
                    removable_types = ['vfat', 'fat32', 'exfat', 'ntfs', 'msdos', 'hfs', 'hfsplus', 'apfs']
                    mount_point_lower = partition.mountpoint.lower()
                    
                    # Types de fichiersystems typiques des USB
                    if partition.fstype.lower() in removable_types:
                        system_mounts = ['/boot', '/home', '/usr', '/var', '/opt', '/tmp', '/sys', '/proc', '/dev']
                        
                        if platform.system() == "Darwin":  # macOS
                            # Sur macOS, les volumes externes sont généralement dans /Volumes/
                            # Exclure le disque système (généralement "Macintosh HD" ou "MacOS")
                            if '/volumes/' in mount_point_lower:
                                # Exclure les volumes système connus
                                system_volume_names = ['macintosh hd', 'macos', 'system', 'recovery']
                                volume_name = os.path.basename(partition.mountpoint).lower()
                                if not any(name in volume_name for name in system_volume_names):
                                    is_removable = True
                        else:  # Linux
                            # Exclure les montages système, accepter le reste
                            if not any(mount_point_lower == mount or mount_point_lower.startswith(mount + '/') for mount in system_mounts):
                                # Exclure le root filesystem
                                if mount_point_lower != '/' and mount_point_lower != '/media' and mount_point_lower != '/mnt':
                                    # Vérifier si c'est un sous-répertoire de /media ou /mnt (emplacements typiques)
                                    if '/media/' in mount_point_lower or '/mnt/' in mount_point_lower:
                                        is_removable = True
                                    # Ou si c'est un montage qui n'est pas système
                                    elif not mount_point_lower.startswith('/run/'):
                                        is_removable = True
                
                if is_removable:
                    # Vérifier que le périphérique est accessible en écriture
                    mount_point = partition.mountpoint
                    if os.path.exists(mount_point) and os.access(mount_point, os.W_OK):
                        # Essayer d'obtenir des informations sur l'espace disponible
                        try:
                            usage = psutil.disk_usage(mount_point)
                            # Vérifier qu'il y a au moins 10 MB d'espace libre
                            if usage.free > 10 * 1024 * 1024:  # 10 MB
                                usb_drives.append(mount_point)
                                logger.debug(f"Périphérique USB détecté: {mount_point}")
                        except (PermissionError, OSError):
                            logger.debug(f"Périphérique non accessible: {mount_point}")
                            pass
                            
            except (PermissionError, OSError) as e:
                # Ignorer les périphériques non accessibles
                logger.debug(f"Erreur lors de la vérification du périphérique {partition.device}: {e}")
                continue
                
    except Exception as e:
        logger.error(f"Erreur lors de la détection des périphériques USB: {e}")
    
    return usb_drives


def select_usb_drive(parent=None):
    """
    Affiche une boîte de dialogue pour sélectionner une clé USB parmi celles détectées.
    
    Args:
        parent: Widget parent pour la boîte de dialogue
        
    Returns:
        str: Chemin de la clé USB sélectionnée, ou None si aucune sélection
    """
    from .cstatic import logger
    
    usb_drives = get_usb_drives()
    
    if not usb_drives:
        # Aucune clé USB détectée automatiquement, proposer une sélection manuelle
        msg = QMessageBox(parent)
        msg.setIcon(QMessageBox.Icon.Warning)
        msg.setWindowTitle("🔌 Clé USB requise")
        msg.setText("Aucune clé USB détectée automatiquement")
        msg.setInformativeText(
            "La sauvegarde de la base de données nécessite une clé USB branchée.\n\n"
            "Veuillez sélectionner manuellement votre clé USB."
        )
        msg.setStandardButtons(QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Retry | QMessageBox.StandardButton.Cancel)
        msg.button(QMessageBox.StandardButton.Ok).setText("Sélectionner manuellement")
        msg.button(QMessageBox.StandardButton.Retry).setText("Réessayer")
        msg.button(QMessageBox.StandardButton.Cancel).setText("Annuler")
        
        result = msg.exec()
        if result == QMessageBox.StandardButton.Retry:
            # Réessayer la détection
            return select_usb_drive(parent)
        elif result == QMessageBox.StandardButton.Cancel:
            return None
        else:
            # Sélection manuelle
            selected_dir = QFileDialog.getExistingDirectory(
                parent,
                "🔌 Sélectionner votre clé USB pour la sauvegarde",
                "",
                QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks
            )
            
            if not selected_dir:
                return None
            
            # Vérifier que le répertoire sélectionné est accessible en écriture
            if os.path.exists(selected_dir) and os.access(selected_dir, os.W_OK):
                try:
                    usage = psutil.disk_usage(selected_dir)
                    if usage.free > 10 * 1024 * 1024:  # 10 MB minimum
                        logger.info(f"Clé USB sélectionnée manuellement: {selected_dir}")
                        return selected_dir
                    else:
                        raise_error(
                            "Espace insuffisant",
                            "La clé USB sélectionnée n'a pas assez d'espace libre (minimum 10 MB requis)."
                        )
                        return None
                except Exception as e:
                    logger.warning(f"Impossible de vérifier l'espace disponible: {e}")
                    # Accepter quand même si on ne peut pas vérifier
                    return selected_dir
            else:
                raise_error(
                    "Accès refusé",
                    "Vous n'avez pas les droits d'écriture sur le répertoire sélectionné."
                )
                return None
    
    elif len(usb_drives) == 1:
        # Une seule clé USB détectée, l'utiliser directement
        selected_drive = usb_drives[0]
        logger.info(f"Une seule clé USB détectée, utilisation de: {selected_drive}")
        return selected_drive
    
    else:
        # Plusieurs clés USB détectées, proposer de choisir
        # Utiliser QFileDialog pour permettre à l'utilisateur de choisir
        msg = QMessageBox(parent)
        msg.setIcon(QMessageBox.Question)
        msg.setWindowTitle("🔌 Sélectionner une clé USB")
        msg.setText(f"{len(usb_drives)} clés USB détectées")
        msg.setInformativeText(
            "Plusieurs clés USB ont été détectées.\n"
            "Veuillez sélectionner celle sur laquelle vous souhaitez sauvegarder."
        )
        msg.setStandardButtons(QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel)
        msg.button(QMessageBox.StandardButton.Ok).setText("Sélectionner")
        msg.button(QMessageBox.StandardButton.Cancel).setText("Annuler")
        
        result = msg.exec()
        if result != QMessageBox.StandardButton.Ok:
            return None
        
        # Ouvrir un sélecteur de répertoire sur la première clé USB
        # L'utilisateur pourra naviguer vers une autre clé si nécessaire
        selected_dir = QFileDialog.getExistingDirectory(
            parent,
            "🔌 Sélectionner une clé USB pour la sauvegarde",
            usb_drives[0],
            QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks
        )
        
        if not selected_dir:
            return None
        
        # Vérifier que le répertoire sélectionné est bien dans une clé USB détectée
        # ou que c'est un répertoire accessible en écriture
        if os.path.exists(selected_dir) and os.access(selected_dir, os.W_OK):
            try:
                usage = psutil.disk_usage(selected_dir)
                if usage.free > 10 * 1024 * 1024:  # 10 MB minimum
                    logger.info(f"Clé USB sélectionnée: {selected_dir}")
                    return selected_dir
            except Exception as e:
                logger.warning(f"Impossible de vérifier l'espace disponible sur {selected_dir}: {e}")
        
        raise_error(
            "Clé USB invalide",
            "Le répertoire sélectionné n'est pas valide ou n'a pas assez d'espace libre."
        )
        return None


def save_database_on_exit(max_backups=10, parent=None):
    """
    Sauvegarde automatique de la base de données à la fermeture de l'application.
    Nécessite une clé USB branchée.
    
    Args:
        max_backups (int): Nombre maximum de sauvegardes à conserver (par défaut: 10)
        parent: Widget parent pour les boîtes de dialogue (optionnel)
    
    Returns:
        bool: True si la sauvegarde a réussi, False sinon
    """
    from .cstatic import logger
    
    try:
        # Sélectionner une clé USB (détection automatique + sélection si nécessaire)
        usb_drive = select_usb_drive(parent)
        if not usb_drive:
            logger.warning("Aucune clé USB sélectionnée, sauvegarde annulée")
            return False
        
        # Obtenir le chemin absolu du fichier de base de données
        db_file_abs = os.path.abspath(DB_FILE)
        
        # Vérifier que le fichier de base de données existe
        if not os.path.exists(db_file_abs):
            logger.warning(f"Le fichier de base de données n'existe pas: {db_file_abs}")
            return False
        
        # Créer le répertoire de sauvegarde sur la clé USB
        backup_dir = os.path.join(usb_drive, "backups")
        
        # Créer le répertoire s'il n'existe pas
        try:
            os.makedirs(backup_dir, exist_ok=True)
        except OSError as e:
            logger.error(f"Impossible de créer le répertoire de sauvegarde sur la clé USB: {e}")
            raise_error(
                "Erreur de sauvegarde",
                f"Impossible de créer le répertoire de sauvegarde sur la clé USB:\n{usb_drive}\n\n"
                f"Vérifiez que la clé USB n'est pas protégée en écriture."
            )
            return False
        
        # Générer le nom du fichier de sauvegarde avec la date et l'heure
        backup_filename = f"backup_{datetime.now().strftime('%Y-%m-%d_%Hh%Mm%Ss')}.db"
        backup_path = os.path.join(backup_dir, backup_filename)
        
        # Copier la base de données sur la clé USB
        try:
            shutil.copy2(db_file_abs, backup_path)
            logger.info(f"✅ Sauvegarde de la base de données créée sur la clé USB: {backup_path}")
        except (IOError, OSError) as e:
            logger.error(f"Erreur lors de la copie vers la clé USB: {e}")
            raise_error(
                "Erreur de sauvegarde",
                f"Impossible de sauvegarder sur la clé USB:\n{usb_drive}\n\n"
                f"Vérifiez que:\n"
                f"• La clé USB n'est pas protégée en écriture\n"
                f"• Il y a suffisamment d'espace disponible\n"
                f"• La clé USB n'a pas été retirée"
            )
            return False
        
        # Nettoyer les anciennes sauvegardes (garder seulement les max_backups plus récentes)
        try:
            backup_files = [
                os.path.join(backup_dir, f)
                for f in os.listdir(backup_dir)
                if f.startswith("backup_") and f.endswith(".db")
            ]
            
            # Trier par date de modification (plus récent en premier)
            backup_files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
            
            # Supprimer les sauvegardes en trop
            if len(backup_files) > max_backups:
                for old_backup in backup_files[max_backups:]:
                    try:
                        os.remove(old_backup)
                        logger.debug(f"Ancienne sauvegarde supprimée: {os.path.basename(old_backup)}")
                    except Exception as e:
                        logger.warning(f"Impossible de supprimer l'ancienne sauvegarde {old_backup}: {e}")
        except Exception as e:
            logger.warning(f"Erreur lors du nettoyage des anciennes sauvegardes: {e}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Erreur lors de la sauvegarde automatique de la base de données: {e}")
        return False
