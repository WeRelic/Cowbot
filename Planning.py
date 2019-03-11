def make_plan(game_info, old_plan):

    #General 'keep track of my team' sign for decisions.
    if game_info.my_team == 0:
        y_sign = 1
    else:
        y_sign = -1

    #Some quantities that are used in decision making.
    current_state = game_info.me
    if game_info.ball.vel.magnitude() != 0 and current_state.vel.magnitude() != 0:
        normalized_ball_vel = game_info.ball.vel.normalize()
        normalized_car_vel = current_state.vel.normalize()
        ball_car_dot = normalized_car_vel.dot(normalized_ball_vel)
    else:
        ball_car_dot = 0
    relative_ball_position = y_sign*(game_info.ball.pos.y - game_info.me.pos.y)
    dist_from_last_touch = (game_info.ball.hit_location - game_info.me.pos).magnitude()
    first_teammate_pos = game_info.teammates[0].pos
    last_touch = game_info.ball.last_touch
    my_team = game_info.my_team
    ball_distance = (game_info.ball.pos - current_state.pos).magnitude()




    if game_info.is_kickoff_pause:
        #If it's a kickoff, and we're strictly the closest on our team, run Kickoff code.
        #If someone is at least as close as us, go get boost.
        if len(game_info.teammates) > 0 and first_teammate_pos.magnitude() < ball_distance + 50:
            return check_boost_side(game_info)
        else:
            return "Kickoff"


    elif old_plan == "Kickoff":
        #If we were doing a kickoff, but now the ball is in front of us, go for ball.
        #If the ball is behind us, go for boost.
        #I think this usually results in going for boost, since "Ball" often
        #results in us waiting in net.
        if relative_ball_position > 0:
            return "Ball"
        else:
            return check_boost_side(game_info)


    elif old_plan == "Ball" and abs(current_state.pos.y) > 5120:
        #If we were going for the ball, but now we're behind either goalline, go to goal.
        return "Goal"


    elif (old_plan == "Ball" or old_plan == "Flip into Ball") and last_touch.team == my_team and dist_from_last_touch < 200:
        #Once we touch the ball, go get boost.
        return check_boost_side(game_info)


    elif (old_plan == "Boost+" or old_plan == "Boost-") and game_current_state.boost == 100:
        #If we were going for boost, but have full boost, go to net.
        #This includes picking up the boost we wanted.
        return "Goal"



    elif old_plan == "Goal" and abs(current_state.pos.x) < 1200:
        #If we were going to goal, but now we're close to the post, go for the ball.
        return "Ball"



    elif (old_plan == "Ball" or old_plan == "Flip into Ball") and relative_ball_position < -250:
        #If we were going for the ball, but the ball is behind us, go for boost.
        return check_boost_side(game_info)


    elif old_plan == "Ball" and ball_distance < 450 - 100*ball_car_dot and game_info.ball.pos.z < 250:
        #If we were going for the ball, and we're close to it, flip into it.
        return "Flip into Ball"


    else:
        #Otherwise don't change plans.
        return old_plan




def check_boost_side(game_info):
    '''
    Choose which boost (+/- x-coordinate) to go for.  Go for the boost opposite the ball.
    '''
    if game_info.ball.pos.x > 0:
        return "Boost-"
    else:
        return "Boost+"


