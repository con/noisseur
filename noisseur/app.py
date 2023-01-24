import logging

from flask import Flask, render_template

from core import app_init
from core import app_config

from noisseur.app import api
from noisseur.app import test

logger = logging.getLogger(__name__)
logger.debug("name=" + __name__)


def create_flask_app() -> Flask:
    app_init()

    logger.info("app")

    app = Flask(__name__, template_folder='app/web/templates', static_folder='app/web/static')
    logger.debug("Loading Flask app config...")
    app.config.from_mapping(app_config.flask)

    api.app = app

    with app.app_context():

        logger.debug("Registering blueprint: admin ...")
        app.register_blueprint(api.api_bp, url_prefix='/api')

        logger.debug("Registering blueprint: test ...")
        app.register_blueprint(test.test_bp, url_prefix='/test')

    @app.route('/')
    def home():
        logger.debug("home")
        return render_template('home.j2')

    return app


def main():
    app = create_flask_app()
    logger.debug("Running server ...")
    app.run(use_reloader=False)


if __name__ == "__main__":
    main()
