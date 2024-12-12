import numpy as np
from ray import Ray

shadowMultiplier = 0.2

def read_object(filename):
    vertices = []
    faces = []
    normals = []

    with open(filename, 'r') as file:
        for line in file:
            if line.startswith('v'):
                vertex = tuple(float(coord) for coord in line.split()[1:])
                vertices.append(vertex)

            elif line.startswith('f'):
                face = tuple(int(index) for index in line.split()[1:])
                faces.append(face)

            elif line.startswith('n'):
                normal = tuple(float(coord) for coord in line.split()[1:])
                normals.append(normal)
                
    return vertices, faces, normals


class Triangle():
    def __init__(self, a, b, c, color, normal, reflection=0):
        self.v0 = np.array(a)
        self.v1 = np.array(b)
        self.v2 = np.array(c)
        self.color = color
        self.normal = normal
        self.reflection = reflection

    def intersect(self, ray):
        #moller trumbore algorithm
        #references:
        #https://en.wikipedia.org/wiki/M%C3%B6ller%E2%80%93Trumbore_intersection_algorithm
        #https://www.scratchapixel.com/lessons/3d-basic-rendering/ray-tracing-rendering-a-triangle/moller-trumbore-ray-triangle-intersection.html

        epsilon = 0.00001
        #haven't had any issues with floating point precision so far but if something comes up just uncomment this and any epsilon instances further below
        
        #calculate two vectors of the triangle with a shared origin. This essentially just gives us the entire thing. Third edge is redundant
        edge_vector1 = self.v1 - self.v0
        edge_vector2 = self.v2 - self.v0

        #get a vector perpendicular to both the ray and one of the edge vectors (2nd in this case). Think of the right hand rule.
        perpendicular_vector = np.cross(ray.direction, edge_vector2)

        #calculate determinant to see if the ray is parallel to the triangle
        determinant = np.dot(edge_vector1, perpendicular_vector)

        #we know that if a determinant is zero (or really close to zero in this instance to account for errors) then the ray is parallel to the triangle 
        #if abs(determinant) < 0:
        if abs(determinant) < epsilon:
            return None, None

        inverse_determinant = 1.0 / determinant

        # Vector from the triangle's first vertex to the ray's origin
        vertex_to_ray_origin = ray.origin - self.v0

        #calculate u and v. These are barycentric coordinates. essentially they go from 0 to 1, add up to 1 with 0 being inside the triangle. think of them as weights. there's a third one but again we don't care about it because two are enough. 
        #calculate u. This is the barycentric for edge_vector1
        u_parameter = inverse_determinant * np.dot(vertex_to_ray_origin, perpendicular_vector)
        if u_parameter < 0.0 or u_parameter > 1.0:
            #if its less than 0 or bigger than 1 it's outside the triangle. We don't need to go any further.
            return None, None

        #calculate v.
        cross_product_ray = np.cross(vertex_to_ray_origin, edge_vector1)
        v_parameter = inverse_determinant * np.dot(ray.direction, cross_product_ray)

        #here we make sure its actually inside the triangle.
        if v_parameter < 0.0 or u_parameter + v_parameter > 1.0:
            return None, None

        #now we know for a fact its inside the triangle and intersects. We calculate how far along the ray the intersection is.
        ray_distance = inverse_determinant * np.dot(edge_vector2, cross_product_ray)

        #if ray_distance > 0:
        if ray_distance > epsilon:
            #get the intersection point and the distance.
            intersection_point = ray.origin + ray.direction * ray_distance
            return intersection_point, ray_distance
        else:
            #if its smaller than 0 the intersection is behind the ray (aka camera) and we just don't care about it.
            return None, None

        
    def get_normal(self, intersection_point):
        return np.array(self.normal)
    
    def render(self, screen, x, y, saved_intersection_point, light, inShadow=False, new_color=None):
        #refer to the plane rendering function everything is commented there.
        normal = self.get_normal(saved_intersection_point)
        light_direction = light.calculate_direction(saved_intersection_point)
        intensity = max(0, np.dot(normal, light_direction)) * light.strength

        converted_color = np.array(self.color)
        final_color = converted_color * intensity * light.color
        if inShadow:
            final_color *= shadowMultiplier

        if new_color is not None:
            final_color = new_color
        final_color = np.clip(final_color, 0, 255)
        screen.set_at((x, y), final_color)

class Plane():
    def __init__(self, yLevel, color, reflection=0):
        self.yLevel = yLevel
        self.color = color
        self.reflection = reflection

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
    
    def render(self, screen, x, y, saved_intersection_point, light, inShadow=False, new_color=None):

        normal = self.get_normal(saved_intersection_point)
        light_direction = light.calculate_direction(saved_intersection_point)
        #light intensity is the dot product of the intersection point's normal and the light direction
        #this lets us see the angle that the light hits it at.
        #we then scale it by the light's strength
        intensity = max(0, np.dot(normal, light_direction)) * light.strength

        #If the plane only has one color, we use it.
        #Otherwise we use a checkerboard pattern
        if len(self.color) == 3:

            if new_color is not None:
                converted_color = new_color
            else:
                converted_color = np.array(self.color)

            final_color = converted_color * intensity * light.color
            if inShadow:
                final_color *= shadowMultiplier
            final_color = np.clip(final_color, 0, 255)
            screen.set_at((x, y), final_color)
        else:
            tile_size = 1.25
            if saved_intersection_point[0] < 0.5 and saved_intersection_point[0] > -0.5 and saved_intersection_point[2] < 0.5 and saved_intersection_point[2] > -0.5:
                converted_color = np.array((200, 200, 50))
                final_color = converted_color * intensity * light.color
                final_color = np.clip(final_color, 0, 255)
                screen.set_at((x, y), final_color)
            elif (saved_intersection_point[0] // tile_size + saved_intersection_point[2] // tile_size) % 2 < 1:
                converted_color = np.array(self.color[0])
                #convert the colors to an np array to handle calculations
                final_color = converted_color * intensity * light.color
                if inShadow:
                    final_color *= shadowMultiplier
                #final color is the object's color scaled by the light's intensity and affected by the light's color
                final_color = np.clip(final_color, 0, 255)
                #if any of the final color's elements exceed 255 we clamp them.
                #is this the right way of doing it? not sure. TODO
                screen.set_at((x, y), final_color)
            else:
                converted_color = np.array(self.color[1])
                final_color = converted_color * intensity * light.color
                if inShadow:
                    final_color *= shadowMultiplier
                final_color = np.clip(final_color, 0, 255)
                screen.set_at((x, y), final_color)

    def get_normal(self, intersection_point):
        #since our plane is always horizontal the normal is always (0, 1, 0)
        #probably replace this later if we get non horizontal planes
        return np.array([0, 1, 0])

class Sphere():
    def __init__(self, center, radius, color, reflection=0):
        self.center = center
        self.radius = radius
        self.color = color
        self.reflection = reflection
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
        
    def render(self, screen, x, y, saved_intersection_point, light, inShadow=False, new_color=None):
        #refer to the plane rendering function everything is commented there.
        normal = self.get_normal(saved_intersection_point)
        light_direction = light.calculate_direction(saved_intersection_point)
        intensity = max(0, np.dot(normal, light_direction)) * light.strength

        if new_color is not None:
            converted_color = new_color
        else:
            converted_color = np.array(self.color)

        final_color = converted_color * intensity * light.color
        if inShadow:
            final_color *= shadowMultiplier


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
    #sphere = Sphere(sphere_center, sphere_radius, (255, 0, 0))
    ray = Ray(origin=(0, 0, 0), direction=(1, 2, 1))
    triangle = Triangle((0, 1, -5), (4, 2, -6), (-2, 0.5, -7), (200, 25, 25))

    ray = Ray(origin=(0, 0, 0), direction=(0, 0, -1))
    triangle = Triangle((0, 1, -5), (1, -1, -5), (-1, -1, -5), (255, 100, 100))

    intersection_point = triangle.intersect(ray)

    if intersection_point is not None:
        print("Intersection Point:", intersection_point)
    else:
        print("No intersection.")

    cube_vertices, cube_faces = read_object("objects/cube.obj")
    print(cube_vertices)
    print(cube_faces)