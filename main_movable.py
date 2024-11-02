import pygame
import numpy as np
from camera import Camera
from objectHandler import Sphere

def update_view(screen, camera, spheres, screen_width, screen_height):
    #black background, will probably replace with a floor/skybox or something later
    background_color = (0, 0, 0)
    screen.fill(background_color)

    for y in range(screen_height):
        for x in range(screen_width):
            ray = camera.castRay(x, y)
            #will probably refactor intersection detection later on so that it's based on the ray rather than the object. I think it'd be better that way?
            closest_t = np.inf
            closest_sphere = None

            for sphere in spheres:
                intersection_point, t = sphere.intersect(ray)
                if intersection_point is not None and t < closest_t:
                    closest_t = t
                    closest_sphere = sphere
                    #find the intersection point of each sphere and render the closest one.

            if closest_sphere:
                color = closest_sphere.color
                screen.set_at((x, y), color)
                #pygame.display.update((x, y, 1, 1))

def main():
    pygame.init()

    screen_width = 100
    screen_height = 75
    camera_position = (0, 0, 0)
    #standard FOV is 90, quake FOB is 110, play around with it if you want, looks funny.
    fov = 90
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("Ray Tracing from Ouedkniss")
    camera = Camera(camera_position, screen_width, screen_height, fov)
    #(x, y, z), radius
    spheres = [
        Sphere((0, 0, -5), 1, (255, 0, 0)),
        Sphere((4, 0, -7), 1, (0, 0, 255)),
        Sphere((-2, 0, -7), 1, (0, 255, 0))
    ]


    running = True
    while running:
        update_view(screen, camera, spheres, screen_width, screen_height)
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    camera.position = (camera.position[0] - 1, camera.position[1], camera.position[2])
                if event.key == pygame.K_RIGHT:
                    camera.position = (camera.position[0] + 1, camera.position[1], camera.position[2])
                if event.key == pygame.K_LSHIFT:
                    camera.position = (camera.position[0], camera.position[1] + 1, camera.position[2])
                if event.key == pygame.K_SPACE:
                    camera.position = (camera.position[0], camera.position[1] - 1, camera.position[2])
                if event.key == pygame.K_UP:
                    camera.position = (camera.position[0], camera.position[1], camera.position[2] - 1)
                if event.key == pygame.K_DOWN:
                    camera.position = (camera.position[0], camera.position[1], camera.position[2] + 1)

    pygame.quit()

if __name__ == "__main__":
    main()