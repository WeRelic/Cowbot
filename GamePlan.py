'''

    This file defines the GamePlan class.  GamePlan will be used for high level strategies, 
    storing planned paths, etc.  The GamePlan object is saved across frames in CowBot.py.
    This doesn't currently do anything, and is likely to be deprecated.  Don't add
    anything here without considering how it'll fit in.


'''


from BallPrediction import *
from Pathing import *

class GamePlan():

    def __init__(self, old_plan, game_info, old_game_info, memory):
        self.old_plan = old_plan
        self.game_info = game_info
        self.old_game_info = old_game_info
        self.memory = memory
        self.plan = None
        self.ball_prediction = make_ball_prediction(game_info.ball, game_info.fps, ('x', 0))
        self.path = self.find_path()



    def find_path(self):
        '''
        Returns the path that we're following for the moment.
        '''
        
        
        path = None #ArcLineArc( self.game_info.me.pos, self.game_info.ball.pos,
                           #self.game_info.me.vel, Vec3(0,1,0), 400, 300)



        return path




