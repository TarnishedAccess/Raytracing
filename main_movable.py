import pygame
import numpy as np
from camera import Camera
from objectHandler import Sphere, Plane, Triangle, read_object
from light import Light
from ray import Ray

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
                vector = np.array(light.position) - np.array(saved_intersection_point)
                normalized_vector = vector / np.linalg.norm(vector)
                OG_obj_light_distance = np.linalg.norm(np.array(light.position) - np.array(saved_intersection_point))
                shadow_ray = Ray(saved_intersection_point + normalized_vector * 1e-4, normalized_vector)
                obstructed = False
                for object in objects:
                    if object is not closest_object:
                        shadow_intersection_result = object.intersect(shadow_ray)
                        if shadow_intersection_result[0] is not None:
                            obj_light_distance = np.linalg.norm(np.array(light.position) - np.array(shadow_intersection_result[1]))
                            if obj_light_distance < OG_obj_light_distance and obj_light_distance > 0:
                                obstructed = True
                                break
                if obstructed:
                    closest_object.render(render_surface, x, y, saved_intersection_point, light, True)
                else:
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
    camera_position = (-7, 3, 6)
    #standard FOV is 90, quake FOV is 110, play around with it if you want, looks funny.
    fov = 90
    screen = pygame.display.set_mode((display_width, display_height))
    pygame.display.set_caption("Ray Tracing from Ouedkniss")
    camera = Camera(camera_position, render_width, render_height, fov)
    moving_object = camera
    #(x, y, z), radius
    light = Light((14, 6, 10), (255, 255, 255), 1)
    #might add multi-light support later? probably?

    cube_vertices, cube_faces, cube_normals = read_object("objects/cube.obj")

    objects = [
        #(x, y, z), radius, color
        #Sphere((0, 0, -5), 1, (200, 0, 0)),
        Sphere((-8, 0.5, -2), 1.5, (160, 32, 240)),
        Sphere((-12.5, 0.5, -1), 1.5, (200, 30, 50)),
        Sphere((-3, 0, -6), 1, (50, 200, 50)),
        #Sphere((-3, 0, 0), 1, (50, 200, 50)),
        #Triangle((-1, 0, -3), (3, 0, -7), (-1, 4, -5), (200, 25, 25)),
        #Triangle((-4, 0, -3), (-1, 4, -5), (-1, 0, -3), (25, 25, 200)),

        #y, color
        Plane(-1, ((50, 50, 50), (80, 80, 80)))
    ]

    for index in range(len(cube_faces)):
        point1 = cube_vertices[cube_faces[index][0]-1]
        point2 = cube_vertices[cube_faces[index][1]-1]
        point3 = cube_vertices[cube_faces[index][2]-1]
        normal = cube_normals[index]
        objects.append(Triangle(point1, point2, point3, (200, 50, 50), normal))

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
