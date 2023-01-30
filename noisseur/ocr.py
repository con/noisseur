import logging
import logging.config
import os
import io
import re
import pytesseract
import pyvips
from PIL import Image, ImageDraw, ImageFont
from noisseur.core import app_config
from noisseur.imgproc import ImageProcessor
from noisseur.hocr import HocrParser
from noisseur.model import ModelFactory, ModelService, ModelMatch, Model

logger = logging.getLogger(__name__)

class TesseractOcr:

    def __init__(self):
        self.imgProc = ImageProcessor()

    def hocr_visualize_as_png(self, path, chain: str, doc: HocrParser.Document) -> bytes:
        logger.debug("hocr_visualize_as_png(..., path={}, chain={})".format(path, chain))
        image: Image = None
        if chain:
            image = self.imgProc.chain(path, chain)
        else:
            image = self.imgProc.to_buffer(self.imgProc.vips_load(path))

        image = Image.open(io.BytesIO(image))

        draw = ImageDraw.Draw(image)
        font = ImageFont.truetype("Arial", 16)
        for w in doc.words:
            rc = [w.bbox.left, w.bbox.top, w.bbox.right, w.bbox.bottom]
            draw.rectangle(rc, outline="red")
            txt = re.sub(r"[^a-zA-Z0-9]", " ", w.text)
            draw.text((w.bbox.left, w.bbox.top), txt, font=font, fill="blue", align="center")

        b = io.BytesIO()
        image.save(b, format="PNG")
        b.seek(0)
        data = b.read()
        return data

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

    def ocr_screen(self, path, chain, scale: float):
        logger.debug(f'ocr_screen(path={path})')
        doc: HocrParser.Document = self.ocr_hocr(path, chain)
        if not doc:
            logger.debug("hocr not found")
            return None

        svc: ModelService = ModelFactory.get_service()
        match: ModelMatch = svc.find_by_hocr(doc, scale)
        if not match:
            logger.debug("model not found by hocr")
            return None

        return svc.get_data_as_dict(doc, match)


    def tesseract_version(self):
        return "tesseract {}".format(pytesseract.get_tesseract_version())




