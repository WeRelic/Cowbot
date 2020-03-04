from CowBotVector import Vec3
from GamePlan import GamePlan
import Planning.OnesPlanning.LayerZero as LayerZero
import Planning.OnesPlanning.LayerOne as LayerOne
import Planning.OnesPlanning.LayerTwo as LayerTwo
import States

def make_plan(game_info,
              old_plan,
              old_path,
              persistent):
    '''
    The function that is currently handling decision making.  This will need to 
    split as it grows and becomes more complicated.  Takes in the plan from the previous 
    frame and the current game state and makes a new plan decision.
    '''

    plan = GamePlan()
    plan.path = old_path
    plan.old_plan = old_plan
    current_state = game_info.me
        
    #######################################################################
    #Layer 0
    #######################################################################

    if game_info.is_kickoff_pause:
        plan.layers[0] = States.KickoffState.KICKOFF

    elif old_plan[0] == States.KickoffState.KICKOFF:
        plan, persistent = LayerZero.kickoff(plan, game_info, persistent)

        #######################################################################

    elif type(old_plan[0]) == States.BallState:
        plan, persistent = LayerZero.ball(plan, game_info, persistent)

        #######################################################################

    elif type(old_plan[0]) == States.BoostState:
        plan, persistent = LayerZero.boost(plan, game_info, persistent)

        #######################################################################

    elif type(old_plan[0]) == States.GoalState:
        plan, persistent = LayerZero.goal(plan, game_info, persistent)

    elif type(old_plan[0]) == States.RecoveryState:
        plan, persistent = LayerZero.recover(plan, game_info, persistent)

    #######################################################################
    #Layer 1
    #######################################################################

    if type(plan.layers[0]) == States.BoostState:
        plan, persistent = LayerOne.boost(plan, game_info, persistent)

        #######################################################################
        
    elif type(plan.layers[0]) == States.BallState:
        plan, persistent = LayerOne.ball(plan, game_info, persistent)

        #######################################################################
    elif type(plan.layers[0]) == States.KickoffState:
        plan, persistent = LayerOne.kickoff(plan, game_info, persistent)

        #######################################################################
    elif type(plan.layers[0]) == States.GoalState:
        plan, persistent = LayerOne.goal(plan, game_info, persistent)

        #######################################################################

    elif type(plan.layers[0]) == States.RecoveryState:
        plan, persistent = LayerOne.recover(plan, game_info, persistent)

    #######################################################################
    #Layer 2
    #######################################################################

    if type(plan.layers[0]) == States.BallState:
        plan, persistent = LayerTwo.ball(plan, game_info, persistent)

        #######################################################################

    elif type(plan.layers[0]) == States.GoalState:
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



