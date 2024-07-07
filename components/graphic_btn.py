import PySimpleGUI as sg
import io
from PIL import Image
import base64

DEF_BUTTON_COLOR = ('white', 'black')

def resize_base64_image(image64, size):
    '''
    May not be the original purpose, but this code is being used to resize an image for use with PySimpleGUI (tkinter) button graphics
    :param image64: (str) The Base64 image
    :param size: Tuple[int, int] Size to make the image in pixels (width, height)
    :return: (str) A new Base64 image
    '''
    image_file = io.BytesIO(base64.b64decode(image64))
    img = Image.open(image_file)
    img.thumbnail(size,  Image.LANCZOS)
    bio = io.BytesIO()
    img.save(bio, format='PNG')
    imgbytes = bio.getvalue()
    return imgbytes
def GraphicButton(text, key, image_data, color=DEF_BUTTON_COLOR, size=(100, 50)):
    '''
    A user defined element.  Use this function inside of your layouts as if it were a Button element (it IS a Button Element)
    Only 3 parameters are required.

    :param text: (str) Text you want to display on the button
    :param key:  (Any) The key for the button
    :param image_data: (str) The Base64 image to use on the button
    :param color: Tuple[str, str] Button color
    :param size: Tuple[int, int] Size of the button to display in pixels (width, height)
    :return: (PySimpleGUI.Button) A button with a resized Base64 image applied to it
    '''
    return sg.Button(text, image_data=resize_base64_image(image_data, size), button_color=color, font='Any 15', pad=(0, 0), key=key, border_width=0)