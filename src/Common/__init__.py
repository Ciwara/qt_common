from .cstatic import logger
from database import Setup
try:
    from .updater import UpdaterInit

    logger.info("Initialisation de l'application")
    Setup().create_all_or_pass()
    UpdaterInit()
    logger.info("Initialisation terminée avec succès")
except ImportError as e:
    logger.error(f"Erreur lors de l'importation des modules: {e}")
except Exception as e:
    logger.error(f"Erreur lors de l'initialisation: {e}")
