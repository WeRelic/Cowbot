import rlbot.utils.game_state_util as framework

def Vec3_to_Vector3(vector):
    return framework.Vector3(x = vector.x, y = vector.y, z = vector.z)

def rot_to_Rotator(rot):
    return framework.Rotator(rot[0], rot[1], rot[2])


def set_state(game_info,
              ball_state = None,
              current_state = None,
              teammates_state = None,
              opponents_state = None,
              boosts_state = None,
              game_info_state = None):

    '''
    This will set the game state as specified.  Most of the code is translating between different state objects.
    game_info is passed solely for the indices of each car, because I have no way of knowing that a priori.
    Seeing as it's unlikely I'll want to mess with boost pads anytime soon, I'm skipping that for now.
    game_info is a GameState object (from CowBot code). 
    ball_state is a BallState object (from CowBot code).
    current_state is a CarState object (from CowBot code).
    teammates_state is a list of CarState objects (from CowBot code).
    opponents_state is a list of CarState objects (from CowBot code).
    boosts_state is currently skipped and should always be None.
    game_info_state is also currently skipped and should be None.
    '''

    new_ball_state = None
    cars_state = None
    boosts_state = None
    game_info_state = None

    #Ball first.
    if ball_state != None:
        new_ball_state = framework.BallState(framework.Physics(location = Vec3_to_Vector3(ball_state.pos),
                                                               rotation = rot_to_Rotator(ball_state.rot),
                                                               velocity = Vec3_to_Vector3(ball_state.vel),
                                                               angular_velocity = Vec3_to_Vector3(ball_state.omega)))

    #Cars
    new_cars_state = {}

    #My car
    if current_state != None:
        my_car = framework.CarState(framework.Physics(location = Vec3_to_Vector3(current_state.pos),
                                                      rotation = rot_to_Rotator(current_state.rot),
                                                      velocity = Vec3_to_Vector3(current_state.vel),
                                                      angular_velocity = Vec3_to_Vector3(current_state.omega)),
                                    boost_amount = current_state.boost,
                                    jumped = current_state.jumped,
                                    double_jumped = current_state.double_jumped)

        cars[game_info.my_index] = my_car

    #Teammates' cars
    if teammates_state != None:
        for i in range(len(teammates_state)):
            teammate_state = framework.CarState(framework.Physics(location = Vec3_to_Vector3(game_info.teammates[i].pos),
                                                                  rotation = rot_to_Rotator(game_info.teammates[i].rot),
                                                                  velocity = Vec3_to_Vector3(game_info.teammates[i].vel),
                                                                  angular_velocity = Vec3_to_Vector3(game_info.teammates[i].omega)),
                                                boost_amount = game_info.teammates[i].boost,
                                                jumped = game_info.teammates[i].jumped,
                                                double_jumped = game_info.teammates[i].double_jumped)

            new_cars_state[game_info.teammates[i].index] = teammate_state

    #Opponents' cars
    if opponents_state != None:
        for i in range(len(opponents_state)):
            opponent_state = framework.CarState(framework.Physics(location = Vec3_to_Vector3(game_info.opponents[i].pos),
                                                                  rotation = rot_to_Rotator(game_info.opponents[i].rot),
                                                                  velocity = Vec3_to_Vector3(game_info.opponents[i].vel),
                                                                  angular_velocity = Vec3_to_Vector3(game_info.opponents[i].omega)),
                                                boost_amount = game_info.opponents[i].boost,
                                                jumped = game_info.opponents[i].jumped,
                                                double_jumped = game_info.opponents[i].double_jumped)
            
            new_cars_state[game_info.opponents[i].index] = opponent_state
            
            
    #Skipping boosts_state setting for now.  Maybe will add later.
            
    #Skipping game_info_state for now.  Maybe will add later.
            
    
    #Put it all together and set the state.
    game_state = framework.GameState(ball = new_ball_state,
                                     cars = cars_state,
                                     boosts = boosts_state,
                                     game_info = game_info_state)

    return game_state
