import os
import logging
from datetime import datetime
import time
import socket
from noisseur.core import app_config
from noisseur.ocr import TesseractOcr
from noisseur.imgproc import ImageProcessor
from noisseur.model import ModelService, ModelFactory

from flask import render_template, make_response, \
    jsonify, request, Markup, Blueprint

logger = logging.getLogger(__name__)
logger.debug("name=" + __name__)

test_bp = Blueprint('test_bp', __name__)


@test_bp.route('/')
def home():
    logger.debug("home")
    return render_template('test/home.j2', name1='Flask')


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


@test_bp.route('/model_visualize', methods=['GET', 'POST'])
def model_visualize():
    logger.debug("model_visualize")
    model_id = request.form["model_id"]
    logger.debug(f"model_id={model_id}")
    svc = ModelFactory.get_service()
    model = svc.find_by_id(model_id)
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
    t = TesseractOcr()
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
    t = TesseractOcr()
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
    t = TesseractOcr()
    doc = t.ocr_hocr(path2, chain)
    data = t.hocr_visualize_as_png(path2, chain, doc)
    return response_ok(data, "image/png")


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
    t = TesseractOcr()
    dt = time.time()
    data = t.ocr_screen(path2, chain, scale)
    dt = int((time.time() - dt)*1000)
    logger.debug("dt={}ms".format(dt))
    res = str(data) + "\n\n##############################\n\ndt={}ms".format(dt)
    return response_ok(res, "text/plain")


@test_bp.route('/tesseract_version', methods=['GET', 'POST'])
def tesseract_version():
    logger.debug("tesseract_version")
    t = TesseractOcr()
    return response_ok(t.tesseract_version(), "text/plain")


@test_bp.route('/vips_version', methods=['GET', 'POST'])
def vips_version():
    logger.debug("vips_version")
    p = ImageProcessor()
    return response_ok(p.vips_version(), "text/plain")


