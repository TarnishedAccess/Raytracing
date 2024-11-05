import numpy as np
from ray import Ray

class Object():
    #will add support for custom objects here later, make do with spheres (and maybe cubes) for now.
    pass

class Plane():
    def __init__(self, yLevel, color):
        self.yLevel = yLevel
        self.color = color

    def intersect(self, ray):
        origin = np.array(ray.origin)
        direction = np.array(ray.direction)
        yLevel = np.array(self.yLevel)

        if direction[1] == 0:
            return None, None
        
        #t = y - o.y / d.y
        #check to make sure d.y != 0 as that's just parallel to the plane and we don't really care about it
        t = (yLevel - origin[1]) / direction[1]

        #t < 0 means ray is behind the plane. No need to render it.
        if t < 0:
            return None, None

        intersection = origin + t * direction

        return (intersection, t)
    
    def render(self, screen, x, y, saved_intersection_point, light):

        normal = self.get_normal(saved_intersection_point)
        light_direction = light.calculate_direction(saved_intersection_point)
        #light intensity is the dot product of the intersection point's normal and the light direction
        #this lets us see the angle that the light hits it at.
        #we then scale it by the light's strength
        intensity = max(0, np.dot(normal, light_direction)) * light.strength

        #If the plane only has one color, we use it.
        #Otherwise we use a checkerboard pattern
        if len(self.color) == 1:
            screen.set_at((x, y), self.color)
        else:
            tile_size = 1.25
            if (saved_intersection_point[0] // tile_size + saved_intersection_point[2] // tile_size) % 2 < 1:
                converted_color = np.array(self.color[0])
                #convert the colors to an np array to handle calculations
                final_color = converted_color * intensity * light.color
                #final color is the object's color scaled by the light's intensity and affected by the light's color
                final_color = np.clip(final_color, 0, 255)
                #if any of the final color's elements exceed 255 we clamp them.
                #is this the right way of doing it? not sure. TODO
                screen.set_at((x, y), final_color)
            else:
                converted_color = np.array(self.color[1])
                final_color = converted_color * intensity * light.color
                final_color = np.clip(final_color, 0, 255)
                screen.set_at((x, y), final_color)

    def get_normal(self, intersection_point):
        #since our plane is always horizontal the normal is always (0, 1, 0)
        #probably replace this later if we get non horizontal planes
        return np.array([0, 1, 0])

class Sphere():
    def __init__(self, center, radius, color):
        self.center = center
        self.radius = radius
        self.color = color

    def intersect(self, ray):

        #Variables:
        #O = Ray origin, Point/Vector. Ex (0, 0, 0)
        #D = Ray direction, Unit Vector. Ex (1, -1, 0.5)
        #C = Sphere Center, Point/Vector. Ex (3, 3, 2)
        #R = Sphere Radius, Number. Ex 2

        #squared(O + tD - C) = r
        #(O + tD - C) . (O + tD - C) = r²
        #Expand first half
        #(D.D)t² + 2(D.(O - C))t + (O - C).(O - C) - R² = 0
        #Rearranging for quadratic formula:
        #a = D.D
        #b = 2(D.(O - C))
        #c = (O - C).(O - C) - R²
        #Solve for t:
        #at² + bt + c = 0

        origin = np.array(ray.origin)
        direction = np.array(ray.direction)
        center = np.array(self.center)

        a = np.dot(direction, direction)
        b = 2 * np.dot(direction, (origin - center))
        c = np.dot((origin - center), (origin - center)) - self.radius**2

        delta = b**2 - 4*a*c
        if delta < 0:
            return None, None
        else:
            t1 = (-b - np.sqrt(delta)) / (2*a)
            t2 = (-b + np.sqrt(delta)) / (2*a)
            
            intersection = None
            #If there's 2 intersections we return the closest one (min distance) since the ray would stop on the first surface hit
            if t1 > 0 and t2 > 0:
                t = min(t1, t2)
            elif t1 > 0:
                t = t1
            else:
                t = t2

            #plug t into the ray equation to find the intersection point and return it
            intersection = origin + direction * t
            return (intersection, t)
        
    def render(self, screen, x, y, saved_intersection_point, light):
        #refer to the plane rendering function everything is commented there.
        normal = self.get_normal(saved_intersection_point)
        light_direction = light.calculate_direction(saved_intersection_point)
        intensity = max(0, np.dot(normal, light_direction)) * light.strength

        converted_color = np.array(self.color)
        final_color = converted_color * intensity * light.color
        final_color = np.clip(final_color, 0, 255)
        screen.set_at((x, y), final_color)

    def get_normal(self, intersection_point):
        #a sphere's normal vector is just the vector from the center to the intersection point going outside.
        vector = np.array(intersection_point) - np.array(self.center)
        normalized_vector = vector / np.linalg.norm(vector)
        return normalized_vector
            
#simple test to check if the intersection works
if __name__ == "__main__":
    ray_origin = (0, 0, 0)
    ray_direction = (1, 2, 1)
    sphere_center = (3, 3, 3)
    sphere_radius = 2

    #i should probably just make direction normalization a function but this works for now
    #TODO?
    ray_direction_normalized = ray_direction / np.linalg.norm(ray_direction)

    ray = Ray(ray_origin, ray_direction_normalized)
    sphere = Sphere(sphere_center, sphere_radius, (255, 0, 0))

    intersection_point = sphere.intersect(ray)

    if intersection_point is not None:
        print("Intersection Point:", intersection_point)
    else:
        print("No intersection.")