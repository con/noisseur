import logging
import os
import io
from dataclasses import dataclass, field
from dataclasses_json import dataclass_json
from flask import Flask, render_template, make_response, \
    jsonify, request, Markup, Blueprint
from flask_restx import Api, Resource, fields, reqparse
from werkzeug.datastructures import FileStorage
from noisseur.api import ApiService, ApiFactory, GetScreenDataResponse
from noisseur.cfg import AppConfig

logger = logging.getLogger(__name__)
logger.debug("name=" + __name__)

api_v1_bp = Blueprint('api_v1_bp', __name__)

api = Api(
    api_v1_bp,
    version="1.0",
    title="Noisseur REST API",
    description="Noisseur public REST API",
    doc="swagger-ui"
)

ns = api.namespace(
    "ApiService",
    description="Noisseur API operations",
    path="/"
)

ping_model = api.model(
    "PingResponse", {
        "message": fields.String
    }
)
ping_parser = api.parser()
ping_parser.add_argument("text1", type=str, required=True, help="Some text to be sent back")


@ns.route("/ping")
class PingAction(Resource):
    """Simple ping action"""

    @api.doc(parser=ping_parser, description="Simple ping action GET")
    @api.marshal_with(ping_model)
    def get(self):
        logger.debug("ping()")
        args = ping_parser.parse_args()
        return {"message": f"Pong: {str(args['text1'])}", "aaa": "zzz"}


get_screen_data_model = api.model(
    "GetScreenDataResponse", {
        "host": fields.String(description="Host name"),
        "ts": fields.String(description="Execution timestamp"),
        "dt_ms": fields.Integer(description="Execution time in ms"),
        "success": fields.Boolean(description="True on success, otherwise False"),
        "errors": fields.List(fields.String, description="List of errors if any"),
        "type": fields.String(description="Recognized screen model type"),
        "data": fields.Raw(description="Recognized Siemens console data in JSON format")
    }
)
get_screen_data_parser = api.parser()
get_screen_data_parser.add_argument("path", type=str, help="Image PNG local path absolute or relative to project root")
get_screen_data_parser.add_argument('screen', location='files', type=FileStorage)


@ns.route("/get_screen_data")
class GetScreenDataAction(Resource):
    """Get screen data action"""

    def execute(self):
        logger.debug("execute()")

        image = None
        path = None

        args = get_screen_data_parser.parse_args()

        path = args["path"]
        logger.debug(f"path={path}")
        if path and not os.path.exists(path):
            path = os.path.join(AppConfig.instance.ROOT_PATH, path)
            logger.debug(f"path#2={path}")

        if args["screen"]:
            logger.debug("screen parameter is specified")
            b = io.BytesIO()
            image = args["screen"].save(b)
            b.seek(0)
            image = b.read()

        res = ApiFactory.get_service().get_screen_data(image, path)
        return res

    @api.doc(parser=get_screen_data_parser, description="Recognize and parse Siemens console screen")
    @api.marshal_with(get_screen_data_model)
    def get(self):
        return self.execute()

    @api.doc(parser=get_screen_data_parser, description="Recognize and parse Siemens console screen")
    @api.marshal_with(get_screen_data_model)
    def post(self):
        return self.execute()

