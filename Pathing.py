'''

This file will hold functions for choosing which path to take.  It will be intermediate
 between Cowculate and Maneuvers.

Arc_line_arc is the first pathing we use, but could be replaced later.

'''

from math import pi, asin, sqrt, acos

from rlbot.agents.base_agent import SimpleControllerState

from CowBotVector import *
from Miscellaneous import *
import EvilGlobals
from Maneuvers import *
#############################################################################################

#############################################################################################

class GroundPath:

    def __init__(self, current_state = None):
        self.length = None
        self.time_to_traverse = None
        self.waypoints = []
        self.current_state = current_state

    def input(self):
        '''
        First attempt at following a ground path.
        For now I'll assume the path includes our starting position, 
        and the correct starting direction.
        Hopefully I'll be able to keep those decisions within path planning.
        '''

        if self.piece.shape == "Waypoint":
            return self.follow_waypoint(self.current_state)
        if self.piece.shape == "Arc":
            return self.follow_arc(self.current_state)
        elif self.piece.shape == "Line":
            return self.follow_line(self.current_state)
        else:
            return self.follow_curve(self.current_state)


    def follow_arc(self, current_state):
        controller_input = SimpleControllerState()
        controller_input.steer = self.piece.direction
        controller_input.throttle = 1 #max_throttle(self)
        
        return controller_input



    def follow_line(self, current_state):
        controller_input = SimpleControllerState()
        controller_input = GroundTurn( current_state,
                                       current_state.copy_state(pos = self.piece.end) ).input()
        
        return controller_input



    def follow_curve(self, current_state):
        controller_input = SimpleControllerState()
        return controller_input


    def follow_waypoint(self, current_state):
        controller_input = SimpleControllerState()
        controller_input = GroundTurn(current_state,
                                      current_state.copy_state(pos = self.piece.waypoint)).input()


        return controller_input





#############################################################################################

#############################################################################################

class PathPiece():
    '''
    The segment of a path that we will try to follow.
    For arcs, we specify direction = 1 for CCW, direction = -1 for CW.
    '''
    def __init__(self,
                 shape = None,
                 start = None,
                 end = None,
                 start_tangent = None,
                 end_tangent = None,
                 center = None,
                 radius = None,
                 direction = None,
                 waypoint = None):
        self.shape = shape
        self.start = start
        self.end = end
        self.start_tangent = start_tangent
        self.end_tangent = end_tangent
        self.direction = direction
        self.waypoint = waypoint


#############################################################################################

#############################################################################################


class WaypointPath(GroundPath):


    def __init__(self, waypoints, current_state = None):
        self.waypoints = waypoints
        self.current_state = current_state
        self.piece = PathPiece(shape = "Waypoint",
                               waypoint = waypoints[0])


#############################################################################################

#############################################################################################


class ArcPath(GroundPath):

    def __init__( self,
                  start = None,
                  start_tangent = None,
                  end = None,
                  end_tangent = None,
                  radius = None,
                  current_state = None):

        '''
        radius > 0 for CW, radius < 0 for CCW
        __init__ does all the calculations for setting up the path
        '''

        self.phi = None
        self.start = start.Vec3_to_2d()
        self.end = end.Vec3_to_2d()
        self.start_tangent = start_tangent.Vec3_to_2d().normalize()
        self.end_tangent = end_tangent.Vec3_to_2d().normalize()
        self.radius = radius
        self.current_state = current_state

        self.center = self.start + self.start_tangent.normal_2d().scalar_multiply(radius)

        #+1 for CCW, -1 for CW
        if ( self.start_tangent.cross(self.center - self.start) ).z > 0:
            direction = 1
        else:
            direction = -1

        self.piece = PathPiece(shape = "Arc",
                               start = self.start,
                               end = self.end,
                               direction = direction,
                               center = self.center)

        #Angle and length stuff
        center_to_end_unit_vector = (self.end - self.start).normalize()

        #The angles we travel around the circle.
        start_normal = self.start_tangent.normal_2d()
        self.phi = 2*asin(abs(start_normal.dot(center_to_end_unit_vector)))

        #Check that the angles are going around the circle the right way.
        if (center_to_end_unit_vector.dot(self.start_tangent)) < 0:
            self.phi = abs(self.phi-(2*pi))

        length_circle = self.phi * abs(self.radius)


        self.draw_path()


    def draw_path( self ):

        start_angle = atan2( (self.start - self.center).y , (self.start - self.center).x )

        #+1 for CW, -1 for CCW
        direction = - ( self.start_tangent.cross(self.end_tangent) ).normalize().z

        center_list = [ self.center.x, self.center.y, self.center.z ]
        #Draw the path to make sure we got the right one.
        EvilGlobals.renderer.begin_rendering()
        EvilGlobals.renderer.draw_polyline_3d( EvilGlobals.draw_arc_3d(self.center, self.radius, start_angle, - direction*self.phi, 60), EvilGlobals.renderer.red())
        EvilGlobals.renderer.end_rendering()

#############################################################################################

#############################################################################################


class LineArcPath(GroundPath):

    def __init__( self,
                  start = None,
                  end = None,
                  start_tangent = None,
                  end_tangent = None,
                  radius = None,
                  current_state = None):

        '''
        radius > 0 for CW, radius < 0 for CCW
        __init__ does all the calculations for setting up the path
        '''

        self.phi = None
        self.start = start.Vec3_to_2d()
        self.end = end.Vec3_to_2d()
        self.start_tangent = start_tangent
        self.end_tangent = end_tangent
        self.radius = radius
        self.current_state = current_state

        self.center = self.end + self.end_tangent.normal_2d().scalar_multiply(radius)
        self.transition = self.center - (start_tangent).Vec3_to_2d().normal_2d().scalar_multiply(radius)

        self.piece = PathPiece(shape = "Line",
                               start = self.start,
                               end = self.transition)

        #Angle and length stuff
        center_to_end_unit_vector = (self.end - self.transition).normalize()

        #The angles we travel around the circles, respectively.
        start_normal = self.start_tangent.normal_2d()
        self.phi = 2*asin(abs(start_normal.dot(center_to_end_unit_vector)))

        #Check that the angles are going around the circle the right way.
        if (center_to_end_unit_vector.dot(self.start_tangent)) < 0:
            self.phi = abs(self.phi-(2*pi))

        self.draw_path()


    def draw_path( self ):

        start_angle = atan2( (self.transition - self.center).y , (self.transition - self.center).x )

        #+1 for CW, -1 for CCW
        direction = - ( self.start_tangent.cross(self.end_tangent) ).normalize().z

        point1 = [self.start.x, self.start.y, 50]
        point2 = [self.transition.x, self.transition.y, 50]

        center_list = [ self.center.x, self.center.y, self.center.z ]
        #Draw the path to make sure we got the right one.
        EvilGlobals.renderer.begin_rendering()
        EvilGlobals.renderer.draw_line_3d(point1, point2, EvilGlobals.renderer.red())
        EvilGlobals.renderer.draw_polyline_3d( EvilGlobals.draw_arc_3d(self.center, self.radius, start_angle, - direction*self.phi, 30), EvilGlobals.renderer.red())
        EvilGlobals.renderer.end_rendering()



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
        if start_tangent.Vec3_to_2d().magnitude() == 0:
            print(ValueError("start_tangent can't be length zero"))
            return None
       

        self.phi = None
        self.start = start.Vec3_to_2d()
        self.end = end.Vec3_to_2d()
        self.start_tangent = start_tangent.Vec3_to_2d().normalize()
        self.transition1 = transition1.Vec3_to_2d()
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

        self.end_tangent = (radius_vector).Vec3_to_2d().normal_2d().normalize()

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


        self.draw_path()


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
        if start_tangent.Vec3_to_2d().magnitude() == 0:
            print(ValueError("start_tangent can't be length zero"))
        if end_tangent.Vec3_to_2d().magnitude() == 0:
            print(ValueError("end_tangent can't be length zero"))

        self.current_state = current_state
        self.start = start.Vec3_to_2d()
        self.end = end.Vec3_to_2d()
        self.start_tangent = start_tangent.Vec3_to_2d().normalize()
        self.end_tangent = end_tangent.Vec3_to_2d().normalize()
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

        #Check if the circles are too big and too close
        if (self.center1 - self.center2).magnitude() < max(radius1, radius2):
            self.is_valid = False
            #For now I'm just using one path, so I'll raise an error if it's broken
            #Eventually I might iterate over a bunch of paths, then this shouldn't happen
            raise ValueError("A circle center is contained in the other circle.")

        #Distance between the centers of the circles.
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
            #print("ArcLineArc Path is not valid")
            raise ValueError("ArcLineArc Path is not valid")

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

        self.draw_path()


        #############################################################################################

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







