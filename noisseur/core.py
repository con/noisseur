import logging
import logging.config
import sys
import platform
from pathlib import Path
from noisseur.config import AppConfig

logger = logging.getLogger(__name__)

app_config = AppConfig()


def app_init():

    if app_config.initialized():
        logger.info("Application already initialized")
        return

    logging_ini = 'logging.ini'
    log_files = [
        app_config.HOST_CONFIG_PATH + '/' + logging_ini,
        app_config.ROOT_PATH + '/' + logging_ini
    ]

    for logFile in log_files:
        if hasattr(logFile, 'readline') or Path(logFile).exists():
            logging.config.fileConfig(logFile, disable_existing_loggers=False)
            logger.info("Found logger configuration file: "+str(logFile))
            break

    logger.info("Application init...")
    logger.info('[Platform Info]: ')
    logger.info(' system    : ' + platform.system())
    logger.info(' node      : ' + platform.node())
    logger.info(' release   : ' + platform.release())
    logger.info(' version   : ' + platform.version())
    logger.info(' machine   : ' + platform.machine())
    logger.info(' processor : ' + platform.processor())
    logger.info(' python    : ' + '.'.join(map(str, sys.version_info)) + ', ' + sys.executable)

    # load configuration from multiple INI files and merge
    noisseur_ini = 'noisseur.ini'
    ini_paths = [
        app_config.ROOT_PATH + '/' + noisseur_ini,
        app_config.HOST_CONFIG_PATH + '/' + noisseur_ini
    ]

    ini_files = None

    app_config.load(ini_paths, ini_files)

    logger.info('Environment: '+app_config.ENV)
    logger.info("Application initialized successfully")
