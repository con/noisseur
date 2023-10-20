import os
import io
import time
import datetime
import platform
import logging
import logging.config
from enum import Enum
from dataclasses import dataclass, field
from dataclasses_json import dataclass_json
from PIL import Image, ImageDraw
from pathlib import Path
from noisseur.hocr import HocrParser
from noisseur.ocr import OcrService, OcrFactory, OcrScreenData

logger = logging.getLogger(__name__)


@dataclass_json
@dataclass
class GetScreenDataResponse:
    host: str = "localhost"
    ts: str = None
    dt_ms: int = 0
    success: bool = False
    errors: list[str] = None
    type: str = None
    data: dict = None

    def add_error(self, s: str):
        if not self.errors:
            self.errors = []
        self.errors.append(s)


class ApiService:

    def __init__(self):
        logger.debug("ApiService()")

    def get_screen_data(self, image: bytes, path: str) -> GetScreenDataResponse:
        res: GetScreenDataResponse = GetScreenDataResponse(None, None, None, False, None, None, None)
        dt = time.time()
        ts = str(datetime.datetime.now())

        try:
            if not image and not path:
                raise Exception("No input data specified (image or path)")

            res2: OcrScreenData = OcrFactory.get_service().ocr_screen(
                image if image else path,
                # "scale(3.0,nearest)|bw|border(30)",
                "prisma(3,30)",
                3.0, 0
            )
            if res2:
                res.host = res2.host
                res.ts = res2.ts
                res.dt_ms = res2.dt_ms
                res.success = res2.success
                res.errors = res2.errors
                res.type = res2.type
                res.data = res2.data

        except BaseException as e:
            res.add_error(f"System error: {str(e)}")

        finally:
            res.host = platform.node()
            res.dt_ms = int((time.time() - dt) * 1000)

        return res


class ApiFactory:

    @staticmethod
    def get_service() -> ApiService:
        return ApiService()
