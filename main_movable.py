import pygame
import numpy as np
from camera import Camera
from objectHandler import Sphere, Plane
from light import Light

def update_view(screen, render_surface, camera, objects, render_width, render_height, light):
    #black background, will probably replace with a floor/skybox or something later
    background_color = (135, 206, 235)
    render_surface.fill(background_color)

    for y in range(render_height):
        for x in range(render_width):
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
                closest_object.render(render_surface, x, y, saved_intersection_point, light)
            else:
                render_surface.set_at((x, y), background_color)

    #we do a lil scaling
    scaled_surface = pygame.transform.scale(render_surface, screen.get_size())
    screen.blit(scaled_surface, (0, 0))

def main():
    pygame.init()
    #if this is true, we move the camera
    #if it's false, we move the light
    render_width = 75
    render_height = 50
    display_width = 900
    display_height = 600
    camera_position = (0, 1, 0)
    #standard FOV is 90, quake FOV is 110, play around with it if you want, looks funny.
    fov = 90
    screen = pygame.display.set_mode((display_width, display_height))
    pygame.display.set_caption("Ray Tracing from Ouedkniss")
    camera = Camera(camera_position, render_width, render_height, fov)
    moving_object = camera
    #(x, y, z), radius
    light = Light((4, 4, 0), (255, 255, 255), 1)
    #might add multi-light support later? probably?

    objects = [
        #(x, y, z), radius, color
        Sphere((0, 1, -5), 1, (200, 50, 50)),
        Sphere((4, 2, -7), 2, (100, 100, 100)),
        Sphere((-2, 0.5, -7), 0.5, (50, 200, 50)),
        #y, color
        Plane(0, ((50, 50, 50), (80, 80, 80)))
    ]

    render_surface = pygame.Surface((render_width, render_height))

    running = True
    while running:
        update_view(screen, render_surface, camera, objects, render_width, render_height, light)
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    moving_object.position = (moving_object.position[0] - 1, moving_object.position[1], moving_object.position[2])
                if event.key == pygame.K_RIGHT:
                    moving_object.position = (moving_object.position[0] + 1, moving_object.position[1], moving_object.position[2])
                if event.key == pygame.K_LSHIFT:
                    moving_object.position = (moving_object.position[0], moving_object.position[1] - 1, moving_object.position[2])
                if event.key == pygame.K_SPACE:
                    moving_object.position = (moving_object.position[0], moving_object.position[1] + 1, moving_object.position[2])
                if event.key == pygame.K_F1:
                    light.strength += 0.25
                if event.key == pygame.K_F2:
                    light.strength -= 0.25
                if event.key == pygame.K_UP:
                    moving_object.position = (moving_object.position[0], moving_object.position[1], moving_object.position[2] - 1)
                if event.key == pygame.K_DOWN:
                    moving_object.position = (moving_object.position[0], moving_object.position[1], moving_object.position[2] + 1)

                if event.key == pygame.K_LCTRL:
                    if moving_object == camera:
                        moving_object = light
                        print("swapped to light")
                    else:
                        moving_object = camera
                        print("swapped to camera")

    pygame.quit()

if __name__ == "__main__":
    main()
