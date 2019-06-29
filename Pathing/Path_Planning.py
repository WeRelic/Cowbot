'''

Decision making for setting CowBot.path

'''

from math import pi, asin, sqrt, acos

from rlbot.agents.base_agent import SimpleControllerState

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


def follow_waypoints(game_info,
                         starting_path,
                         waypoint_list,
                         waypoint_index,
                         path_following_state):
    '''
    This function will take a list of Vec3 waypoints and choose paths so that 
    the bot goes through the points in a reasonably efficient way.
    Currently, it uses GroundTurn if the next two waypoints are roughly in the same direction,
    and it uses an ArcLineArc to line up the next two waypoints if not. 
    '''

    #TODO: upgrade turning radius calculations
    turn_radius = min_radius(1410)

    #The next two waypoints we're aiming for
    current_waypoint = waypoint_list[waypoint_index]
    next_waypoint = waypoint_list[(waypoint_index + 1) % len(waypoint_list)]

    #Find the direction between them and try to guess how far off we'll be to
    #see if we need an ArcLineArc.
    #TODO: Check if we can just always use ArcLineArc, with most being small turns?
    waypoint_pair_angle = atan2(next_waypoint.y - current_waypoint.y, next_waypoint.x - current_waypoint.x)
    delta_theta = abs(rotate_to_range(game_info.me.rot.yaw - waypoint_pair_angle, [-pi,pi]))
    theta = game_info.me.rot.yaw
    start_tangent = Vec3(cos(theta), sin(theta), 0)


    if path_following_state == None and delta_theta > pi/3:
        #If we're not lined up well to go through the next two points,
        #do an ArcLineArc to be at a good angle
        #TODO: Choose between the four ArcLineArc options to minimize path length
        path_following_state = "First Arc"

        #Here we check which combination of turns is the shortest, and follow that path.
        #Later we might also check if we run into walls, the post, etc.
        #Maybe even decide based on actual strategical principles of the game o.O
        min_length = 100000
        path = WaypointPath([current_waypoint], current_state = game_info.me)
        for sign_pair in [[1,1], [1,-1], [-1,1], [-1,-1]]:
            temp_path = ArcLineArc(start = game_info.me.pos,
                                   end = current_waypoint,
                                   start_tangent = start_tangent,
                                   end_tangent = next_waypoint - current_waypoint,
                                   radius1 = sign_pair[0]*turn_radius,
                                   radius2 = sign_pair[1]*turn_radius,
                                   current_state = game_info.me)

            if not temp_path.is_valid:
                print("Invalid Path")
                continue

            if temp_path.length < min_length:
                min_length = temp_path.length
                path = temp_path


        if type(path) == WaypointPath:
            print("WARNING: No ArcLineArc path chosen")
        

        ##############################

    elif path_following_state == "First Arc":
        path = ArcLineArc(start = game_info.me.pos,
                               end = current_waypoint,
                               start_tangent = start_tangent,
                               end_tangent = next_waypoint - current_waypoint,
                               radius1 = turn_radius,
                               radius2 = turn_radius,
                               current_state = game_info.me)

        if (game_info.me.pos - path.transition1).magnitude() < 150:
            path_following_state = "Switch to Line"

        ##############################

    elif path_following_state == "Switch to Line":
        #If we're on the first frame of the line segment,
        #match everything up accoringly, then go over to normal "Line" following
        path = LineArcPath(start = game_info.me.pos,
                                start_tangent = start_tangent,
                                end = starting_path.end,
                                end_tangent = starting_path.end_tangent,
                                radius = starting_path.radius2,
                                current_state = game_info.me)
        path_following_state = "Line"

        ##############################

    elif path_following_state == "Line":
        path = LineArcPath(start = game_info.me.pos,
                                end = starting_path.end,
                                start_tangent = start_tangent,
                                end_tangent = starting_path.end_tangent,
                                radius = starting_path.radius,
                                current_state = game_info.me)

        if (game_info.me.pos - path.transition).magnitude() < 150:
            path_following_state = "Switch to Arc"

        ##############################

    elif path_following_state == "Switch to Arc":
        path = ArcPath(start = starting_path.transition,
                            start_tangent = starting_path.transition,
                            end = starting_path.end,
                            end_tangent = starting_path.end_tangent,
                            radius = starting_path.radius,
                            current_state = game_info.me)
        
        path_following_state = "Final Arc"

        ##############################

    elif path_following_state == "Final Arc":
        path = ArcPath(start = game_info.me.pos,
                            start_tangent = start_tangent,
                            end = starting_path.end,
                            end_tangent = starting_path.end_tangent,
                            radius = starting_path.radius,
                            current_state = game_info.me)
                
        if (game_info.me.pos - path.end).magnitude() < 150:
            path_following_state = None
            
            ##############################

    else:
        #If we're facing the right way and not following another path,
        #just GroundTurn towards the target
        path_following_state == None
        path = WaypointPath([current_waypoint], current_state = game_info.me)

    if (game_info.me.pos - current_waypoint).magnitude() < 150:
        waypoint_index = (waypoint_index + 1) % len(waypoint_list)

    return path, path_following_state, waypoint_index
                
