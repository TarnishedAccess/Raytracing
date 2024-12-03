from PIL import Image
from numpy import array
from math import atan2, asin, pi

class Skybox():
    def __init__(self, image):
        self.skybox_image = Image.open(image)
        self.skybox_array = array(self.skybox_image)

    #source: https://en.wikipedia.org/wiki/UV_mapping
    #this is what handles turning a simple image into something of a sphere around the area (panoramic)
    def map_UV(self, direction):
        u = 0.5 + atan2(direction[2], direction[0]) / (2 * pi)
        v = 0.5 - asin(direction[1]) / pi
        return (u, v)
    
    def get_skybox_pixel(self, direction):
        u, v = self.map_UV(direction)
        height, width, _ = self.skybox_array.shape
        #u and v are normalized between 0 and 1. Multiply by width and height to get pixel position.
        #we use modulo to handle wrapping around
        x = int(u * width) % width
        y = int(v * height) % height
        return self.skybox_array[y, x]