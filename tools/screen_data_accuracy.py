import json
import logging.config
import os
import sys
import time
from pathlib import Path

import click
import enchant
import requests

logger = logging.getLogger(__name__)
logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))
# logger.setLevel(logging.DEBUG)
logger.setLevel(logging.INFO)
logger.debug(f"name={__name__}")


def calc_str_mismatch(v0, v1) -> float:
    res: float = 0.0
    if v0 and v1 and isinstance(v0, str) and isinstance(v1, str):
        if len(v0) > 0 and len(v1) > 0:
            n = enchant.utils.levenshtein(v0, v1)
            if n <= 0:
                res = 1.0
            else:
                if n < len(v0):
                    res = (len(v0) - n) / len(v0)
    return res


def validate_screen(noisseur_api_url: str, upload_image: bool,
                    path_image: str, path_json: str, verbose: bool):
    logger.debug("validate_screen(...)")

    if verbose:
        click.echo(f"    {path_image}")
        click.echo(f"    {path_json}")

    data0 = {}
    with open(path_json, 'r') as json_file:
        data0 = json.load(json_file)

    headers = {
        'accept': 'application/json',
    }

    if upload_image:
        ext = os.path.splitext(path_image)[1]
        mimetypes = {
            '.png': 'image/png',
            '.tif': 'image/tiff',
            '.tiff': 'image/tiff',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
        }

        params = None
        files = {
            "screen": (os.path.basename(path_image),
                       open(path_image, 'rb'),
                       mimetypes[ext])
        }
    else:
        files = None
        params = {
            "path": path_image
        }

    url = f"{noisseur_api_url}/get_screen_data"

    if verbose:
        click.echo(f"    POST {url}")
        if params:
            click.echo(f"        params={str(params)}")
        if files:
            click.echo(f"        files={str(files)}")

    dt = time.time()
    response = requests.post(f"{url}",
                             params=params,
                             headers=headers,
                             files=files,
                             verify=False  # NOTE: This should be only used
                             # with local self-signed
                             # certificates and not in
                             # production environment
                             )
    dt = time.time() - dt
    dts = f"{dt:.3f} seconds"
    logger.debug(dts)
    dt = int(dt * 1000) / 1000.0

    c_all: int = 1
    c_match: float = 0

    c_field: int = 0
    c_strict_match: int = 0

    if response.status_code == 200:
        res = response.json()
        model_type1 = res["type"]
        model_data1 = res["data"]
        logger.debug(f"model type: {model_type1}")

        model_type0 = data0["type"]
        model_data0 = data0["data"]

        if model_type0 == model_type1:
            logger.debug("TODO: validate data")
            c_match += 1.0
            c_all += 1
            for key, val0 in model_data0.items():
                c_all += 1
                c_field += 1
                if key in model_data1:
                    val1 = model_data1[key]
                    if val1 == val0:
                        c_match += 1.0
                        c_strict_match += 1
                        if verbose:
                            click.echo(f"    data match [{key},"
                                       f" 100.00%] {val0} / {val1}")
                    else:
                        r = calc_str_mismatch(val0, val1)
                        logger.debug(f" data mismatch [{key}, {(r*100.0):.2f}%] {val0} / {val1}")
                        if verbose:
                            click.echo(f"    data mismatch [{key}, {(r*100.0):.2f}%] {val0} / {val1}",
                                       err=True)
                        c_match += calc_str_mismatch(val0, val1)
        else:
            logger.debug(f"Model type mismatch: {model_type0} / {model_type1}")
            if verbose:
                click.echo(f"    model type mismatch: {model_type0} / {model_type1}", err=True)
            c_match = 0

    accuracy: float = c_match * 100.0 / c_all if c_all > 0 else 0.0
    accuracy = int(100 * accuracy) / 100.0
    strict_match: float = c_strict_match * 100.0 / c_field if c_field > 0 else 0.0
    strict_match = int(100 * strict_match) / 100.0

    if verbose:
        click.echo(f"    strict match data count={c_strict_match}, all fields count={c_field}")

    return {
        "accuracy": accuracy,
        "strict_match": strict_match,
        "time_sec": dt
    }


@click.command(help='OCR screen_data accuracy measure tool. '
                    'Works against running con/noisseur server.')
@click.option('--noisseur-api-url',
              help='Noisseur API base URL. Default is http://127.0.0.1:5050/api/1',
              required=True,
              default='http://127.0.0.1:5050/api/1')
@click.option('--path-data',
              help='Path to screen data directory. Default is data/screen_data',
              required=True,
              default='data/screen_data')
@click.option('--upload-image', is_flag=True,
              help='Send screen image BLOB to server rather than use path')
@click.option('--max-count',
              help='Specify max screen data cases to be processed. Default is -1.',
              type=int,
              default=-1)
@click.option('--verbose', is_flag=True,
              help='Provide detailed information to output console')
def main(noisseur_api_url, path_data, upload_image, max_count, verbose):
    logger.debug("screen_data_accuracy.py tool")
    logger.debug(f" noisseur_api_url={noisseur_api_url}")
    logger.debug(f" path_data={path_data}")

    _root_path = str(Path(__file__).parent.parent)
    logger.debug(f" _root_path={_root_path}")

    if not os.path.exists(path_data):
        path_data = os.path.join(_root_path, path_data)

    images = [filename for filename in os.listdir(path_data)
              if filename.endswith(('.png', '.tiff', '.tif', '.jpg', '.jpeg'))]
    # sort by name
    images = sorted(images)

    click.echo(f"Images count: {len(images)}")

    total_count: int = 0
    total_accuracy: float = 0.0
    total_strict_match: float = 0.0
    total_time_sec: float = 0.0

    for index, image in enumerate(images):
        if 0 < max_count <= index:
            break
        click.echo(f"[{index}]: {image}")
        path_image = os.path.join(path_data, image)
        path_json = os.path.join(path_data, os.path.splitext(image)[0] + '.json')
        logger.debug(f" {path_image}, {path_json}")
        res = validate_screen(noisseur_api_url, bool(upload_image),
                              path_image, path_json, bool(verbose))
        accuracy = res["accuracy"]
        strict_match = res["strict_match"]
        time_sec = res["time_sec"]
        click.echo(f"    accuracy={str(accuracy)}%, strict_match={str(strict_match)}%, time={time_sec} sec")

        total_count += 1
        total_accuracy += accuracy
        total_strict_match += strict_match
        total_time_sec += time_sec

    click.echo("--------------------------------------")
    click.echo(f"Total screen count   : {total_count}")
    click.echo(f"Total time           : {total_time_sec:0.3f} sec")

    if total_count > 0:
        avg_accuracy = total_accuracy / total_count
        avg_strict_match = total_strict_match / total_count
        avg_time = total_time_sec / total_count
        click.echo(f"Average accuracy     : {avg_accuracy:0.2f}%")
        click.echo(f"Average strict_match : {avg_strict_match:0.2f}%")
        click.echo(f"Average time         : {avg_time:0.3f} sec")

    click.echo("--------------------------------------")
    click.echo("Done.")


if __name__ == "__main__":
    main()
