import io
import logging
import logging.config
import pyvips
import PIL

logger = logging.getLogger(__name__)

class ImageProcessor:

    #: default output format
    OUT_VIPS_FORMAT = ".png"
    OUT_PIL_FORMAT = "PNG"

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

    def caption_ex(self, path):
        logger.debug("caption_ex")
        image = self.pil_load(path)
        image = image.convert("RGB")
        width, height = image.size

        top_line = None
        bottom_line = None
        for y in range(0, int(height * 0.33)):
            f = True
            for x in range(int(width * 0.25), int(width * 0.75)):
                r, g, b = image.getpixel((x, y))
                if r != 0 or g != 0 or b <= 120 or b >= 130:
                    f = False
                    break
            if f:
                # logger.debug("Blue line on Y == {}".format(y))
                bottom_line = y
                if not top_line:
                    top_line = y

        if top_line and bottom_line and bottom_line > top_line:
            image = image.crop((0, top_line, width, bottom_line))
            # image = PIL.ImageOps.expand(image, border=50, fill="black")
            return {"rc": (0, top_line, width, bottom_line), "data": self.to_buffer(image)}
        else:
            return None  # image = PIL.Image.new("RGB", (1, 1), "white")

    def caption(self, path):
        logger.debug("caption(...)")
        res = self.caption_ex(path)
        if res:
            return res["data"]
        else:
            return self.to_buffer(PIL.Image.new("RGB", (1, 1), "white"))

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
        image = pyvips.Image.resize(image, factor, kernel="mitchell")
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
        elif isinstance(image, PIL.Image.Image):
            b = io.BytesIO()
            image.save(b, format=self.OUT_PIL_FORMAT)
            b.seek(0)
            data = b.read()
            return data
        return None

    def pil_load(self, pathOrData):
        if isinstance(pathOrData, bytes):
            image = PIL.Image.open(io.BytesIO(pathOrData))
        else:
            image = PIL.Image.open(pathOrData)
        return image

    def vips_load(self, pathOrData) -> pyvips.Image:
        if isinstance(pathOrData, bytes):
            image = pyvips.Image.new_from_buffer(pathOrData, "")
        else:
            image = pyvips.Image.new_from_file(pathOrData, access="sequential")
        return image

    def vips_version(self):
        return "vips-{}.{}.{}".format(pyvips.version(0), pyvips.version(1), pyvips.version(2))
