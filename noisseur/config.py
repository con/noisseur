import configparser
import logging
from pathlib import Path
import os.path
import os
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
    def HOST_CONFIG_PATH(self):
        return self._hostConfigPath

    @property
    def ENV(self):
        return self._getStr(self.SECTION_SYSTEM, "ENV")

    @property
    def MODEL_LIST(self):
        return self._getListStr(self.SECTION_NOISSEUR, "MODEL_LIST")

    @property
    def noisseur(self) -> dict:
        return self._getDict(self.SECTION_NOISSEUR)

    @property
    def flask(self) -> dict:
        return self._getDict(self.SECTION_FLASK)

