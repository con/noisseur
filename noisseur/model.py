import os
import io
import logging
import logging.config
from noisseur.cfg import AppConfig
from enum import Enum
from dataclasses import dataclass, field
from dataclasses_json import dataclass_json
from PIL import Image, ImageDraw
from pathlib import Path
from noisseur.hocr import HocrParser

logger = logging.getLogger(__name__)


@dataclass_json
@dataclass
class BaseObject:
    id: str = None
    description: str = None

@dataclass
class Point:
    x: int = 0
    y: int = 0


@dataclass_json
@dataclass
class Rect:
    left: int = 0
    top: int = 0
    right: int = 0
    bottom: int = 0

    def __init__(self, left: int = 0, top: int = 0, right: int = 0, bottom: int = 0):
        self.left = left
        self.top = top
        self.right = right
        self.bottom = bottom

    def center(self) -> Point:
        return Point(int((self.left + self.right) / 2), int((self.top + self.bottom) / 2))

    def contains(self, pt: Point) -> bool:
        return self.left <= pt.x <= self.right and self.top <= pt.y <= self.bottom

    def copy(self):
        return Rect(self.left, self.top, self.right, self.bottom)

    @staticmethod
    def from_bbox(bbox: HocrParser.BBox):
        if bbox:
            return Rect(bbox.left, bbox.top, bbox.right, bbox.bottom)
        return None

    def offset(self, x: int, y: int):
        self.left += x
        self.top += y
        self.right += x
        self.bottom += y
        return self

    def scale(self, scale_x: float, scale_y: float):
        self.left = int(self.left * scale_x)
        self.top = int(self.top * scale_y)
        self.right = int(self.right * scale_x)
        self.bottom = int(self.bottom * scale_y)
        return self

    def union(self, rc):
        if rc:
            self.left = min(self.left, rc.left)
            self.top = min(self.top, rc.top)
            self.right = max(self.right, rc.right)
            self.bottom = max(self.bottom, rc.bottom)
        return self

    def to_list(self) -> []:
        return [self.left, self.top, self.right, self.bottom]


@dataclass_json
@dataclass
class GeomObject(BaseObject):
    rect: Rect = None

class ItemType(str, Enum):
    LABEL = "label"
    CAPTION = "caption"
    TEXT = "text"
    RADIO_BOX = "radio_box"
    CHECK_BOX = "check_box"
    LIST = "list"

    def __str__(self) -> str:
        return self.value


class ItemDataType(str, Enum):
    STR = "str"
    INT = "int"
    DATE = "date"
    TIME = "time"
    DATETIME = "datetime"
    FLOAT = "float"
    BOOL = "bool"
    DICT = "dict"
    LIST = "list"

    def __str__(self) -> str:
        return self.value


class ControlPointType(str, Enum):
    TOP_LEFT = "top_left"
    TOP_RIGHT = "top_right"
    BOTTOM_RIGHT = "bottom_right"
    BOTTOM_LEFT = "bottom_left"

    def __str__(self) -> str:
        return self.value


@dataclass_json
@dataclass
class Item(GeomObject):
    type: ItemType = None
    text: list[str] = None
    re: list[str] = None
    data_field: str = None
    data_type: ItemDataType = None
    data_format: str = None
    control_point: ControlPointType = None
    row_height: int = None
    list_item_screen_type: str = None


@dataclass_json
@dataclass
class Relation(BaseObject):
    from_id: str = None
    to_id: str = None


@dataclass_json
@dataclass
class Form(GeomObject):
    items: list[Item] = field(default_factory=list)
    relations: list[Relation] = field(default_factory=list)

    def find_control_point(self, type=ControlPointType.TOP_LEFT) -> Item:
        return next((item for item in self.items if item.control_point == type), None)


@dataclass_json
@dataclass
class Model(BaseObject):
    image_path: str = None
    screen_type: str = None
    form: Form = None

    """
    @staticmethod
    def from_json(s: str):
        return Model(**json.loads(s))

    def to_json(self) -> str:
        return json.dumps(self, default=lambda o: o.__dict__, indent=4)
    """

@dataclass
class ModelMatch:
    model: Model
    offset_x: int
    offset_y: int
    scale_x: float
    scale_y: float

    def copy(self):
        return ModelMatch(self.model, self.offset_x, self.offset_y, self.scale_x,self.scale_y)


class ModelService:

    def __init__(self):
        logger.debug("ModelService()")
        self.models = []  # Model[]

    def find_by_hocr(self, doc: HocrParser.Document, scale: float=1.0) -> ModelMatch:
        for model in self.models:
            match = self.match(doc, model, scale)
            if match:
                return match
        return None

    def find_by_id(self, model_id: str) -> Model:
        return next((m for m in self.models if m.id == model_id), None)

    def find_by_screen_type(self, screen_type: str) -> Model:
        return next((m for m in self.models if m.screen_type == screen_type), None)

    def get_data_as_dict(self, doc: HocrParser.Document, match: ModelMatch) -> dict:
        if not match or not doc:
            return None

        if not match.model:
            return None

        items = {}
        data = {}

        for item in match.model.form.items:

            # process item renderers
            if item.type == ItemType.LIST and item.row_height:
                lst = []
                index = 0
                for y in range(item.rect.top, item.rect.bottom, item.row_height):
                    rc2: Rect = Rect(item.rect.left, y, item.rect.right, y + item.row_height)
                    rc2.scale(match.scale_x, match.scale_y)

                    match2: ModelMatch = match.copy()
                    match2.model = ModelFactory.get_service().find_by_screen_type(item.list_item_screen_type)
                    if not match2.model:
                        raise Exception(f"Model not found: item.id={str(item.id)},"
                                        " screen_type={str(item.list_item_screen_type)}")
                    match2.offset_x = match2.offset_x + rc2.left
                    match2.offset_y = match2.offset_y + rc2.top

                    res2 = self.get_data_as_dict(doc, match2)
                    if res2 and res2["data"]:
                        data2 = res2["data"]
                        # add only dict with non-empty values
                        if any(data2.values()):
                            lst.append(data2)
                        data2["index"] = index
                    index += 1

                if item.data_field:
                    data[item.data_field] = lst
            else:
                rc: Rect = item.rect.copy()
                rc.scale(match.scale_x, match.scale_y)
                rc.offset(match.offset_x, match.offset_y)
                texts = []
                for word in doc.words:
                    rc2: Rect = Rect.from_bbox(word.bbox)
                    if rc.contains(rc2.center()):
                        texts.append(word.text)

                text = None
                if texts:
                    text = " ".join(texts)

                items[item.id] = text
                if item.data_field:
                    data[item.data_field] = text

        res = {"items": items, "type": match.model.screen_type, "data": data}
        return res

    def get_image_path(self, model: Model) -> str:
        return os.path.join(AppConfig.instance.ROOT_PATH, model.image_path)

    def load(self, path: str) -> Model:
        logger.debug("load(path={})".format(path))
        with open(path, "r") as f:
            s = f.read()
            model: Model = Model.from_json(s)
            return model

    def match(self, doc: HocrParser.Document, model: Model, scale: float) -> ModelMatch:
        if not model:
            return None

        if not model.form:
            return None

        item = model.form.find_control_point()
        if not item:
            logger.debug("control point not found")
            return None

        for text in item.text:
            text = text.lower()
            a = text.split()
            l = len(a)
            logger.debug(f"l={str(l)}")
            if l < 1:
                return None

            for line in doc.lines:
                if line.text and line.text.lower().find(text) >= 0:
                    for i, w in enumerate(line.words):
                        if w.text.lower().find(a[0]) >= 0:
                            words = []
                            rc: Rect = None
                            logger.debug(f"range: {str(i)}, {str(i+l)}")
                            for k in range(i, i+l):
                                word = line.words[k]
                                logger.debug(f"word[{str(k)}] = {word.text}")
                                rc2: Rect = Rect.from_bbox(word.bbox)
                                if rc:
                                    rc.union(rc2)
                                else:
                                    rc = rc2
                                words.append(word)

                            scale_x: float = scale
                            scale_y: float = scale
                            pt_hocr: Point = rc.center()
                            pt_item: Point = item.rect.copy().scale(scale_x, scale_y).center()
                            return ModelMatch(model, pt_hocr.x - pt_item.x, pt_hocr.y - pt_item.y, scale_x, scale_y)
        return None

    def register(self, path: str) -> None:
        logger.debug("register(...)")
        model: Model = self.load(path)
        if model:
            self.models.append(model)

    def visualize_as_png(self, model: Model) -> bytes:
        logger.debug("visualize_as_png(...)")

        path2 = Path(self.get_image_path(model))
        logger.debug("image absolute path: {}".format(path2))
        image = Image.open(path2)

        for item in model.form.items:
            draw = ImageDraw.Draw(image)
            if item.type == ItemType.LIST and item.row_height:
                for y in range(item.rect.top, item.rect.bottom, item.row_height):
                    draw.rectangle([item.rect.left, y, item.rect.right, y + 1], outline="green")

            draw.rectangle(item.rect.to_list(), outline="red")
            if item.text:
                draw.text(item.rect.to_list(), item.text[0], fill="red", align="left")

        b = io.BytesIO()
        image.save(b, format="PNG")
        b.seek(0)
        data = b.read()
        return data


class ModelFactory:
    __model_service = None

    @staticmethod
    def init() -> None:
        svc = ModelFactory.get_service()

    @staticmethod
    def get_service() -> ModelService:
        if not ModelFactory.__model_service:
            ModelFactory.reload()
        return ModelFactory.__model_service

    @staticmethod
    def reload() -> None:
        logger.debug("reload()")
        svc = ModelService()
        lst = AppConfig.instance.MODEL_LIST
        if lst:
            for path in lst:
                logger.debug("path="+path)
                svc.register(os.path.join(AppConfig.instance.ROOT_PATH, path))
        ModelFactory.__model_service = svc


# ModelFactory.init()


