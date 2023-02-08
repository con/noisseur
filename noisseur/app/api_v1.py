import logging
import os
from dataclasses import dataclass, field
from dataclasses_json import dataclass_json
from flask import Flask, render_template, make_response, \
    jsonify, request, Markup, Blueprint

from noisseur.api import ApiService, ApiFactory, GetScreenDataResponse
from noisseur.cfg import AppConfig

logger = logging.getLogger(__name__)
logger.debug("name=" + __name__)

api_v1_bp = Blueprint('api_v1_bp', __name__)


def response_ok(res, mimetype):
    response = make_response(res, 200)
    response.mimetype = mimetype
    return response


@api_v1_bp.route('/')
def home():
    logger.debug("home")
    return render_template('api_v1/home.j2')


@api_v1_bp.route('/get_screen_data', methods=['GET', 'POST'])
def get_screen_data():
    logger.debug("get_screen_data")
    res: GetScreenDataResponse = GetScreenDataResponse(None, None, None, False, None, None, None)

    image = None
    path = None

    if request.method == "POST":
        f = request.files["screen"]
        # if not f:
        #    raise Exception("screen data not found")
        if f:
            image = f.read()

    path = request.form["path"]
    logger.debug(f"path={path}")
    if path:
        path = os.path.join(AppConfig.instance.ROOT_PATH, path);
    logger.debug(f"path#2={path}")

    res = ApiFactory.get_service().get_screen_data(image, path)

    return response_ok(res.to_json(indent=4), "application/json")



