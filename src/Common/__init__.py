from .cstatic import logger

try:
    # Import des modules disponibles
    from .models import init_database
    from .updater import UpdaterInit

    logger.info("Initialisation de l'application")
    
    # Initialisation de la base de données
    if init_database():
        logger.info("Base de données initialisée avec succès")
    else:
        logger.warning("Impossible d'initialiser la base de données")
    
    # L'updater sera initialisé manuellement par les fenêtres qui en ont besoin
    # pour éviter les problèmes de threads non fermés
    logger.info("Modules Common chargés avec succès")
    
except ImportError as e:
    logger.error(f"Erreur lors de l'importation des modules: {e}")
except Exception as e:
    logger.error(f"Erreur lors de l'initialisation: {e}")
