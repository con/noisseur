import logging

from flask import Flask, render_template

from noisseur.cfg import app_init
from noisseur.cfg import AppConfig
from noisseur.app import api_v1
from noisseur.app import test
from noisseur.model import ModelFactory

logger = logging.getLogger(__name__)
logger.debug("name=" + __name__)

flask_app: Flask = None

def create_flask_app() -> Flask:
    app_init()

    logger.info("app")

    ModelFactory.init()

    app1 = Flask(__name__, template_folder='app/web/templates', static_folder='app/web/static')
    logger.debug("Loading Flask app config...")
    app1.config.from_mapping(AppConfig.instance.flask)

    flask_app = app1

    with app1.app_context():

        logger.debug("Registering blueprint: api_v1 ...")
        app1.register_blueprint(api_v1.api_v1_bp, url_prefix='/api/1')

        logger.debug("Registering blueprint: test ...")
        app1.register_blueprint(test.test_bp, url_prefix='/test')

    @app1.route('/')
    def home():
        logger.debug("home")
        return render_template('home.j2')

    return app1


def main():
    app = create_flask_app()
    logger.debug("Running server ...")
    app.run(use_reloader=False, port=AppConfig.instance.flask.get("PORT"))


if __name__ == "__main__":
    main()
