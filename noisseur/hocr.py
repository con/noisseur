import logging
import logging.config

import bs4
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


class HocrParser:

    class Document:
        def __init__(self, strip_word_whitespaces: bool = True):
            self.lines = []
            self.pages = []
            self.hocr = None  # str
            self.words = []
            self.strip_word_whitespaces = strip_word_whitespaces

        def add_page(self, page) -> None:
            self.pages.append(page)

        def add_line(self, line) -> None:
            self.lines.append(line)

        def add_word(self, word) -> None:
            self.words.append(word)

    class OcrNode:
        def __init__(self):
            self.id = None      # string
            self.bbox = None    # bbox
            self.title = None   # string
            self.mapTitle = {}  # string -> string[]

    class BaseLine:
        def __init__(self):
            self.slope = 0.0  # float
            self.shift = 0.0  # float

    class BBox:
        def __init__(self):
            self.left = 0    # int
            self.top = 0     # int
            self.right = 0   # int
            self.bottom = 0  # int

    class OcrPage(OcrNode):
        def __init__(self):
            self.image = None  # string
            self.ppageno = 0   # int
            self.areas = []    # ocr_carea[]

        def add_area(self, o):
            self.areas.append(o)

    class OcrCarea(OcrNode):
        def __init__(self):
            self.pars = []  # ocr_par[]

        def add_par(self, o):
            self.pars.append(o)

    class OcrPar(OcrNode):
        def __init__(self):
            self.lang = None  # string
            self.lines = []   # ocr_line[]

        def add_line(self, o):
            self.lines.append(o)

    class OcrLine(OcrNode):
        def __init__(self):
            self.baseline = None     # baseline
            self.lange = None        # string
            self.text = None         # string
            self.words = []          # ocrx_words[]
            self.glyphs = []         # ocrs_cinfo
            self.x_size = 0.0        # float
            self.x_descenders = 0.0  # float
            self.x_ascenders = 0.0   # float

        def add_glyph(self, o):
            self.glyphs.append(o)

        def add_word(self, o):
            self.words.append(o)

    class OcrHeader(OcrLine):
        pass

    class OcrCaption(OcrLine):
        pass

    class OcrxWord(OcrNode):
        def __init__(self):
            self.x_wconf = 0.0  # float
            self.text = None    # string
            self.glyphs = []    # ocrx_cinfo[]

        def add_glyph(self, o):
            self.glyphs.append(o)

        def calc_avg_x_conf(self):
            f: float = sum(glyph.x_conf for glyph in self.glyphs)
            if len(self.glyphs)>0:
                f = f / len(self.glyphs)
            return f

    class OcrxCinfo(OcrNode):
        def __init__(self):
            self.x_bboxes = None  # bbox
            self.x_conf = 0.0     # float
            self.char_ = None     # string

    def __int__(self):
        pass

    @staticmethod
    def first_char(s: str) -> str:
        if not s:
            return None

        if len(s) == 0:
            return None

        if len(s) > 1:
            logger.info("Multiple chars found, 1st is used: {}".format(s))

        return s[0]

    def parse(self, s: str, strip_word_whitespaces: bool = True) -> Document:
        logger.debug("parse(...)")
        doc = HocrParser.Document(strip_word_whitespaces=strip_word_whitespaces)
        doc.hocr = s
        d = BeautifulSoup(s, "html.parser")
        self.parse_page(doc, d)
        return doc

    def parse_baseline(self, o: OcrNode) -> BaseLine:
        name = "baseline"

        if not(name in o.mapTitle.keys()):
            return None

        a = o.mapTitle.get(name)
        if len(a) < 3:
            return None

        bl = HocrParser.BaseLine()
        bl.slope = float(a[1])
        bl.shift = float(a[2])
        return bl

    def parse_carea(self, doc: Document, owner: OcrPage, node: bs4.Tag) -> None:
        careas = node.find_all(class_="ocr_carea")
        for node2 in careas:
            o = HocrParser.OcrCarea()
            self.parse_node(o, node2)
            self.parse_par(doc, o, node2)
            owner.add_area(o)

    def parse_cinfo(self, doc: Document, line: OcrLine, owner: OcrxWord, node: bs4.Tag) -> None:
        pars = node.find_all(class_="ocrx_cinfo")
        for node2 in pars:
            o = HocrParser.OcrxCinfo()
            self.parse_node(o, node2)
            o.x_conf = self.parse_float_tag(o, "x_conf")
            o.char_ = self.first_char(node2.get_text())

            o.x_bboxes = HocrParser.BBox()
            if "x_bboxes" in o.mapTitle.keys():
                a = o.mapTitle["x_bboxes"]
                if len(a) >= 5:
                    o.x_bboxes.left = int(a[1])
                    o.x_bboxes.top = int(a[2])
                    o.x_bboxes.right = int(a[3])
                    o.x_bboxes.bottom = int(a[4])

            owner.add_glyph(o)
            line.add_glyph(o)

    def parse_caption(self, doc: Document, owner: OcrPar, node: bs4.Tag) -> None:
        pars = node.find_all(class_="ocr_caption")
        for node2 in pars:
            o = HocrParser.OcrCaption()
            self.parse_node(o, node2)
            o.baseline = self.parse_baseline(o)
            o.x_ascenders = self.parse_float_tag(o, "x_ascenders")
            o.x_descenders = self.parse_float_tag(o, "x_descenders")
            o.x_size = self.parse_float_tag(o, "x_size")
            o.lang = node2.get("lang")
            self.parse_word(doc, o, node2)

            lst = []
            for w in o.words:
                if len(w.text) > 0:
                    lst.append(w.text)

            o.text = " ".join(lst)

            owner.add_line(o)
            doc.add_line(o)

    def parse_header(self, doc: Document, owner: OcrPar, node: bs4.Tag) -> None:
        pars = node.find_all(class_="ocr_header")
        for node2 in pars:
            o = HocrParser.OcrHeader()
            self.parse_node(o, node2)
            o.baseline = self.parse_baseline(o)
            o.x_ascenders = self.parse_float_tag(o, "x_ascenders")
            o.x_descenders = self.parse_float_tag(o, "x_descenders")
            o.x_size = self.parse_float_tag(o, "x_size")
            o.lang = node2.get("lang")
            self.parse_word(doc, o, node2)

            lst = []
            for w in o.words:
                if len(w.text) > 0:
                    lst.append(w.text)

            o.text = " ".join(lst)

            owner.add_line(o)
            doc.add_line(o)

    def parse_line(self, doc: Document, owner: OcrPar, node: bs4.Tag) -> None:
        pars = node.find_all(class_="ocr_line")
        for node2 in pars:
            o = HocrParser.OcrLine()
            self.parse_node(o, node2)
            o.baseline = self.parse_baseline(o)
            o.x_ascenders = self.parse_float_tag(o, "x_ascenders")
            o.x_descenders = self.parse_float_tag(o, "x_descenders")
            o.x_size = self.parse_float_tag(o, "x_size")
            o.lang = node2.get("lang")
            self.parse_word(doc, o, node2)

            lst = []
            for w in o.words:
                if len(w.text) > 0:
                    lst.append(w.text)

            o.text = " ".join(lst)

            owner.add_line(o)
            doc.add_line(o)

    def parse_node(self, o: OcrNode, node: bs4.Tag) -> None:
        o.id = node.get("id")
        o.title = node.get("title")
        o.mapTitle = {}

        if o.title:
            a1 = o.title.split(";")
            for s1 in a1:
                if not s1:
                    continue

                s1 = s1.strip()
                if not s1:
                    continue

                a2 = s1.split(" ")
                if not a2:
                    continue

                if not a2[0]:
                    continue

                o.mapTitle[a2[0]] = a2

        o.bbox = HocrParser.BBox()
        if "bbox" in o.mapTitle.keys():
            a = o.mapTitle["bbox"]
            if len(a) >= 5:
                o.bbox.left = int(round(float(a[1])))
                o.bbox.top = int(round(float(a[2])))
                o.bbox.right = int(round(float(a[3])))
                o.bbox.bottom = int(round(float(a[4])))

    def parse_page(self, doc: Document, node: bs4.Tag) -> None:
        pages = node.find_all(class_="ocr_page")
        for node2 in pages:
            o = HocrParser.OcrPage()
            self.parse_node(o, node2)
            o.image = self.parse_str_tag(o, "image")
            o.ppageno = self.parse_int_tag(o, "ppageno")
            self.parse_carea(doc, o, node2)
            doc.add_page(o)

    def parse_par(self, doc: Document, owner: OcrCarea, node: bs4.Tag) -> None:
        pars = node.find_all(class_="ocr_par")
        for node2 in pars:
            o = HocrParser.OcrPar()
            self.parse_node(o, node2)
            o.lang = node2.get("lang")
            self.parse_caption(doc, o, node2)
            self.parse_header(doc, o, node2)
            self.parse_line(doc, o, node2)
            owner.add_par(o)

    def parse_word(self, doc: Document, owner: OcrLine, node: bs4.Tag) -> None:
        pars = node.find_all(class_="ocrx_word")
        for node2 in pars:
            o = HocrParser.OcrxWord()
            self.parse_node(o, node2)
            o.x_wconf = self.parse_float_tag(o, "x_wconf")
            if doc.strip_word_whitespaces:
                o.text = str(node2.get_text()).replace("\n", "").replace(" ", "")
            else:
                o.text = str(node2.get_text())
            self.parse_cinfo(doc, owner, o, node2)
            owner.add_word(o)
            doc.add_word(o)

    def parse_int_tag(self, o: OcrNode, name: str) -> int:
        r = self.parse_str_tag(o, name)
        if r is None:
            return r
        return int(r)

    def parse_float_tag(self, o: OcrNode, name: str) -> float:
        r = self.parse_str_tag(o, name)
        if r is None:
            return r
        return float(r)

    def parse_str_tag(self, o: OcrNode, name: str) -> str:
        if not o.mapTitle:
            return None

        if name not in o.mapTitle.keys():
            return None

        a = o.mapTitle[name]
        if not a:
            return None

        if len(a) < 2:
            return None

        return a[1]
