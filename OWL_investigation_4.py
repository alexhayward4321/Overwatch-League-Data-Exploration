# -*- coding: utf-8 -*-
"""
Created on Wed Sep 22 16:00:17 2021

@author: alexh
"""

import numpy as np
import pandas as pd



player_stats = pd.read_csv("C:/Users/alexh/OneDrive/Documents/Coding/Python/Data_science/data/phs_2021_1.csv")

#%%

# Define functions for all of these

def get_player_stats(player, heroes="All Heroes", match_id=None, map_name=None, time=None):
    """
    Returns the statistics of a particular player, with options for which
    heroes you want data for, whether you want it for the entire league
    history, one match or several maps. There is also the option to enter a
    time period over which you want statistics for.
    
    Parameters: 
    ----------
        heroes : str or list of str
            The hero(es) you want data for (default all)
        match_id : int
            A valid match id for an Overwatch League match. If none is given
            and the two below parameters are their default, then data will be
            taken from all of OWL history.
        map_played : str
            A map played within your selected match_id
        time: timestamp, timestamp slice
            A timestamp or time period over which you want the player data.
            The two above parameters must both be None for this to work.
            
    Returns
    ------
    A dataframe with all of the specified data
    
    """
    
    if not match_id and not None:
        return player_stats.groupby("hero_name").get_group(player)
    
    if match_id and not map_name:
        return player_stats.groupby(["hero_name", "esports_match_id"])\
            .get_group((player, match_id))
    
    if match_id and map_name:
        return player_stats\
            .groupby(["hero_name", "esports_match_id", "map_name"])\
            .get_group((player, match_id, map_name))
            


players_heroes_all_stats = player_stats.groupby(["player_name", "hero_name"])

players_heroes_one_match = player_stats.groupby(["player_name", "hero_name", "esports_match_id"])

players_heroes_one_map = player_stats.groupby(["player_name", "hero_name", "esports_match_id", "map_name"])

heroes = player_stats.groupby(["hero_name"])
