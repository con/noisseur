import logging
import logging.config
import os
import io
import re
import time
import datetime
import platform
import pytesseract
import pyvips
from dataclasses import dataclass, field
from dataclasses_json import dataclass_json
from PIL import Image, ImageDraw, ImageFont
from lxml import etree
from lxml.etree import QName
from easyocr import Reader

from noisseur.cfg import AppConfig
from noisseur.imgproc import ImageProcessor
from noisseur.hocr import HocrParser
from noisseur.model import ModelFactory, ModelService, ModelMatch, Model

logger = logging.getLogger(__name__)


@dataclass_json
@dataclass
class OcrScreenData:
    host: str = "localhost"
    ts: str = None
    dt_ms: int = 0
    success: bool = False
    errors: list[str] = None
    type: str = None
    data: dict = None
    items: dict = None

    def add_error(self, s: str):
        if not self.errors:
            self.errors = []
        self.errors.append(s)


class OcrService:
    WORD_CONFIDENCE_THRESHOLD: float = 40.0
    AVG_CONFIDENCE_THRESHOLD: float = 97.0

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

        rgb_image = Image.new("RGB", image.size)
        rgb_image.paste(image)
        image = rgb_image

        draw = ImageDraw.Draw(image)
        font = None
        try:
            font = ImageFont.truetype(AppConfig.instance.HOCR_VISUALIZE_FONT,
                                      size=AppConfig.instance.HOCR_VISUALIZE_FONT_SIZE)
        except IOError as ex:
            logger.error(f"Failed load font, use default one: {str(ex)}", ex)
            font = ImageFont.load_default()

        for w in doc.words:
            rc = [w.bbox.left, w.bbox.top, w.bbox.right, w.bbox.bottom]
            w_conf: float = w.x_wconf
            avg_conf: float = w.calc_avg_x_conf()
            color: str = "red"
            if w_conf > OcrService.WORD_CONFIDENCE_THRESHOLD and avg_conf > OcrService.AVG_CONFIDENCE_THRESHOLD:
                color = "green"
            draw.rectangle(rc, outline=color)
            txt = w.text
            # txt = re.sub(r"[^a-zA-Z0-9]", " ", w.text)
            # draw.fontmode = "1"
            draw.text((w.bbox.left, w.bbox.top - 21), txt, font=font, fill="blue", align="center")
            draw.text((w.bbox.right - 30, w.bbox.top - 14), f"w{int(w_conf)}/a{int(avg_conf)}",
                      font=ImageFont.load_default(),
                      fill=color, align="center")

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
        logger.debug("-> " + res)
        return res

    def ocr_hocr(self, path, chain) -> HocrParser.Document:
        logger.debug(f'ocr_hocr(path={path})')

        if chain:
            img = self.imgProc.chain(path, chain)
            path = Image.open(io.BytesIO(img))

        cfg = AppConfig.instance.TESSERACT_HOCR_CONFIG

        logger.debug(f"cfg={cfg}")
        res = pytesseract.image_to_pdf_or_hocr(path, config=cfg, extension='hocr')
        res = res.decode('utf-8')

        hp = HocrParser()
        doc = hp.parse(res)
        return doc

    def ocr_caption(self, path) -> ModelMatch:
        logger.debug(f'ocr_caption(path={path})')
        caption = self.imgProc.caption_ex(path)
        if not caption:
            logger.debug("caption not found")
            return None

        doc: HocrParser.Document = self.ocr_hocr(Image.open(io.BytesIO(caption["data"])), None)
        if not doc:
            logger.debug("hocr not found")
            return None

        svc: ModelService = ModelFactory.get_service()
        match: ModelMatch = svc.find_by_hocr(doc)
        if not match:
            logger.debug("model not found by hocr")
            return None

        match.offset_x = int(match.offset_x + caption["rc"][0])  # add crop.rc.top coordinate
        match.offset_y = int(match.offset_y + caption["rc"][1])  # add crop.rc.top coordinate
        return match

    def ocr_screen(self, path, chain, scale: float, border: int) -> OcrScreenData:
        logger.debug(f'ocr_screen(path={path})')
        osd: OcrScreenData = OcrScreenData()
        osd.success = False
        osd.host = platform.node()
        osd.ts = str(datetime.datetime.now())
        dt = time.time()
        doc: HocrParser.Document = self.ocr_hocr(path, chain)
        if not doc:
            logger.debug("hocr not found")
            osd.add_error("HOCR not found")
            return osd

        match: ModelMatch = self.ocr_caption(path)
        svc: ModelService = ModelFactory.get_service()

        if match:
            logger.debug("model found by caption")
            match.offset_x = int(match.offset_x * scale)
            match.offset_y = int(match.offset_y * scale)
            match.scale_x = scale
            match.scale_y = scale
        else:
            logger.debug("model not found by caption, try search by hocr")
            match: ModelMatch = svc.find_by_hocr(doc, scale)

        if border and match:
            match.offset_x = match.offset_x + border
            match.offset_y = match.offset_y + border

        if not match:
            logger.debug("model not found by hocr")
            osd.add_error("Model not found by HOCR")
            return osd

        dad: dict = svc.get_data_as_dict(doc, match)

        osd.type = dad["type"]
        osd.items = dad["items"]
        osd.data = dad["data"]
        osd.dt_ms = int((time.time() - dt) * 1000)
        if osd.type:
            osd.success = True
        return osd

    def tesseract_version(self):
        return "tesseract {}".format(pytesseract.get_tesseract_version())


class EasyOcrService(OcrService):
    def __init__(self):
        super().__init__()
        logger.debug("EasyOcrService()")
        self._reader = Reader(['en'], gpu=True)

    def ocr_hocr(self, path, chain) -> HocrParser.Document:
        logger.debug(f'ocr_hocr(path={path})')
        if chain:
            img = self.imgProc.chain(path, chain)
        else:
            if isinstance(path, str):
                img = self.imgProc.to_buffer(self.imgProc.pil_load(path))
            else:
                img = self.imgProc.to_buffer(path)

        path = Image.open(io.BytesIO(img))

        logger.debug("invoke easyocr")
        res = self._reader.readtext(img, detail=1)

        logger.debug(f"done easyocr: {str(res)}")
        width, height = path.size
        hocr = self._to_hocr(res, width, height)

        hp = HocrParser()
        doc = hp.parse(hocr)
        return doc

    def _to_hocr(self, res, img_width: int, img_height: int) -> str:
        root = etree.Element('html', xmlns="http://www.w3.org/1999/xhtml", lang="en")
        root.set(QName("http://www.w3.org/XML/1998/namespace", "lang"), 'en')

        head = etree.SubElement(root, 'head')

        title = etree.SubElement(head, 'title')
        title.text = ''

        etree.SubElement(head, 'meta', http_equiv="Content-Type", content="text/html;charset=utf-8")
        etree.SubElement(head, 'meta', name="ocr-system", content="easyocr")
        etree.SubElement(head, 'meta', name="ocr-capabilities",
                         content="ocr_page ocr_carea ocr_par ocr_line ocrx_word ocrp_wconf")

        body = etree.SubElement(root, 'body')

        div_page_1 = etree.SubElement(body, 'div')
        div_page_1.set('class', 'ocr_page')
        div_page_1.set('id', 'page_1')
        div_page_1.set('title', f'image "input.PNG"; bbox 0 0 {img_width} {img_height}; ppageno 0')

        div_block_1_1 = etree.SubElement(div_page_1, 'div')
        div_block_1_1.set('class', 'ocr_carea')
        div_block_1_1.set('id', 'block_1_1')
        div_block_1_1.set('title', f'bbox 0 0 {img_width} {img_height}')

        p_par_1_1 = etree.SubElement(div_block_1_1, 'p')
        p_par_1_1.set('class', 'ocr_par')
        p_par_1_1.set('id', 'par_1_1')
        p_par_1_1.set('lang', 'prisma')
        p_par_1_1.set('title', f'bbox 0 0 {img_width} {img_height}')

        for i, (bbox, text, conf) in enumerate(res):
            lt, rt, rb, lb = bbox
            x = lt[0]
            y = lt[1]
            w = rb[0] - x
            h = rb[1] - y
            #
            span_line_1 = etree.SubElement(p_par_1_1, 'span')
            span_line_1.set('class', 'ocr_line')
            span_line_1.set('id', f'line_1_{(i+1)}')
            span_line_1.set('title', f'bbox {x} {y} {x+w} {y+h};')
            # title='bbox 51 45 3108 99; baseline 0 -9; x_size 54; x_descenders 9; x_ascenders 18'

            span_word_1 = etree.SubElement(span_line_1, 'span')
            span_word_1.set('class', 'ocrx_word')
            span_word_1.set('id', f'word_1_{(i+1)}')
            span_word_1.set('title', f'bbox {x} {y} {x+w} {y+h}; x_wconf {conf}')
            span_word_1.text = text


        tree = etree.ElementTree(root)
        s = etree.tostring(tree,
                           doctype='<!DOCTYPE html PUBLIC '
                                   '"-//W3C//DTD XHTML 1.0 Transitional//EN" '
                                   '"http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">',
                           encoding='utf-8',
                           xml_declaration=True,
                           pretty_print=True,
                           ).decode("utf-8")
        return s


class TesseractOcrService(OcrService):
    def __init__(self):
        super().__init__()
        logger.debug("TesseractOcrService()")


class OcrFactory:
    __ocr_service = None

    @staticmethod
    def init() -> None:
        if AppConfig.instance.OCR == "tesseract":
            svc = TesseractOcrService()
        elif AppConfig.instance.OCR == "easyocr":
            svc = EasyOcrService()
        else:
            raise Exception(f"Unknown ocr: {AppConfig.instance.OCR}")
        OcrFactory.__ocr_service = svc

    @staticmethod
    def get_service() -> OcrService:
        if not OcrFactory.__ocr_service:
            OcrFactory.init()
        return OcrFactory.__ocr_service

# OcrFactory.init()
