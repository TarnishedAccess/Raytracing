import pygame
from camera import Camera
from objectHandler import Sphere

def main():
    pygame.init()

    screen_width = 800
    screen_height = 600
    camera_position = (0, 0, 0)
    #standard FOV is 90, quake FOB is 110, play around with it if you want, looks funny.
    fov = 90
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("Ray Tracing from Ouedkniss")

    camera = Camera(camera_position, screen_width, screen_height, fov)
    #(x, y, z), radius
    sphere = Sphere((0, 0, -5), 1)
    #black background, will probably replace with a floor/skybox or something later
    background_color = (0, 0, 0)
    screen.fill(background_color)

    for y in range(screen_height):
        for x in range(screen_width):
            ray = camera.castRay(x, y)
            intersection_point = sphere.intersect(ray)
            #will probably refactor intersection detection later on so that it's based on the ray rather than the object. I think it'd be better that way?
            #TODO
            if intersection_point is not None:
                #would be easy to add color, just give the objects a color attribute and use it here
                #TODO
                color = (255, 255, 255)
                screen.set_at((x, y), color)

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