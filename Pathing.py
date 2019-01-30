'''

This file will hold functions for choosing which path to take.  It will be intermediate
 between Cowculate and Maneuvers.

Arc_line_arc is the first pathing we use, but could be replaced later.

'''

from math import pi, asin, sqrt
from CowBotVector import *

#############################################################################################

#############################################################################################

class GroundPath:

    def __init__(self):
        self.length = None
        self.time_to_traverse = None
        self.waypoints = []
        
        

#############################################################################################

#############################################################################################


class ArcLineArc(GroundPath):


    def __init__(self, start, end, start_tangent, end_tangent, radius1, radius2, renderer):
        '''
        Postiive radius means Clockwise
        Negative radius means Counter-clockwise
        '''

        #Make sure we don't have zero radius on one of the circles.
        if radius1 == 0:
            raise TypeError("Radius1 can't be zero")
        if radius2 == 0:
            raise TypeError("Radius2 can't be zero")

        #make sure tangents aren't the zero vector
        if start_tangent.magnitude == 0:
            raise TypeError("start_tangent can't be length zero")
        if end_tangent.magnitude == 0:
            raise TypeError("end_tangent can't be length zero")

        self.start = start
        self.end = end
        self.start_tangent = start_tangent.normalize()
        self.end_tangent = end_tangent.normalize()
        self.radius1 = radius1
        self.radius2 = radius2

        #Signs of the radii, and the characteristic sign for the path
        #Negative if both circles are the same orientation
        #Positive if one of them is clockwise and the other is counterclockwise
        self.sgn1 = self.radius1 / abs(self.radius1)
        self.sgn2 = self.radius2 / abs(self.radius2)
        sign = - (self.sgn1 * self.sgn2)

        #Find the centers of the circles
        self.center1 = self.start + (self.start_tangent).rotate_2d(pi/2).scalar_multiply(radius1)
        self.center2 = self.end + (self.end_tangent).rotate_2d(pi/2).scalar_multiply(radius2)
        
        #Check if the circles are too big and too close
        if (self.center1 - self.center2).magnitude() < max(radius1, radius2):
            self.is_valid = False
            raise TypeError("A circle center is contained in the other circle.")

        #Disctance between the centers of the circles.
        center_separation = (self.center1 - self.center2).magnitude()

        #Find the "net radius" of the geometry.
        #This is used for checking validity, and finding transition points.
        if sign < 0:
            net_radius = abs(self.radius1) + abs(self.radius2)
        else:
            net_radius = abs(self.radius1) - abs(self.radius2)

        #Check that the path is valid
        if ((net_radius)**2) / ((center_separation)**2) < 0.97:
            self.is_valid = True
        else:
            self.is_valid = False

        #find the offsets of the transition points from the centers
        e1 = (self.center2 - self.center1).normalize()
        e2 = e1.rotate_2d(pi/2).scalar_multiply(-self.sgn1)
        component1 = e1.scalar_multiply(net_radius / center_separation)
        component2 = e2.scalar_multiply(sqrt(1 - (net_radius / center_separation)**2))

        #Find transition points
        self.transition1 = self.center1 + (component1 + component2).scalar_multiply(abs(radius1))
        self.transition2 = self.center2 + (component1 + component2).scalar_multiply(-1 * sign * abs(radius2))

        #Find the total length of the path.
        self.length_circle1, self.length_line, self.length_circle2 = self.find_lengths()
        self.length = self.length_circle1 + self.length_line + self.length_circle2

        self.draw_path(renderer)


    def find_lengths(self):
        '''
        Find the legnth of an ArcLineArc path.  Returns the lengths of the segments
        in the order they're traversed.
        '''
        
        length_line = (self.start - self.end).magnitude()
        
        #All vectors normalized here
        start_normal = (self.start - self.center1).normalize()
        end_normal = (self.end - self.center2).normalize()
        direction1 = (self.transition1 - self.start).normalize()
        direction2 = (self.end - self.transition2).normalize()
        
        #The angles we travel around the circles, respectively.
        self.phi1 = 2*asin(abs(start_normal.dot(direction1)))
        self.phi2 = 2*asin(abs(end_normal.dot(direction2)))
        
        #Check that the angles are going around the circle the right way.
        if (direction1.dot(self.start_tangent)) < 0:
            self.phi1 = abs(self.phi1-(2*pi))
        if (direction2.dot(self.end_tangent)) < 0:
            self.phi2 = abs(self.phi2-(2*pi))

        length_circle1 = self.phi1 * self.radius1
        length_circle2 = self.phi2 * self.radius2

        return length_circle1, length_line, length_circle2




    def draw_path( self, renderer ):
        point1 = [ self.transition1.x , self.transition1.y , 0 ]
        point2 = [ self.transition2.x, self.transition2.y, 0 ]

        direction1 = self.start - self.center1
        angle1 = atan2( direction1.y , direction1.x )

        direction2 = self.transition2 - self.center2
        angle2 = atan2( direction2.y , direction2.x )


        renderer.begin_rendering()
        renderer.draw_line_3d(point1, point2, renderer.red())
        renderer.draw_polyline_3d( draw_arc_3d(self.center1, abs(self.radius1), angle1, self.sgn1*self.phi1, 60), renderer.red())
        renderer.draw_polyline_3d( draw_arc_3d(self.center2, abs(self.radius2), angle2, self.sgn2*self.phi2, 60), renderer.red() )
        renderer.end_rendering()

        


def draw_circle_3d( center, radius, steps ):
    '''
    Returns a list of points for the renderer to draw a polyline in a circle
    '''

    first_point = center + Vec3(1,0,0).scalar_multiply(radius)
    locations = [ [first_point.x, first_point.y , 0] ]


    for theta in range(steps):
        next_point = center + Vec3(cos((2*pi)*(theta/steps)),sin((2*pi)*(theta/steps)),0).scalar_multiply(radius)
        locations.append([ next_point.x, next_point.y, 0 ])

    return locations



def draw_arc_3d( center, radius, start_angle, delta_angle, steps ):
    '''
    Returns a list of points for the renderer to draw a polyline in a circle
    Orientation is +1 for Counterclockwise
    Orienation is -1 for Clcokwise
    '''

    first_point = center + Vec3(cos(start_angle), sin(start_angle), 0).scalar_multiply(radius)
    locations = [ [first_point.x, first_point.y , 0] ]


    for theta in range(steps):
        next_point = center + Vec3(cos(start_angle + (delta_angle*(theta/steps))), sin(start_angle + (delta_angle*(theta/steps))),0).scalar_multiply(radius)
        locations.append([ next_point.x, next_point.y, 0 ])

    return locations







        
