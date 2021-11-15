# -*- coding: utf-8 -*-
"""
Created on Sun Jul 11 19:08:50 2021

@author: alexh
"""

import pandas as pd
import numpy as np

map_stats = pd.read_csv("C:/Users/alexh/OneDrive/Documents/Coding/Python/Data_science/data/match_map_stats.csv")

"""
    Here we are going to convert some of the actions we did in the previous investigation 
    into functions that can be generalised over time periods we specify as parameters.
    To start we do the same basic file cleaning.
"""

# Converting to more pandas-friendly data types

map_stats = map_stats.convert_dtypes()

# Setting the index to a datetime index to allow easy slicing

map_stats = map_stats.set_index("round_start_time")
map_stats.index = pd.DatetimeIndex(map_stats.index)

#%%

""" 
    Let's make a function that will select a set of matches based off of a time period
    (or year, or month) and an optional regular expression. 
"""

# Uncomment the below if you want a list of all of the strings available for selecting different periods of the Overwatch League
# print(map_stats["stage"].unique())

def match_selector(slice_, regex=None):
    matches = map_stats.loc[slice_]
    if regex:
        matches = matches[matches["stage"].str.contains(regex)]
    return matches

#%%

""" 
    Let's define a function that gives the league standings of data given over a certain
    time period. This will give the total wins and losses for each team, as well as the
    total number of map wins, map losses and map difference. This will be ordered with
    the most successful team at the top.
"""

def find_match_loser(x):
        winner = x["match_winner"][0]
        team_1 = x["team_one_name"][0]
        team_2 = x["team_two_name"][0]
        return team_2 if winner == team_1 else team_1

def find_map_loser(x):
        winner =  x["map_winner"][0]
        team_1 = x["team_one_name"][0]
        team_2 = x["team_two_name"][0]
        if winner == team_1:
            return team_2
        elif winner == team_2:
            return team_1
        else:
            return "draw"

def get_league_table(data):

    wins = data.groupby("match_id").apply(lambda x: x["match_winner"][0])
    losses = data.groupby("match_id").apply(find_match_loser)
    
    standings = pd.DataFrame({"Wins": wins.value_counts(), "Losses": losses.value_counts()})
    
    standings = standings.fillna(0).sort_values(by="Wins", ascending=False)
    
    """
        We now have a copy of the most basic league table that you can realistically
        create, but there are often other statistics like map difference on the table, so
        let's add that. As for whether it is worth repeating this for other seasons or
        creating functions so that it can be easily repeated for any number of seasons, I
        don't think it is worth it because this isn't the most useful information anyway.
    """
    
    map_wins = data.groupby(["match_id", "map_name"]).apply(lambda x: x["map_winner"][0])
    map_losses = data.groupby(["match_id", "map_name"]).apply(find_map_loser)
    
    combined_map_stats = pd.DataFrame({"map_wins": map_wins.value_counts(), "map_losses":
                                       map_losses.value_counts(), "map_difference":
                                       (map_wins.value_counts() -
                                        map_losses.value_counts())})
    
    standings = standings.join(combined_map_stats)
    return standings

#%%

"""
    Now let's define a function that will calculate the map type win percentage for each team for a set of input data (preprocessed by a function like match_selector) and put the result into a MultiIndex with the levels of team name and map type.
    
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
        
def find_map_type_win_percentage(data):
    map_type_seq = data.groupby(["match_id", "map_name"]).apply(find_map_type)
    map_wins = data.groupby(["match_id", "map_name"]).apply(lambda x: x["map_winner"][0])
    map_losses = data.groupby(["match_id", "map_name"]).apply(find_map_loser)
    
    map_wins_losses_types = pd.concat([map_type_seq, map_wins, map_losses], axis=1).rename(columns={0: "map_type", 1: "map_winner", 2: "map_loser"})
    
    map_type_wins_num = map_wins_losses_types.groupby(["map_winner", "map_type"]).count().rename(columns={"map_loser": "map_winner"})
    
    map_type_losses_num = map_wins_losses_types.groupby(["map_loser", "map_type"]).count().rename(columns={"map_winner": "map_loser"})
    
    map_type_percentages = ((map_type_wins_num["map_winner"] / (map_type_wins_num["map_winner"] + map_type_losses_num["map_loser"])) * 100).rename("map_percentage_win_rate")
    
    map_percentages = pd.concat([map_type_wins_num, map_type_losses_num, map_type_percentages.round(1)], axis=1).rename(columns={"map_loser": "map_winner", "map_winner": "map_loser"})
    
    #Some maps are draws so better drop those from the data
    
    return map_percentages.drop("draw")


#%%

"""
    Creating a function that will select all matches between two teams in
    their history given by the data input
"""

def pick_matches(data, team_1, team_2):
    col_1 = data.groupby(["team_one_name", "team_two_name"])
    matches = pd.concat([col_1.get_group((team_1, team_2)),
                        col_1.get_group((team_2, team_1))])
    return matches

#%%

"""Testing code"""

data_1 = match_selector("2018", regex="Overwatch League - Stage [1-4]$")
history = pick_matches(map_stats, "Los Angeles Valiant", "San Francisco Shock")
map_type_win_percentages = find_map_type_win_percentage(map_stats)
