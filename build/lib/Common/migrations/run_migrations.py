#!/usr/bin/env python
# -*- coding: utf-8 -*-
# maintainer: Fad

import os
import sys
import importlib.util
from pathlib import Path

# Ajouter le répertoire parent au chemin Python
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from Common.cstatic import logger
from Common.models import dbh
from Common.migrations.migration_tracker import MigrationTracker

def run_migrations():
    """Exécute toutes les migrations dans l'ordre"""
    try:
        # Vérifier la connexion à la base de données
        if dbh is None or dbh.is_closed():
            logger.error("❌ La base de données n'est pas connectée")
            return False
            
        # Exécuter d'abord la migration du MigrationTracker
        logger.info("🔄 Exécution de la migration du système de suivi")
        if not MigrationTracker.migrate():
            logger.error("❌ Échec de la migration du système de suivi")
            return False
        logger.info("✅ Migration du système de suivi terminée avec succès")
        
        # Obtenir le répertoire des migrations
        migrations_dir = Path(__file__).parent
        
        # Trouver tous les fichiers de migration
        migration_files = sorted([
            f for f in migrations_dir.glob("migration_*.py")
            if f.name not in ["__init__.py", "run_migrations.py", "migration_tracker.py"]
        ])
        
        if not migration_files:
            logger.info("✅ Aucune migration à exécuter")
            return True
            
        logger.info(f"🔍 {len(migration_files)} migration(s) trouvée(s)")
        
        # Récupérer les migrations en attente
        pending_migrations = MigrationTracker.get_pending_migrations([f.stem for f in migration_files])
        
        if not pending_migrations:
            logger.info("✅ Toutes les migrations sont à jour")
            return True
            
        logger.info(f"🔄 {len(pending_migrations)} migration(s) en attente")
        
        # Exécuter chaque migration en attente
        for migration_file in migration_files:
            if migration_file.stem not in pending_migrations:
                continue
                
            try:
                # Importer le module de migration
                spec = importlib.util.spec_from_file_location(
                    migration_file.stem, 
                    migration_file
                )
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                
                # Exécuter la migration
                logger.info(f"🔄 Exécution de la migration: {migration_file.name}")
                try:
                    if module.migrate():
                        MigrationTracker.mark_migration_applied(migration_file.stem)
                        logger.info(f"✅ Migration {migration_file.name} terminée avec succès")
                    else:
                        MigrationTracker.mark_migration_applied(
                            migration_file.stem,
                            status='failed',
                            error_message="La migration a échoué"
                        )
                        logger.error(f"❌ Échec de la migration {migration_file.name}")
                        return False
                except Exception as e:
                    MigrationTracker.mark_migration_applied(
                        migration_file.stem,
                        status='failed',
                        error_message=str(e)
                    )
                    logger.error(f"❌ Erreur lors de l'exécution de -- {migration_file.name}: {e}")
                    return False
                    
            except Exception as e:
                logger.error(f"❌ Erreur lors du chargement de {migration_file.name}: {e}")
                return False
                
        logger.info("🎉 Toutes les migrations ont été exécutées avec succès")
        return True
        
    except Exception as e:
        logger.error(f"❌ Erreur lors de l'exécution des migrations: {e}")
        return False

if __name__ == "__main__":
    run_migrations() 