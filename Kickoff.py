def is_kickoff(game_info, old_game_info):
    return game_info.is_kickoff_pause, old_game_info.is_kickoff_pause




def run_kickoff(game_info, old_game_info):

    current_state = game_info.me

    #Let's figure out which kickoff it is
    for spot in game_info.kickoff_dict.keys():
        if abs((current_state.pos - spot).magnitude()) < 500:
            game_info.kickoff_position = game_info.kickoff_dict[spot]
            break
        else:
            game_info.kickoff_position = "Other"
            




    
