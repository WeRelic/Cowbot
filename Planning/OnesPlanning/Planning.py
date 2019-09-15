from CowBotVector import Vec3
from GamePlan import GamePlan
import Planning.OnesPlanning.LayerZero as LayerZero
import Planning.OnesPlanning.LayerOne as LayerOne
import Planning.OnesPlanning.LayerTwo as LayerTwo


def make_plan(game_info,
              old_plan,
              old_path,
              persistent):
    '''
    The function that is currently handling decision making.  This will need to 
    split as it grows and becomes more complicated.  Takes in the plan from the previous 
    frame and the current game state and makes a new plan decision.
    Possible top-level plan states are:
    Kickoff
    Ball:
        Save
        Clear
        Shot
        Challenge
    Boost:
        Back Boost+
        Back Boost-
        Mid Boost+
        Mid Boost-
    Goal:
        Go to net
        Wait in net
        Far post
        Far Boost
        Prep for Aerial
    Recover:
        Ground
        Air
    '''

    plan = GamePlan()
    plan.path = old_path
    plan.old_plan = old_plan
    current_state = game_info.me
        
    #######################################################################
    #Layer 0
    #######################################################################

    if game_info.is_kickoff_pause:
        plan.layers[0] = "Kickoff"

    elif old_plan[0] == "Kickoff":
        plan, persistent = LayerZero.kickoff(plan, game_info, persistent)

        #######################################################################

    elif old_plan[0] == "Ball":
        plan, persistent = LayerZero.ball(plan, game_info, persistent)

        #######################################################################

    elif old_plan[0] == "Boost":
        plan, persistent = LayerZero.boost(plan, game_info, persistent)

        #######################################################################

    elif old_plan[0] == "Goal":
        plan, persistent = LayerZero.goal(plan, game_info, persistent)

    elif old_plan[0] == "Recover":
        plan, persistent = LayerZero.recover(plan, game_info, persistent)

    #######################################################################
    #Layer 1
    #######################################################################

    if plan.layers[0] == "Boost":
        plan, persistent = LayerOne.boost(plan, game_info, persistent)

        #######################################################################
        
    elif plan.layers[0] == "Ball":
        plan, persistent = LayerOne.ball(plan, game_info, persistent)

        #######################################################################
    elif plan.layers[0] == "Kickoff":
        plan, persistent = LayerOne.kickoff(plan, game_info, persistent)

        #######################################################################
    elif plan.layers[0] == "Goal":
        plan, persistent = LayerOne.goal(plan, game_info, persistent)

        #######################################################################

    elif plan.layers[0] == "Recover":
        plan, persistent = LayerOne.recover(plan, game_info, persistent)

    #######################################################################
    #Layer 2
    #######################################################################

    if plan.layers[0] == "Ball":
        plan, persistent = LayerTwo.ball(plan, game_info, persistent)

        #######################################################################


    elif plan.layers[0] == "Goal":
        plan, persistent = LayerTwo.goal(plan, game_info, persistent)

    #######################################################################


    if plan.layers != plan.old_plan:
        print(plan.layers, plan.old_plan)

    #Get ready for next frame, and return
    plan.old_plan = plan.layers
    if not plan.path_lock:
        plan.path = None

    #Return our final decision
    return plan, persistent


##############################################################

##############################################################

##############################################################



