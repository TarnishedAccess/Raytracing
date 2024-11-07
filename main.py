import pygame
import numpy as np
from camera import Camera
from objectHandler import Sphere, Plane
from light import Light

def main():
    pygame.init()

    screen_width = 800
    screen_height = 600
    camera_position = (0, 1, 0)
    #standard FOV is 90, quake FOB is 110, play around with it if you want, looks funny.
    fov = 90
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("Ray Tracing from Ouedkniss")

    camera = Camera(camera_position, screen_width, screen_height, fov)

    light = Light((4, 4, 0), (200, 200, 200), 2)
    #might add multi-light support later? probably?

    objects = [
        #(x, y, z), radius, color
        Sphere((0, 1, -5), 1, (200, 0, 0)),
        Sphere((4, 2, -8), 2, (100, 100, 100)),
        Sphere((-2, 0.5, -7), 0.5, (0, 200, 0)),
        Sphere((1.5, 0.5, -4), 0.5, (160, 32, 240)),
        #y, color
        Plane(0, ((50, 50, 50), (80, 80, 80)))
    ]
    #cyan background, will probably replace with a floor/skybox or something later
    background_color = (135, 206, 235)
    screen.fill(background_color)

    for y in range(screen_height):
        for x in range(screen_width):
            ray = camera.castRay(x, y)
            #will probably refactor intersection detection later on so that it's based on the ray rather than the object. I think it'd be better that way?
            closest_t = np.inf
            closest_object = None
            saved_intersection_point = None

            for object in objects:
                intersection_point, t = object.intersect(ray)
                if intersection_point is not None:
                    if t < closest_t:
                        closest_t = t
                        closest_object = object
                        saved_intersection_point = intersection_point
                        #find the intersection point of each object and render the closest one.
            if closest_object:
                closest_object.render(screen, x, y, saved_intersection_point, light)
                pygame.display.update((x, y, 1, 1))
            else:
                screen.set_at((x, y), background_color)
                pygame.display.update((x, y, 1, 1))

    pygame.display.flip()
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

    pygame.quit()

if __name__ == "__main__":
    main()