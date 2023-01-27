import io
import logging
import logging.config
import pyvips

logger = logging.getLogger(__name__)

class ImageProcessor:

    #: default output format
    OUT_VIPS_FORMAT = ".png"

    #: default output mime type
    OUT_MIME_TYPE = "image/png"

    def border(self, path, width: int = 20):
        logger.debug("border(...,{})".format(width))
        width = int(width)
        image = self.vips_load(path)
        image2 = pyvips.Image.black(width*2 + image.width, width*2 + image.height, bands=image.bands)
        image2 = pyvips.Image.invert(image2)
        image2 = pyvips.Image.insert(image2, image, width, width)
        return self.to_buffer(image2)

    def bw(self, path):
        logger.debug("bw(...)")
        image = self.vips_load(path)
        image = image.colourspace("b-w")
        return self.to_buffer(image)

    def chain(self, path, commands):
        logger.debug(f"chain(commands={commands})")
        lst = commands.split("|")
        res = path
        for cmd in lst:
            logger.debug("cmd="+cmd)
            args = []
            name = cmd
            i = cmd.find("(")
            if i >= 0:
                name = cmd[:i]
                a = cmd[i:].strip("() ")
                args = a.split(",")

            f = getattr(self, name)
            if len(args) == 0:
                res = f(res)
            elif len(args) == 1:
                res = f(res, args[0])
            elif len(args) == 2:
                res = f(res, args[0], args[1])
            elif len(args) == 3:
                res = f(res, args[0], args[1], args[2])
            else:
                assert "Unsupported, cmd.length="+cmd.length
        return res

    def invert(self, path):
        logger.debug("invert(...)")
        image = self.vips_load(path)
        if image.hasalpha():
            alpha = image[-1]
            image = image[0:image.bands - 1]
            image = pyvips.Image.invert(image)
            image = image.bandjoin(alpha)
        else:
            image = pyvips.Image.invert(image)
        return self.to_buffer(image)

    def rotate(self, path, angle):
        logger.debug(f"rotate(.., angle={angle})")
        image = self.vips_load(path)
        image = image.rot("d{}".format(angle))
        return self.to_buffer(image)

    def scale(self, path, factor: float = 1.0):
        logger.debug("scale(...,{})".format(factor))
        factor = float(factor)
        image = self.vips_load(path)
        image = pyvips.Image.resize(image, factor)
        return self.to_buffer(image)

    def sharpen(self, path):
        logger.debug("sharpen(...)")
        image = self.vips_load(path)
        image = image.sharpen()
        return self.to_buffer(image)

    def top(self, path, height):
        logger.debug("top(...,{})".format(height))
        image = self.vips_load(path)
        image = image.crop(0, 0, image.width, height)
        return self.to_buffer(image)

    def threshold(self, path, threshold):
        logger.debug(f"threshold(.., threshold={threshold})")
        image = self.vips_load(path)
        image = image.relational_const("moreeq", int(threshold))
        return self.to_buffer(image)

    def to_buffer(self, image):
        if isinstance(image, pyvips.Image):
            data = image.write_to_buffer(self.OUT_VIPS_FORMAT)
            return data
        return None

    def vips_load(self, pathOrData) -> pyvips.Image:
        if isinstance(pathOrData, bytes):
            image = pyvips.Image.new_from_buffer(pathOrData, "")
        else:
            image = pyvips.Image.new_from_file(pathOrData, access="sequential")
        return image

    def vips_version(self):
        return "vips-{}.{}.{}".format(pyvips.version(0), pyvips.version(1), pyvips.version(2))
