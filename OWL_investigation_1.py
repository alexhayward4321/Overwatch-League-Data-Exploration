# -*- coding: utf-8 -*-
"""
Created on Sun Jul 11 19:08:50 2021

@author: alexh
"""

import pandas as pd
import numpy as np

map_stats = pd.read_csv("C:/Users/alexh/OneDrive/Documents/Coding/Python/Data_science/data/match_map_stats.csv")

player_stats = pd.read_csv("C:/Users/alexh/OneDrive/Documents/Coding/Python/Data_science/data/phs_2021_1.csv")

"""
We'll start with manipulating map statistics. This first script is only to really
get a feel of the data and practice my data manipulation. We'll generalise
some of the data manipulation techniques into functions in future scripts.

"""

# Converting to more pandas-friendly data types 

map_stats = map_stats.convert_dtypes()

# Setting the index to a datetime index to allow easy slicing

map_stats = map_stats.set_index("round_start_time")
map_stats.index = pd.DatetimeIndex(map_stats.index)

# Separating data into different seasons

map_stats_2018 = map_stats.loc["2018"]

map_stats_2019 = map_stats.loc["2019"]

map_stats_2020 = map_stats.loc["2020"]

map_stats_2021 = map_stats.loc["2021"]

#%%

""" Let's work with 2018 stats first just for simplicity. To find the regular season standings, we need to exclude the data from the tournaments using a regular expression

"""

map_stats_2018_regular = map_stats_2018[map_stats_2018["stage"].str.contains(r"Overwatch League - Stage [1-4]$")]

""" Now to find the number of wins and losses each team took, because of the way the data is arranged, we need to first group the data by the individual match, then take the winner from that match

"""

wins_2018 = map_stats_2018_regular.groupby("match_id").apply(lambda x: x["match_winner"].unique()[0])

def find_loser(x):
    winner = x["match_winner"].unique()[0]
    team_1 = x["team_one_name"].unique()[0]
    team_2 = x["team_two_name"].unique()[0]
    return team_2 if winner == team_1 else team_1
    

losses_2018 = map_stats_2018_regular.groupby("match_id").apply(find_loser)

regular_season_standings_2018 = pd.DataFrame({"Wins": wins_2018.value_counts(), "Losses": losses_2018.value_counts()})

regular_season_standings_2018 = regular_season_standings_2018.fillna(0).sort_values(by="Wins", ascending=False)

"""
    We now have a copy of the most basic league table that you can realistically create, but there are often other statistics like map difference on the table, so let's add that. As for whether it is worth repeating this for other seasons or creating functions so that it can be easily repeated for any number of seasons, I don't think it is worth it because this isn't the most useful information anyway.
"""

map_wins_2018_regular = map_stats_2018_regular.groupby(["match_id", "map_name"]).apply(lambda x: x["map_winner"].unique()[0])

def find_map_loser(x):
    winner = x["map_winner"].unique()[0]
    team_1 = x["team_one_name"].unique()[0]
    team_2 = x["team_two_name"].unique()[0]
    if winner == team_1:
        return team_2
    elif winner == team_2:
        return team_1
    else:
        return "draw"

map_losses_2018_regular = map_stats_2018_regular.groupby(["match_id", "map_name"]).apply(find_map_loser)

combined_map_stats = pd.DataFrame({"map_wins": map_wins_2018_regular.value_counts(), "map_losses": map_losses_2018_regular.value_counts(), "map_difference": (map_wins_2018_regular.value_counts() - map_losses_2018_regular.value_counts())})

regular_season_standings_2018 = regular_season_standings_2018.join(combined_map_stats)


#%%

"""
    Now let's calculate the map type win percentage for each team over the 2018 season and put the result into a MultiIndex with the levels of team name and map type.
    
"""

def find_map_type(x):
    if x["control_round_name"].notna().any():
        return "Control"
    elif x["map_name"].isin(["Temple of Anubis", "Horizon Lunar Colony", "Hanamura", "Volskaya Industries", "Paris", ]).all():
        return "Assault"
    elif x["map_name"].isin(["King's Row", "Blizzard World", "Numbani", "Eichenwalde", "Hollywood"]).all():
        return "Hybrid"
    elif x["map_name"].isin(["Watchpoint: Gibraltar", "Dorado", "Junkertown", "Route 66", "Rialto", "Havana"]).all():
        return "Escort"
        
   
map_types_2018_regular = map_stats_2018_regular.groupby(["match_id", "map_name"]).apply(find_map_type)

map_wins_losses_types = pd.concat([map_types_2018_regular, map_wins_2018_regular, map_losses_2018_regular], axis=1).rename(columns={0: "map_type", 1: "map_winner", 2: "map_loser"})

map_type_wins_num_2018 = map_wins_losses_types.groupby(["map_winner", "map_type"]).count().rename(columns={"map_loser": "map_winner"})

map_type_losses_num_2018 = map_wins_losses_types.groupby(["map_loser", "map_type"]).count().rename(columns={"map_winner": "map_loser"})

map_type_percentages = ((map_type_wins_num_2018["map_winner"] / (map_type_wins_num_2018["map_winner"] + map_type_losses_num_2018["map_loser"])) * 100).rename("map_percentage_win_rate")

map_percentages_2018_regular = pd.concat([map_type_wins_num_2018, map_type_losses_num_2018, map_type_percentages], axis=1).rename(columns={"map_loser": "map_winner", "map_winner": "map_loser"})
