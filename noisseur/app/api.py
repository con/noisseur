import logging
from flask import Flask, render_template, Blueprint

logger = logging.getLogger(__name__)
logger.debug("name=" + __name__)

app: Flask = None
api_bp = Blueprint('api_bp', __name__)


@api_bp.route('/')
def home():
    logger.debug("home")
    return render_template('api/home.j2')




