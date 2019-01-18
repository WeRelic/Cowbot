from CowBotVector import *
from rlbot.agents.base_agent import SimpleControllerState
from Mechanics import *



def run_kickoff(game_info, kickoff_position):

    controller_input = SimpleControllerState()

    current_state = game_info.me

    if kickoff_position == "Far Back":
        #Boost, then jump and flip, then resume boosting.
        if current_state.vel.magnitude() < 1500:
            controller_input.boost = 1
            return controller_input
        elif current_state.wheel_contact:
            controller_input.jump = 1
            return controller_input
        elif current_state.vel.z < 300:
            return AirDodge(Vec3(1,0,0)).input()
        else:
            controller_input.boost = 1
            return controller_input
    else:
        controller_input.boost = 1
        return controller_input




def check_kickoff_position(current_state):

    kickoff_dict = {Vec3(0.0, -4608, 10): "Far Back", Vec3(0.0, 4608, 10): "Far Back", Vec3(-1952, -2464, 10): "Right", Vec3(1952, 2464, 10): "Right", Vec3(1952, -2464, 10): "Left", Vec3(-1952, 2464, 10): "Left", Vec3(-256.0, -3840, 10): "Back Right", Vec3(256.0, 3840, 10): "Back Right", Vec3(256.0, -3840, 10): "Back Left", Vec3(-256.0, 3840,10): "Back Left"}


    #Let's figure out which kickoff it is
    for spot in kickoff_dict.keys():
        if abs((current_state.pos - spot).magnitude()) < 500:
            kickoff_position = kickoff_dict[spot]
            break
        else:
            kickoff_position = "Other"


    return kickoff_position




    
