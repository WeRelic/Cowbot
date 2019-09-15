'''

Decision making for setting CowBot.path

'''

from math import pi, asin, sqrt, acos

from rlbot.agents.base_agent import SimpleControllerState
from rlutilities.mechanics import FollowPath


from CowBotVector import Vec3
from Miscellaneous import rotate_to_range, min_radius
from Pathing.ArcLineArc import ArcLineArc
from Pathing.ArcPath import ArcPath
from Pathing.LineArcLine import LineArcLine
from Pathing.LineArcPath import LineArcPath
from Pathing.WaypointPath import WaypointPath

import EvilGlobals #Only needed for rendering

#############################################################################################

#############################################################################################

def shortest_arclinearc(game_info = None,
                        index = None,
                        prediction_slice = None,
                        end_tangent = None):

    #Starting point
    start_tangent = game_info.me.rot.front
    start_location = game_info.me.pos

    #Good enough for now
    turn_radius = min_radius(1410) + 350

    #Here we check which combination of turns is the shortest, and follow that path.
    #Later we might also check if we run into walls, the post, etc.
    #Maybe even decide based on actual strategical principles of the game o.O
    min_length = 100000
    path = None
    for sign_pair in [[1,1], [1,-1], [-1,1], [-1,-1]]:
        temp_path = ArcLineArc(start = game_info.me.pos,
                               end = prediction_slice.pos,
                               start_tangent = start_tangent,
                               end_tangent = end_tangent,
                               radius1 = sign_pair[0]*turn_radius,
                               radius2 = sign_pair[1]*turn_radius,
                               current_state = game_info.me)

        if temp_path.length < min_length:
            min_length = temp_path.length
            path = temp_path

    if path == None:
        print("No path chosen!")
        return True, None, None

    else:
        if path.length / 1410 + game_info.game_time > prediction_slice.time:
            return True, None, None
        #path.draw_path()
        curve = path.to_Curve(game_info.team_sign)
        path_follower = FollowPath(game_info.utils_game.my_car)
        path_follower.path = curve
        path_follower.arrival_time = prediction_slice.time

    return False, curve, path_follower


###########################################################################################
###########################################################################################

