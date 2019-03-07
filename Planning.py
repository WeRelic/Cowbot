def make_plan(game_info, old_plan):

    if game_info.my_team == 0:
        y_sign = 1
    else:
        y_sign = -1

    current_state = game_info.me
    if game_info.ball.vel.magnitude() != 0 and current_state.vel.magnitude() != 0:
        normalized_ball_vel = game_info.ball.vel.normalize()
        normalized_car_vel = current_state.vel.normalize()
        ball_car_dot = normalized_car_vel.dot(normalized_ball_vel)
    else:
        ball_car_dot = 0




    if game_info.is_kickoff_pause:
        if len(game_info.teammates) > 0 and game_info.teammates[0].pos.magnitude() < game_info.me.pos.magnitude() + 50:
            return check_boost_side(game_info)
        else:
            return "Kickoff"
    elif old_plan == "Kickoff":
        if y_sign*(game_info.ball.pos.y - game_info.me.pos.y) > 0:
            return "Ball"
        else:
            return check_boost_side(game_info)
    elif old_plan == "Ball" and abs(current_state.pos.y) > 5120:
        return "Goal"
    elif (old_plan == "Ball" or old_plan == "Flip into Ball") and game_info.ball.last_touch.team == game_info.my_team and (game_info.ball.hit_location - game_info.me.pos).magnitude() < 200:
        return check_boost_side(game_info)
    elif (old_plan == "Boost+" or old_plan == "Boost-") and game_info.me.boost == 100:
        return "Goal"
    elif old_plan == "Goal" and abs(game_info.me.pos.x) < 1200:
        return "Ball"
    elif (old_plan == "Ball" or old_plan == "Flip into Ball") and y_sign*(game_info.ball.pos.y - game_info.me.pos.y) < -250:
        return check_boost_side(game_info)
    elif old_plan == "Ball" and (game_info.ball.pos - current_state.pos).magnitude() < 450 - 100*ball_car_dot and game_info.ball.pos.z < 250:
        return "Flip into Ball"
    else:
        return old_plan


def check_boost_side(game_info):
    if game_info.ball.pos.x > 0:
        return "Boost-"
    else:
        return "Boost+"


