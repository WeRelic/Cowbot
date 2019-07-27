'''

Currently the final layer of planning.  
Planning only gets this far in a few branches now, but eventually this will be used more.


'''


from BallPrediction import choose_stationary_takeoff_time, get_ball_arrival, is_ball_in_scorable_box#, rendezvous_prediction



def ball(plan, game_info, persistent):
    if persistent.aerial.check:
        plan.layers[2] = "Aerial"
    elif plan.layers[1] == "Save":
        pass
    elif plan.old_plan[2] == "Hit ball":
        plan.layers[2] = "Hit ball"

    return plan, persistent


def goal(plan, game_info, persistent):
    if plan.layers[1] == "Wait in net":
        ball_arrival = get_ball_arrival(game_info, is_ball_in_scorable_box)
        if ball_arrival != None:
            plan.layers[2] = "Prep for Aerial"
            #In the current state, this will aerial for every ball.
            #TODO: Once shot/clear pathing gets implemented, that can be used here
            target_time, target_loc = ball_arrival
            if game_info.game_time > choose_stationary_takeoff_time(game_info,
                                                                    target_loc,
                                                                    target_time) - 1/10:
                if -50 < game_info.me.vel.y < 200:
                    #TODO: Deal with aerials while moving
                    plan.layers[0] = "Ball"
                    plan.layers[1] = "Clear"
                    plan.layers[2] = "Aerial"

                    persistent.aerial.check = True
                    persistent.aerial.initialize = True
                    persistent.aerial.target_location = target_loc
                    persistent.aerial.target_time = target_time
                    #TODO: Make this a general-purpose contact point function
                    #Currently works worse than just using the pre-calculated values.
                    #persistent = rendezvous_prediction(game_info, target_time, persistent)


    return plan, persistent





