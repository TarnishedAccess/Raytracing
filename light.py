import numpy as np

class Light():
    def __init__(self, position, color, strength):
        self.position = position
        self.color = np.array(color)/255
        #you really want to normalize light color into a [0,1] range otherwise it just comes out completely scuffed
        #but this also means colors don't really mix well?
        #not sure, but if there's a fix to this it's either here or in the final_color calculation. TODO
        self.strength = strength

    def calculate_direction(self, intersection_point):
        #normalization is just V = (P - L) / (|P - L|)
        vector = self.position - intersection_point 
        #np.linalg.norm(vector) is just distance (sqrt(x^2 + y^2 + z^2))
        normalized_vector = vector / np.linalg.norm(vector)
        return normalized_vector