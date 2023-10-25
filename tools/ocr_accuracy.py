import sys
import logging.config


logger = logging.getLogger(__name__)
logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))
logger.setLevel(logging.DEBUG)
logger.debug(f"name={__name__}")


def main():
    logger.debug("ocr_accuracy tool")


if __name__ == "__main__":
    main()
