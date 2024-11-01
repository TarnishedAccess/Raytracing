import numpy as np
from ray import Ray

class Camera:
    def __init__(self, position, screenWidth, screenHeight, fov):
        self.position = position
        self.screenWidth = screenWidth
        self.screenHeight = screenHeight
        self.fov = fov

    def castRay(self, x, y):
        aspect_ratio = self.screenWidth / self.screenHeight

        #we center x and y since a pixel is usually defined by its top left corner
        #aka the point (2,2) is the topleft corner of the (2,2) pixel. We don't want that.
        #what we want is (2.5, 2.5), aka the center of the (2,2) pixel.
        centeredX = x + 0.5
        #divide the x position by screen width to normalize it, *2 so it's between [0, 2] then subtract 1 so its between [-1, 1] where -1 is the absolute left of the screen and 1 is the absolute right.
        screenNormalizedX = 2 * centeredX / self.screenWidth - 1
        #scale x by aspect ratio to determine its proper position on the screen
        screenScaledX = screenNormalizedX * aspect_ratio
        #convert FOV from degrees to radians (for numpy)
        #I just stole the equation under this comment. Give me like 2 weeks ill probably understand what it does 
        screenX = screenScaledX * np.tan(np.radians(self.fov) / 2)

        centeredY = y + 0.5
        #same as normalizing X except we subtract the value from 1 because in most graphic frameworks (like pygame) (0, 0) is at the top left of the screen rather that bottom left
        screenY = 1 - 2 * centeredY / self.screenHeight

        direction = np.array([screenX, screenY, -1])
        #Z=-1 since we want the ray to be going OUT of the camera AWAY from the viewer. 1 would make it go towards the screen/viewer.
        direction = direction / np.linalg.norm(direction)

        return Ray(self.position, direction)