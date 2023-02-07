import logging
from dataclasses import dataclass, field
from dataclasses_json import dataclass_json
from flask import Flask, render_template, make_response, \
    jsonify, request, Markup, Blueprint

from noisseur.api import ApiService, ApiFactory, GetScreenDataResponse

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

    if request.method == "POST":
        f = request.files["screen"]
        if not f:
            raise Exception("screen data not found")

        image = f.read()
        res = ApiFactory.get_service().get_screen_data(image)

    return response_ok(res.to_json(indent=4), "application/json")



