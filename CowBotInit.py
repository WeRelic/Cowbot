def find_self_and_teams(packet, my_index, my_team):

    teammate_indices = []
    opponent_indices = []
    
    for i in range(packet.num_cars):
        if i == my_index:
            pass
        elif packet.game_cars[i].team == my_team:
            teammate_indices.append(i)
        else:
            opponent_indices.append(i)

    return teammate_indices, opponent_indices
