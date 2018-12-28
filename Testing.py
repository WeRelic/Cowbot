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
