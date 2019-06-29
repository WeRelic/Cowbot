'''

The class for calculating a LineArcLine path, given the parameters.

'''

from math import pi, asin, sqrt, acos

from rlbot.agents.base_agent import SimpleControllerState

from CowBotVector import Vec3
from Pathing.Pathing import GroundPath, PathPiece

import EvilGlobals
#############################################################################################

#############################################################################################


class LineArcLine(GroundPath):

    def __init__( self,
                  start = None,
                  end = None,
                  start_tangent = None,
                  transition1 = None,
                  radius = None):

        '''
        radius > 0 for CW, radius < 0 for CCW
        __init__ does all the calculations for setting up the path
        '''

        #Make sure tangents aren't the zero vector
        if start_tangent.to_2d().magnitude() == 0:
            print(ValueError("start_tangent can't be length zero"))
            return None
       

        self.phi = None
        self.start = start.to_2d()
        self.end = end.to_2d()
        self.start_tangent = start_tangent.to_2d().normalize()
        self.transition1 = transition1.to_2d()
        self.radius = radius

        self.center = self.transition1 + self.start_tangent.normal_2d().scalar_multiply(radius)

        #+1 for CCW, -1 for CW
        if ( self.start_tangent.cross(self.center - self.start) ).z > 0:
            direction = 1
        else:
            direction = -1

        #geometry stuff: https://stackoverflow.com/questions/3349125/circle-circle-intersection-points
        p0 = self.center
        p1 = self.end
        d = (p1 - p0).magnitude()
        r0 = self.radius
        print((p1 - p0).dot(p1-p0) - (r0**2), (p1 - p0).dot(p1-p0), r0**2)
        r1 = sqrt((p1 - p0).dot(p1-p0) - (r0**2))

        a = ((r0**2) - (r1**2) + (d**2)) / (2*d)
        h = sqrt((r0**2) - (a**2))
        p2 = p0 + (p1-p0).scalar_multiply( a/d )
        x3 = p2.x + direction*(h/d)*(p1.y - p0.y)
        y3 = p2.y - direction*(h/d)*(p1.x - p0.x)
        p3 = Vec3(x3, y3, 0)
        radius_vector = p3 - p0

        self.end_tangent = (radius_vector).to_2d().normal_2d().normalize()

        self.transition2 = p3

        #Make sure the overdetermined conditions don't contradict
        self.is_valid = self.check_validity()

        #Find the total length of the path.
        self.length_line1, self.length_circle, self.length_line2 = self.find_lengths()
        self.length = self.length_line1 + self.length_circle + self.length_line2

        #The first segment of the path, i.e., the part we're following
        self.piece = PathPiece(shape = "Line",
                               start = self.start,
                               end = self.transition1,
                               start_tangent = self.start_tangent,
                               end_tangent = self.start_tangent)

        #self.draw_path()


        #############################################################################################

    def find_lengths(self):
        '''
        Find the legnth of an ArcLineArc path.  Returns the lengths of the segments
        in the order they're traversed.
        '''
        
        length_line1 = (self.start - self.transition1).magnitude()
        length_line2 = (self.end - self.transition2).magnitude()
                
        theta = acos(cap_magnitude(self.start_tangent.dot(self.end_tangent), 1))

        self.phi = pi - theta
        length_circle = self.phi * abs(self.radius)

        return length_line1, length_circle, length_line2

    def draw_path( self ):

        start_angle = atan2( (self.transition1 - self.center).y , (self.transition1 - self.center).x )

        #+1 for CCW, -1 for CW
        direction = ( self.start_tangent.cross(self.end_tangent) ).z

        point1 = [self.start.x, self.start.y, 50]
        point2 = [self.transition1.x, self.transition1.y, 50]
        point3 = [self.transition2.x, self.transition2.y, 50]
        point4 = [self.end.x, self.end.y, 50]

        center_list = [ self.center.x, self.center.y, self.center.z ]
        #Draw the path to make sure we got the right one.
        EvilGlobals.renderer.begin_rendering()
        EvilGlobals.renderer.draw_line_3d(point1, point2, EvilGlobals.renderer.red())
        EvilGlobals.renderer.draw_polyline_3d( EvilGlobals.draw_arc_3d(self.center, self.radius, start_angle, - direction*self.phi, 60), EvilGlobals.renderer.red())
        EvilGlobals.renderer.draw_line_3d(point3, point4, EvilGlobals.renderer.red())
        EvilGlobals.renderer.draw_rect_3d(center_list, 3, 3, True, EvilGlobals.renderer.red())
        EvilGlobals.renderer.end_rendering()


    def check_validity(self):
        return True


#############################################################################################

#############################################################################################
