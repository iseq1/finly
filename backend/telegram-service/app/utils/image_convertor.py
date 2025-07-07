from aiogram.types import FSInputFile, BufferedInputFile
import base64
import io

def img_convertor(data_url: str) -> BufferedInputFile:
    header, encoded = data_url.split(',', 1)
    image_data = base64.b64decode(encoded)
    return BufferedInputFile(file=image_data, filename="image.png")
