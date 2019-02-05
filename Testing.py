from GameState import *
from CowBotVector import *


def find_position(game_info):
    '''
    Print the location of the opposing car (human control, in practice)
    when it jumps.  Set up a 1v1 with car 0 BAC and car 1 human control.
    '''
    if game_info.opponents[0].pos.z > 100:
        print(game_info.opponents[0].pos)


def find_rotation(game_info):
    '''
    Print the rotation of the opposing car (human control, in practice)
    when it jumps.  Set up a 1v1 with car 0 BAC and car 1 human control.
    '''
    if game_info.opponents[0].pos.z > 100:
        print(game_info.opponents[0].rot)




def draw_debug(car, ball, ball_prediction, action_display = None):
    renderer.begin_rendering()
    #Draw the expected path of the ball
    #The time is wrong, but not used here right now
    ball_path = renderer_ball_prediction(ball)
    renderer.draw_polyline_3d(ball_path, renderer.white())
    if ball_prediction != None:
        renderer.draw_rect_3d( [ball_prediction.x, ball_prediction.y, ball_prediction.z], 90, 90, True, renderer.red() )
    # display the action that the bot is taking
    #renderer.draw_string_3d(car.physics.location, 2, 2, action_display, renderer.white())
    renderer.end_rendering()
