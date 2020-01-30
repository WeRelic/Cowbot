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
                        target_time = None,
                        target_pos = None,
                        end_tangent = None):

    #Starting point
    start_tangent = game_info.me.rot.front
    start_location = game_info.me.pos

    #Good enough for now
    turn_radius = min_radius(2300) + 300#TODO: Improve using actual turn radius
    end_tangent = end_tangent.normalize()

    #Here we check which combination of turns is the shortest, and follow that path.
    min_length = 100000
    path = None
    for sign_pair in [[1,1], [1,-1], [-1,1], [-1,-1]]:
        temp_path = ArcLineArc(start = game_info.me.pos,
                               end = target_pos,
                               start_tangent = start_tangent,
                               end_tangent = end_tangent,
                               radius1 = sign_pair[0]*turn_radius,
                               radius2 = sign_pair[1]*turn_radius,#update second radius based on expected speed?
                               current_state = game_info.me,
                               team_sign = game_info.team_sign)

        if temp_path.is_valid and temp_path.length < min_length:
            min_length = temp_path.length
            path = temp_path

    if path == None:
        return True, None, None

    else:
        if path.length / 1610 + game_info.game_time > target_time: #TODO: Improve
            return True, None, None
        path.draw_path()
        RLU_path_follower = FollowPath(game_info.utils_game.my_car)
        RLU_path_follower.path = path.RLU_curve
        RLU_path_follower.arrival_time = target_time
        RLU_path_follower.arrival_speed = 1800 #TODO: Choose intelligently

    return False, path, RLU_path_follower


###########################################################################################
###########################################################################################




    







