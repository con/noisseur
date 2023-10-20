import configparser
import logging
import platform
from pathlib import Path
import os.path
import os
import sys
import time

logger = logging.getLogger(__name__)

class BaseConfig:
    def __init__(self, owner, section):
        self.owner = owner
        self.section = section

    def get(self, name):
        return self.owner._getStr(self.section, name)




# Main application configuration
class AppConfig:
    instance = None

    #
    SECTION_SYSTEM           = "system"
    SECTION_NOISSEUR         = "noisseur"
    #
    SECTION_FLASK            = "flask"
    #

    # AppConfig members

    def __init__(self):
        self._config = None
        self._initialized = False
        self._rootPath = str(Path(__file__).parent.parent)
        self._hostConfigPath = "/etc/con/noisseur"
        self.START_TIME = time.time()
        self.CONFIG_PATH = None

    def _getCfg(self, section, constructor):
        key = f'{section}'
        if not (key in self._cache):
            self._cache[key] = constructor(self, section)
        return self._cache[key]

    def _getDict(self, section):
        key = f'dict|{section}'
        d = None
        if not (key in self._cache):
            d = dict(self._config.items(section, raw=True))

            for key2 in d:
                val = str(d.get(key2))
                if val.startswith('@|'):
                    val = eval(val[2:])
                    d[key2] = val

            self._cache[key] = d
        else:
            d = self._cache[key]
        return d

    def _getEnv(self, key, defVal=None):
        return os.getenv(key, defVal)

    def _getListStr(self, section, name) -> list:
        key = f'{section}|{name}'
        if not (key in self._cache):
            s = str(self._config.get(section, name))
            lst = list(filter(None, [opt.strip() for opt in s.splitlines()]))
            self._cache[key] = lst
        return self._cache[key]

    def _getPath(self, section, name) -> str:
        key = f'{section}|{name}'
        if not (key in self._cache):
            self._cache[key] = os.path.expanduser(self._config.get(section, name))
        return self._cache[key]

    def _getStr(self, section, name) -> str:
        key = f'{section}|{name}'
        if not (key in self._cache):
            self._cache[key] = self._config.get(section, name)
        return self._cache[key]

    def _getInt(self, section, name) -> int:
        key = f'{section}|{name}'
        if not (key in self._cache):
            self._cache[key] = int(self._config.get(section, name))
        return self._cache[key]

    #def dump(self):
    #    logger.debug("AppConfig dump")

    def initialized(self):
        return self._initialized

    def load(self, paths, files):
        self._config = configparser.RawConfigParser()
        self._initialized = True
        # fix lowercase/case insensitive issue
        self._config.optionxform = str
        self._cache = {};
        logger.info("Reading configuration from local file: "+str(paths))
        res = None
        try:
            res = self._config.read(paths)
        except:
            logger.error("Failed read configuration", exc_info=True)
            raise

        if files != None and len(files) > 0:
            for file in files:
                logger.info("Reading configuration from url: " + str(file))
                self._config.read_file(file)
                res.append(str(file))

        self.CONFIG_PATHS = res
        logger.info("Found config files: " + str(res))

    @property
    def ROOT_PATH(self):
        return self._rootPath

    @property
    def HOCR_VISUALIZE_FONT(self):
        return self._getStr(self.SECTION_NOISSEUR, "HOCR_VISUALIZE_FONT")

    @property
    def HOCR_VISUALIZE_FONT_SIZE(self):
        return self._getInt(self.SECTION_NOISSEUR, "HOCR_VISUALIZE_FONT_SIZE")

    @property
    def HOST_CONFIG_PATH(self):
        return self._hostConfigPath

    @property
    def ENV(self):
        return self._getStr(self.SECTION_SYSTEM, "ENV")

    @property
    def MODEL_LIST(self):
        return self._getListStr(self.SECTION_NOISSEUR, "MODEL_LIST")

    @property
    def TESSERACT_HOCR_CONFIG(self):
        return self._getStr(self.SECTION_NOISSEUR, "TESSERACT_HOCR_CONFIG")

    @property
    def noisseur(self) -> dict:
        return self._getDict(self.SECTION_NOISSEUR)

    @property
    def flask(self) -> dict:
        return self._getDict(self.SECTION_FLASK)


def app_init():

    if AppConfig.instance and AppConfig.instance.initialized():
        logger.info("Application already initialized")
        return

    if not AppConfig.instance:
        AppConfig.instance = AppConfig()

    cfg = AppConfig.instance

    logging_ini = 'logging.ini'
    log_files = [
        cfg.HOST_CONFIG_PATH + '/' + logging_ini,
        cfg.ROOT_PATH + '/' + logging_ini
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
        cfg.ROOT_PATH + '/' + noisseur_ini,
        cfg.HOST_CONFIG_PATH + '/' + noisseur_ini
    ]

    ini_files = None

    cfg.load(ini_paths, ini_files)

    logger.info('Environment: '+cfg.ENV)
    logger.info("Application initialized successfully")
