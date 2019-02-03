from CowBotVector import *
from rlbot.agents.base_agent import SimpleControllerState
from Mechanics import *
from BallPrediction import *






class Kickoff():

    def __init__(self, game_info, kickoff_position, memory):
        self.position = kickoff_position
        self.memory = memory
        self.game_info = game_info



        
    def input(self):

        controller_input = SimpleControllerState()

        current_state = self.game_info.me

        if self.position == "Far Back":
            #Boost, then jump and flip, then resume boosting.
            if current_state.vel.magnitude() < 1500:
                controller_input.boost = 1
                return controller_input
            elif current_state.wheel_contact:
                controller_input.jump = 1
                return controller_input
            elif current_state.vel.z < 300:
                return AirDodge(Vec3(1,0,0), game_info.me.jumped_last_frame).input()
            else:
                controller_input.boost = 1
                return controller_input
        else:
            controller_input.boost = 1
            return controller_input



def update_kickoff_position(game_info, kickoff_position):
        '''
        Returns the current kickoff position.
        Gives "Other" except from the frame the countdown ends until either the ball is hit.
        During this time it returns the position the bot starts in for the kickoff.
        Eventually this will be map specific.  Currently only the standard pool.
        '''

        #if the kickoff has just started, update the position.
        if game_info.is_kickoff_pause and kickoff_position == "Other":
            kickoff_position = check_kickoff_position(game_info.me)

        #If the ball has just moved, reset the kickoff position.
        elif kickoff_position != "Other" and game_info.is_kickoff_pause > 0:
            kickoff_position = "Other"
        return kickoff_position


def check_kickoff_position(current_state):
    '''
    Returns a string encoding which starting position we have for kickoff.
    This only works for "mostly standard" maps.  I'll worry about the others later.
    '''

    kickoff_dict = {Vec3(0.0, -4608, 10): "Far Back", Vec3(0.0, 4608, 10): "Far Back", Vec3(-1952, -2464, 10): "Right", Vec3(1952, 2464, 10): "Right", Vec3(1952, -2464, 10): "Left", Vec3(-1952, 2464, 10): "Left", Vec3(-256.0, -3840, 10): "Back Right", Vec3(256.0, 3840, 10): "Back Right", Vec3(256.0, -3840, 10): "Back Left", Vec3(-256.0, 3840,10): "Back Left"}


    #Let's figure out which kickoff it is
    for spot in kickoff_dict.keys():
        if abs((current_state.pos - spot).magnitude()) < 500:
            kickoff_position = kickoff_dict[spot]
            break
        else:
            kickoff_position = "Other"


    return kickoff_position
