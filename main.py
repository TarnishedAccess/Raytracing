import pygame
import numpy as np
from camera import Camera
from objectHandler import Sphere, Plane, Triangle, read_object
from light import Light
from ray import Ray

def main():
    pygame.init()

    screen_width = 400
    screen_height = 300
    #camera_position = (0, 1, 3)
    camera_position = (-7, 3, 6)

    #standard FOV is 90, quake FOB is 110, play around with it if you want, looks funny.
    fov = 90
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("Ray Tracing from Ouedkniss")

    camera = Camera(camera_position, screen_width, screen_height, fov)

    light = Light((14, 6, 10), (255, 255, 255), 1)
    #might add multi-light support later? probably?

    cube_vertices, cube_faces, cube_normals = read_object("objects/cube.obj")

    objects = [
        #(x, y, z), radius, color
        #Sphere((0, 1, -5), 1, (200, 0, 0)),
        Sphere((-7, 0.5, -2), 1.5, (160, 32, 240)),
        Sphere((-12.5, 0.5, -1), 1.5, (200, 30, 50)),
        Sphere((-3, 0, -6), 1, (50, 200, 50)),
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
                
                #if the shadow ray could not successfully make it to the light source we color the pixel black, otherwise we proceed as usual.
                if obstructed:
                    closest_object.render(screen, x, y, saved_intersection_point, light, True)
                else:
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