from BallPrediction import get_ball_arrival, is_ball_in_scorable_box



def ball(plan, game_info, persistent):
    if persistent.aerial.initialize:
        plan.layers[2] = "Aerial"
    elif plan.old_plan[2] == "Aerial":
        plan.layers[2] = "Aerial"
    elif plan.layers[1] == "Save":
        pass
        #if game_info.ball.vel.magnitude() != 0 and (Vec3(cos(current_state.rot.yaw) , sin(current_state.rot.yaw), 0)).dot((game_info.ball.vel).normalize()) > pi/8:
        #plan.layers[2] = "Backwards"
    elif plan.old_plan[2] == "Hit ball":
        plan.layers[2] = "Hit ball"

    return plan, persistent

def goal(plan, game_info, persistent):
    if plan.layers[1] != None and "Wait" in plan.layers[1]:
        ball_arrival = get_ball_arrival(game_info, is_ball_in_scorable_box)
        
        if ball_arrival != None:
            if ball_arrival[1].z > 200:
                plan.layers[2] = "Prep for Aerial"

    return plan, persistent
