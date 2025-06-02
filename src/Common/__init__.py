from .cstatic import logger

try:
    from .database import AdminDatabase as Setup
    from .cmain import cmain
    from .updater import UpdaterInit

    logger.info("Initialisation de l'application")
    Setup().create_all_or_pass()
    UpdaterInit()
    logger.info("Initialisation terminée avec succès")
except ImportError as e:
    logger.error(f"Erreur lors de l'importation des modules: {e}")
except Exception as e:
    logger.error(f"Erreur lors de l'initialisation: {e}")
