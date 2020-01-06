from CowBotVector import Vec3
import Kickoffs.Default_Kickoffs
import Kickoffs.Fast_Kickoffs

def update_kickoff_position(game_info, kickoff_position):
    '''
    Returns the current kickoff position.
    Gives "Other" except from the frame the countdown ends until either the ball is hit.
    During this time it returns the position the bot starts in for the kickoff.
    Eventually this will be map specific.  Currently only the standard pool.
    '''

    #if the kickoff has just started, update the position.k
    if game_info.is_kickoff_pause and kickoff_position == "Other":
        kickoff_position = check_kickoff_position(game_info.me)

        #If the ball has just moved, reset the kickoff position.
    elif kickoff_position != "Other" and not game_info.is_kickoff_pause:
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


#########################################################################################################

#########################################################################################################

#########################################################################################################


class Kickoff():

    def __init__(self,
                 game_info,
                 kickoff_position,
                 memory,
                 persistent):
        self.position = kickoff_position
        self.memory = memory
        self.current_state = game_info.me
        self.game_info = game_info

        self.persistent = persistent


    def input(self):


        #Check left or right, and set the sign to keep track.
        #Right means +1, Left means -1.
        if self.position == "Right" or self.position == "Back Right":
            x_sign = 1
        elif self.position == "Left" or self.position == "Back Left":
            x_sign = -1

        if self.position == "Far Back":
            #Run the straight kickoff
            controller_input = Kickoffs.Default_Kickoffs.far_back(self.game_info,
                                                                  self.persistent)

        elif self.position == "Back Left" or self.position == "Back Right":
            #Run the offcenter kickoff
            controller_input, persistent = Kickoffs.Fast_Kickoffs.offcenter(self.game_info,
                                                                            x_sign,
                                                                            self.persistent)

            
        elif self.position == "Right" or self.position == "Left":
            #Run the diagonal kickoff
            controller_input, self.persistent = Kickoffs.Fast_Kickoffs.diagonal(self.game_info,
                                                                                x_sign,
                                                                                self.persistent)

        return controller_input, self.persistent


