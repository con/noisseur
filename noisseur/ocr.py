import logging
import logging.config
import os
import io
import pytesseract
import pyvips
from PIL import Image
from noisseur.core import app_config
from noisseur.imgproc import ImageProcessor
from noisseur.hocr import HocrParser

logger = logging.getLogger(__name__)

class TesseractOcr:

    def __init__(self):
        self.imgProc = ImageProcessor()

    def ocr_text(self, path, chain) -> str:
        logger.debug(f'ocr_plain(path={path})')

        if chain:
            img = self.imgProc.chain(path, chain)
            path = Image.open(io.BytesIO(img))

        res = pytesseract.image_to_string(path)
        logger.debug("-> "+res)
        return res

    def ocr_hocr(self, path, chain) -> HocrParser.Document:
        logger.debug(f'ocr_hocr(path={path})')

        if chain:
            img = self.imgProc.chain(path, chain)
            path = Image.open(io.BytesIO(img))

        """
        tessdataPath = os.path.join(app_config.ROOT_PATH, "tessdata")
        # --psm 8 --oem 1 -c lstm_choice_mode=0 -c tessedit_pageseg_mode=6
        cfg = f" --tessdata-dir {tessdataPath}" \
              " -l eng " \
              " --psm 3 " \
              " --oem 1 " \
              " -c hocr_char_boxes=1" \
              " -c lstm_choice_mode=0" \
              " -c tessedit_pageseg_mode=3" \
              " hocr"
        """
        cfg = f" -c hocr_char_boxes=1" \
              " hocr"

        logger.debug(f"cfg={cfg}")
        res = pytesseract.image_to_pdf_or_hocr(path, config=cfg, extension='hocr')
        res = res.decode('utf-8')

        hp = HocrParser()
        doc = hp.parse(res)
        return doc

    def tesseract_version(self):
        return "tesseract {}".format(pytesseract.get_tesseract_version())


