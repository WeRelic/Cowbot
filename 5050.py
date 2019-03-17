'''
Here's the first attempt at getting 50/50s into code.  Ideally this will be a mechanic 
that can be called from a decision process and BAC will make a correct challenge from there.
'''


from rlbot.agents.base_agent import SimpleControllerState

from Mechanics import *





class Challenge():


    def __init__(self, game_info, opponent_index, good_direction = None, bad_direction = None):
        self.game_info = game_info
        self.current_state = game_info.me
        self.opp_state = game_info.opponents[opponent_index]
        self.ball = game_info.ball
        self.good_direction = good_direction
        self.bad_direction = bad_direction





    def input(self):

        '''
        I'm starting to think I don't have the infrastructure for this yet.
        I'll come back to it later.
        '''

        controller_state = SimpleControllerState()











        return controller_state














