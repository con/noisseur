import json
import os
import io
import logging
from datetime import datetime
import time
import socket
from PIL import Image, ImageOps, ImageDraw, ImageFont, FontFile
from noisseur.core import app_config
from noisseur.ocr import OcrService, OcrFactory
from noisseur.imgproc import ImageProcessor
from noisseur.model import ModelService, ModelFactory
from noisseur.model_prototype import generate_models


from flask import render_template, make_response, \
    jsonify, request, Markup, Blueprint

logger = logging.getLogger(__name__)
logger.debug("name=" + __name__)

test_bp = Blueprint('test_bp', __name__)


@test_bp.route('/')
def home():
    logger.debug("home")
    return render_template('test/home.j2', name1='Flask', model_factory=ModelFactory)


@test_bp.route('/hw', methods=['GET', 'POST'])
def hw():
    logger.debug("hw")
    return Markup('<h3>Hello World!!!</h3>')


@test_bp.route('/ping', methods=['GET', 'POST'])
def ping():
    logger.debug("ping")
    res = {}
    headers = {"Content-Type": "application/json"}
    res["message"] = f'pong: {str(request.form.get("text1"))}'
    res["success"] = True
    res["host"] = socket.gethostname()
    res["ts"] = str(datetime.now())
    return make_response(jsonify(res), 200, headers)


def response_ok(res, mimetype):
    response = make_response(res, 200)
    response.mimetype = mimetype
    return response


@test_bp.route('/imgproc_chain', methods=['GET', 'POST'])
def imgproc_chain():
    logger.debug("imgproc_chain")
    path = request.form["path"]
    logger.debug(f"path={path}")
    path2 = os.path.join(app_config.ROOT_PATH, path);
    logger.debug(f"path2={path2}")
    chain = request.form["chain"]
    logger.debug(f"chain={chain}")
    ip = ImageProcessor()
    dt = time.time()
    data =ip.chain(path2, chain)
    dt = int((time.time() - dt)*1000)
    logger.debug("dt={}ms".format(dt))
    return response_ok(data, ip.OUT_MIME_TYPE)

@test_bp.route('/model_generate', methods=['GET', 'POST'])
def model_generate():
    logger.debug("model_generate")
    generate_models()
    ModelFactory.reload()
    return response_ok("Done", "text/plain")


@test_bp.route('/model_visualize', methods=['GET', 'POST'])
def model_visualize():
    logger.debug("model_visualize")
    screen_type = request.form["screen_type"]
    logger.debug(f"screen_type={screen_type}")
    svc = ModelFactory.get_service()
    model = svc.find_by_screen_type(screen_type)
    data = svc.visualize_as_png(model)
    return response_ok(data, "image/png")


@test_bp.route('/ocr_text', methods=['GET', 'POST'])
def ocr_text():
    logger.debug("ocr_text")
    path = request.form["path"]
    logger.debug(f"path={path}")
    path2 = os.path.join(app_config.ROOT_PATH, path);
    logger.debug(f"path2={path2}")
    chain = request.form["chain"]
    logger.debug(f"chain={chain}")
    t = OcrFactory.get_service()
    dt = time.time()
    res = t.ocr_text(path2, chain)
    dt = int((time.time() - dt)*1000)
    logger.debug("dt={}ms".format(dt))
    logger.debug(f"res={res}")
    return response_ok(res + "\n\n##############################\n\ndt={}ms".format(dt), "text/plain")


@test_bp.route('/ocr_hocr', methods=['GET', 'POST'])
def ocr_hocr():
    logger.debug("ocr_hocr")
    path = request.form["path"]
    logger.debug(f"path={path}")
    path2 = os.path.join(app_config.ROOT_PATH, path);
    logger.debug(f"path2={path2}")
    chain = request.form["chain"]
    logger.debug(f"chain={chain}")
    t = OcrFactory.get_service()
    dt = time.time()
    doc = t.ocr_hocr(path2, chain)
    dt = int((time.time() - dt)*1000)
    logger.debug("dt={}ms".format(dt))
    text = "\n".join([line.text for line in doc.lines])
    res = text + "\n\n##############################\n\ndt={}ms".format(dt) + \
          "\n\n##############################\n\n" + doc.hocr
    return response_ok(res, "application/x-view-source")

@test_bp.route('/ocr_hocr_visualize', methods=['GET', 'POST'])
def ocr_hocr_visualize():
    logger.debug("ocr_hocr_visualize")
    path = request.form["path"]
    logger.debug(f"path={path}")
    chain = request.form["chain"]
    logger.debug(f"chain={chain}")
    path2 = os.path.join(app_config.ROOT_PATH, path);
    logger.debug(f"path2={path2}")
    t = OcrFactory.get_service()
    doc = t.ocr_hocr(path2, chain)
    data = t.hocr_visualize_as_png(path2, chain, doc)
    return response_ok(data, "image/png")

@test_bp.route('/ocr_caption', methods=['GET', 'POST'])
def ocr_caption():
    logger.debug("ocr_caption")
    path = request.form["path"]
    logger.debug(f"path={path}")
    path2 = os.path.join(app_config.ROOT_PATH, path);
    logger.debug(f"path2={path2}")
    t = OcrFactory.get_service()
    dt = time.time()
    data = t.ocr_caption(path2)
    dt = int((time.time() - dt)*1000)
    logger.debug("dt={}ms".format(dt))
    if data:
        text = str(data)
    else:
        text = "Not found"

    res = text + "\n\n##############################\n\ndt={}ms".format(dt)
    return response_ok(res, "text/plain")


@test_bp.route('/ocr_screen', methods=['GET', 'POST'])
def ocr_screen():
    logger.debug("ocr_screen")
    path = request.form["path"]
    logger.debug(f"path={path}")
    path2 = os.path.join(app_config.ROOT_PATH, path);
    logger.debug(f"path2={path2}")
    chain = request.form["chain"]
    logger.debug(f"chain={chain}")
    scale = float(request.form["scale"])
    logger.debug(f"scale={scale}")
    border = int(request.form["border"])
    logger.debug(f"border={border}")
    t = OcrFactory.get_service()
    dt = time.time()
    data = t.ocr_screen(path2, chain, scale, border)
    dt = int((time.time() - dt)*1000)
    logger.debug("dt={}ms".format(dt))
    # res = json.dumps(data, indent=4) + "\n\n##############################\n\ndt={}ms".format(dt)
    res = data.to_json(indent=4)
    return response_ok(res, "text/plain")

@test_bp.route('/test_font', methods=['GET', 'POST'])
def test_font():
    logger.debug("test_font")

    image = Image.open(os.path.join(app_config.ROOT_PATH, "data/s_009.png"))
    image = image.convert("RGB")
    width, height = image.size

    top_line = None
    bottom_line = None
    for y in range(0, int(height*0.33)):
        f = True
        for x in range(int(width*0.25), int(width*0.75)):
            r, g, b = image.getpixel((x, y))
            if r != 0 or g != 0 or b <= 120 or b >= 130:
                f = False
                break
        if f:
            logger.debug("Blue line on Y == {}".format(y))
            bottom_line = y
            if not top_line:
                top_line = y

    if top_line and bottom_line and bottom_line > top_line:
        image = image.crop((0, top_line, width, bottom_line))
        image = ImageOps.expand(image, border=50, fill="black")
    else:
        image = Image.new("RGB", (1, 1), "white")


    """
    pixels = list(im.getdata())
    width, height = im.size

    pixels = [pixels[i * width:(i + 1) * width] for i in range(height)]

    
    for idx, y in enumerate(pixels):
        if y[200] == (0, 0, 128):
            logger.debug("Line {} is white.".format(idx))
    """

    """
    image = Image.new("RGB", (1024, 768), "white")

    font = ImageFont.truetype(os.path.join(app_config.ROOT_PATH, "data/clinicapro.otf"), size=16)
    draw = ImageDraw.Draw(image)
    draw.text((0, 0, 1024, 768), "\nLast name O0O0o0o0O0O\n0123456789QWERTUIOP{}ASDF\nHead First - Supine\nPatient ID",\
              fill="black", align="left", font=font)
    """

    b = io.BytesIO()
    image.save(b, format="PNG")
    b.seek(0)
    data = b.read()
    return response_ok(data, "image/png")


@test_bp.route('/tesseract_version', methods=['GET', 'POST'])
def tesseract_version():
    logger.debug("tesseract_version")
    t = OcrFactory.get_service()
    return response_ok(t.tesseract_version(), "text/plain")


@test_bp.route('/vips_version', methods=['GET', 'POST'])
def vips_version():
    logger.debug("vips_version")
    p = ImageProcessor()
    return response_ok(p.vips_version(), "text/plain")


