'''

The class for calculating a Waypoint path, given the parameters.

'''

from math import pi, asin, sqrt, acos

from rlbot.agents.base_agent import SimpleControllerState

from CowBotVector import *
import EvilGlobals
from Maneuvers import * #Not needed?
from Miscellaneous import *
from Pathing.Pathing import GroundPath, PathPiece

#############################################################################################

#############################################################################################


class WaypointPath(GroundPath):


    def __init__(self, waypoints, current_state = None):
        self.waypoints = waypoints
        self.current_state = current_state
        self.piece = PathPiece(shape = "Waypoint",
                               waypoint = waypoints[0])
