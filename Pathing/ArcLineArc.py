'''

The class for calculating and ArcLineArc path, given the parameters.

'''

from math import pi, asin, sqrt, acos

from rlbot.agents.base_agent import SimpleControllerState

from CowBotVector import *
from Miscellaneous import *
import EvilGlobals
from Pathing.Pathing import GroundPath, PathPiece


#############################################################################################

#############################################################################################

class ArcLineArc(GroundPath):

    def __init__(self,
                 start = None,
                 end = None,
                 start_tangent = None,
                 end_tangent = None,
                 radius1 = None,
                 radius2 = None,
                 current_state = None):
        '''
        Postiive radius means Clockwise
        Negative radius means Counter-clockwise
        Zero radius means no arc: the endpoint is on the line segment.
        __init__ does all the calculations for setting up the path
        '''
        #Make sure tangents aren't the zero vector
        if start_tangent.to_2d().magnitude() == 0:
            print(ValueError("start_tangent can't be length zero"))
        if end_tangent.to_2d().magnitude() == 0:
            print(ValueError("end_tangent can't be length zero"))

        self.current_state = current_state
        self.start = start.to_2d()
        self.end = end.to_2d()
        self.start_tangent = start_tangent.to_2d().normalize()
        self.end_tangent = end_tangent.to_2d().normalize()
        self.radius1 = radius1
        self.radius2 = radius2
        self.start_normal = self.start_tangent.normal_2d().normalize()
        self.end_normal = self.end_tangent.normal_2d().normalize()

        #Find the centers of the circles
        self.center1 = self.start + self.start_normal.scalar_multiply(self.radius1)
        self.center2 = self.end + self.end_normal.scalar_multiply(self.radius2)

        self.transition1 = None
        self.transition2 = None
        self.length = None
        self.is_valid = None

    
        #Signs of the radii, and the characteristic sign for the path
        #Negative if both circles are the same orientation
        #Positive if one of them is clockwise and the other is counterclockwise
        self.sgn1 = self.radius1 / abs(self.radius1)
        self.sgn2 = self.radius2 / abs(self.radius2)

        sign = - (self.sgn1 * self.sgn2)


        #Distance between the centers of the circles.
        center_separation = (self.center1 - self.center2).magnitude()

        #Find the "net radius" of the geometry.
        #This is used for checking validity, and finding transition points.
        if sign < 0:
            net_radius = abs(self.radius1) + abs(self.radius2)
        else:
            net_radius = abs(self.radius1) - abs(self.radius2)

        #Check that the path is valid
        if (self.center1 - self.center2).magnitude() < max(radius1, radius2):
            self.is_valid = False
            #print("A circle center is contained in the other circle.")
        elif ((net_radius)**2) / ((center_separation)**2) >= 0.97:
            self.is_valid = False
            self.is_valid = False
            #print("ArcLineArc Path is not valid")
        else:            
            #Find the offsets of the transition points from the centers
            e1 = (self.center2 - self.center1).normalize()
            e2 = e1.normal_2d().scalar_multiply(-self.sgn1)
            component1 = e1.scalar_multiply(net_radius / center_separation)
            component2 = e2.scalar_multiply(sqrt(1 - (net_radius / center_separation)**2))
            
            #Find transition points
            self.transition1 = self.center1 + (component1 + component2).scalar_multiply(abs(radius1))
            self.transition2 = self.center2 - (component1 + component2).scalar_multiply(sign * abs(radius2))
            
            #Find the total length of the path.
            self.length_circle1, self.length_line, self.length_circle2 = self.find_lengths()
            self.length = self.length_circle1 + self.length_line + self.length_circle2
            
            #The first segment of the path
            if self.radius1 < 0:
                direction = 1
            else:
                direction = -1
                self.piece = PathPiece(shape = "Arc",
                                       start = self.start,
                                       end = self.transition1,
                                       start_tangent = self.start_tangent,
                                       end_tangent = (self.transition1 - self.start).normalize(),
                                       direction = direction)

            #self.draw_path()


        #############################################################################################

    def find_lengths(self):
        '''
        Find the length of an ArcLineArc path.  Returns the lengths of the segments
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


    #############################################################################################

    def draw_path( self ):
        point1 = [ self.transition1.x , self.transition1.y , 50 ]
        point2 = [ self.transition2.x, self.transition2.y, 50 ]

        direction1 = self.start - self.center1
        angle1 = atan2( direction1.y , direction1.x )

        direction2 = self.transition2 - self.center2
        angle2 = atan2( direction2.y , direction2.x )

        #Draw the path to make sure we got the right one.
        EvilGlobals.renderer.begin_rendering()
        EvilGlobals.renderer.draw_line_3d(point1, point2, EvilGlobals.renderer.red())
        EvilGlobals.renderer.draw_polyline_3d( EvilGlobals.draw_arc_3d(self.center1, abs(self.radius1), angle1, - self.sgn1*self.phi1, 30), EvilGlobals.renderer.red())
        EvilGlobals.renderer.draw_polyline_3d( EvilGlobals.draw_arc_3d(self.center2, abs(self.radius2), angle2, - self.sgn2*self.phi2, 30), EvilGlobals.renderer.red() )
        EvilGlobals.renderer.end_rendering()

#############################################################################################

#############################################################################################


