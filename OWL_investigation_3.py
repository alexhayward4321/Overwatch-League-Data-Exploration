# -*- coding: utf-8 -*-
"""
Created on Sun Jul 18 18:52:50 2021

@author: alexh
"""

import numpy as np
import pandas as pd

"""
    Let's play around a bit with player stats now.
    
    Objectives: write a function that will
    
    - Return key stats about a certain player on a certain hero
    - 
    - 
"""

player_stats = pd.read_csv("C:/Users/alexh/OneDrive/Documents/Coding/Python/Data_science/data/phs_2021_1.csv")


players_heroes_all_stats = player_stats.groupby(["player_name", "hero_name"])

players_heroes_one_match = player_stats.groupby(["player_name", "hero_name", "esports_match_id"])

players_heroes_one_map = player_stats.groupby(["player_name", "hero_name", "esports_match_id", "map_name"])

heroes = player_stats.groupby(["hero_name"])

#%%

"""With this function I want to rearrange the dataframe 'Mei' below so that I can compare players by their stats on an average basis. Eventually I'll write a function that can do this fresh from the heroes groupby"""

Mei = heroes.get_group("Mei").drop(["start_time", "tournament_title", "map_type", "team_name", "hero_name"], axis=1)

# This data is actually a bit messy

print("Check to see if there are na values in any of the columns: \n\n", Mei.isna().any(), sep="")
print("\nCount of na values in stat_amount column: ", Mei["stat_name"].isna().sum())

# Cleaning it a bit

Mei = Mei.dropna()

Mei = Mei.set_index(["player_name", "esports_match_id", "map_name", "stat_name"])

# Counting duplicates

duplicates = Mei.index.duplicated()

print("Number of duplicates in index: ", duplicates.sum())

print("\nIt appears that the self-healing column for Mei consistently duplicates for some reason, but we can simply remove this")

Mei = Mei[~Mei.index.duplicated()]

# Now we can start to rearrange this into a more convenient form

Mei = Mei.unstack()

Mei = Mei.droplevel(level=0, axis=1)

#%%

# Players that have only played for a very short time on each hero often massively skew the stats so I will somewhat arbitrarily eliminate all of the players which have less than 10 minutes played on Mei over the course of the season and see if there are any skews remaining.

Mei_times = Mei.groupby("player_name")["Time Played"].sum()

valid_players = Mei_times[Mei_times > 600]

valid_players_list = Mei.index.to_frame().drop(["esports_match_id", "map_name"], axis=1)

what = valid_players_list.isin(valid_players.index)

Mei = Mei[what["player_name"]]

#%%

# Now that we have our data in a nice neat form, we can start to compare players, aggregate data and find out maximum and minimum values for different stats. 

"""
    Initially I used very basic data processing operations across all columns to try and produce informative and interesting information, however different statistics only give meaning to a different player's performance under different circumstances. The only general rule across all statistics seems to be an average over time: final blows per ten, damage per ten, deaths per ten etc. But certain statisics like average time alive, weapon accuracy, self healing percent of damage taken and average time alive aren't really useful or accurate if averaged in such a basic way as using the .mean() method.

    Sometimes there are statistics which you would like to know over the course of over a single match, which is where most often you want to see just the bare statistic without averaging, but for now we'll ignore such cases and pass them onto a later function. We don't need to actually average all of the statistics though, some of these aren't very useful like barrier damage done, self healing percent of damage taken, shots fired, time hacked, turrets destroyed etc. They are the kind of thing we may want to see eventually, and there is no harm in processing and then recombining that data as well I suppose.

    Below is a list of data where it may be desirable to know what that statistic is per 10 minutes
    
    - Damage done
    - Assists
    - Barrier Damage Done
    - Blizzard Kills
    - Critical Hits
    - Damage - Blizzard
    - Damage - Weapon primary
    - Damage - Weapon Secondary
    - Damage Blocked
    - Damage Taken
    - Deaths
    - Eliminations
    - Enemies frozen
    .
    .
    .
    
    At this rate it is probably easier to list the statistics that aren't useful to know on a per 10 minute basis.
    
    - Average Time Alive
    - Blizzard Efficiency
    - Critical hit accuracy
    - Self healing percent of damage taken
    - Time building ultimate
    - Time Elapsed per ultimate earned
    - Time Hacked
    - Time played
    .
    .
    .
    
Again, at this rate now much is happening quickly, and a lot of these statistics are somewhat useless in comparing Mei players. The problem is, there are a lot of statistics that could potentially be of use or interesting to know like successful freezes, but such statistics obviously don't hold across multiple heroes so it would be very annoying to try and generalise across all of those heroes in a function, in fact, let's try and find out what statistics are constant across all heroes.
    
"""

def stats_per_hero(hero):
    return pd.Index(player_stats.groupby("hero_name").get_group(hero)["stat_name"].unique()).dropna()

common = stats_per_hero("Mei").intersection(stats_per_hero("Reaper").intersection(stats_per_hero("McCree")))

"""
    That's 37 statistics in all still, but the fact remains that only some of these are things you would want to compare between certain heroes. The question that I am asking here is what functions do I want to define? Is it that I would like to  have a rank of all possible statistics of a particular hero for all players? Or is that I want a function that only takes the most important ones. Not only do I want a rank for different heroes of course, but I would also like to access the numbers of their specific statistics individual to them. I think it would be good to have a function that gives you all of the most significant statistics you are likely to care about per player role; that is, damage, tank and healer. The fact is that there are too many individually relevant statistics per hero to generalise into a single function, so I will need to define an individual funtion or two to examine those other significant statistics. The aim of getting a good ranking along every statistics for each hero is an achievable one, but it is highly unlikely to be particularly useful and not worth the effort to implement.
    
Now I need to find the most relevant stats for each role:
"""

def find_role_stats(hero_list):
    common_stats = stats_per_hero(hero_list[0])
    for i in range(1, len(hero_list)):
        common_stats = common_stats.intersection(stats_per_hero(hero_list[i]))
    return common_stats

all_heroes_list = player_stats["hero_name"].unique()

dps_list = ["Echo", "Mei", "Reaper", "Sombra", "Symmetra", "Doomfist", "Tracer", "Ashe", "McCree", "Hanzo", "Pharah", "Widowmaker", "Genji", "Soldier: 76", "Junkrat", "Bastion", "Torbjörn"]
                     
tank_list = ["Reinhardt", "Winston", "Wrecking Ball", "D.Va", "Sigma", "Zarya", "Orisa", "Roadhog"]

support_list = ["Ana", "Baptiste", "Moira", "Brigitte", "Lúcio", "Zenyatta", "Mercy"] 

#%%

# Intersection is apparently quite a computationally complex operation it seems (unless my functions were written completely inefficiently), so it's best only to need to run this cell once.

dps_stats_long = find_role_stats(dps_list)

tank_stats_long = find_role_stats(tank_list)

support_stats_long = find_role_stats(support_list)

#%%

# Here are all of the differences between each stats list for each role:
    
print(dps_stats_long.difference(tank_stats_long))
print(dps_stats_long.difference(support_stats_long))

print(tank_stats_long.difference(dps_stats_long))
print(tank_stats_long.difference(support_stats_long))

print(support_stats_long.difference(dps_stats_long))
print(support_stats_long.difference(tank_stats_long))

"""
    I have found some problems with taking this approach. Firstly, that the statistics that vary in between each role do not matter very much. The only two that do are Healing done and Defensive assists for support. There is not much value that has been added by finding all of the statistics common to all of each role. For example, for tanks that use barriers, otherwise known as main tanks, the amount of damage blocked is quite a significant statistic, but sometimes main tanks flex to off tank to play wrecking ball which doesn't block damage, so it would be strange to define a different category for main tank that includes barrier damage than what you actually see in the game. In addition, symmetra is a dps that does not offer the possibility for critical hits, so the dps_stats_long variable does not include that stat that is interesting for multiple dps, especially hitscan. I think what I am going to do is define a function for dps and tank, then one for healer which includes healing and defensive assists, but then define functions that offer additional data for hitscan dps or another category, as well as another function that will simply take the stat that you would like to add to your hero data and then just add that particular stat - which would be useful for heroes like Ana where sleep darts are important, Roadhog where hook accuracy is important, emp charge time which for Sombra is very important etc. If I get very invested into this project I could eventually come up with individualised data sets for each hero, but that should be after I complete all the major stuff that would allow me to try and use machine learning to do more interesting things with data
"""

#%%

"""
Here are the most key general stats for a dps or tank player in my opinion:
    
    - Hero damage done
    - Final Blows
    - Eliminations
    - Time Building ultimate
    - Deaths
    - Solo kills

Then a separate function for each of these per 10.

As for supports:
    
    - Hero damage done
    - Final Blows
    - Eliminations
    - Time Building ultimate
    - Deaths
    - Solo kills
    - Healing done

Then again a separate function for each of these per 10.

For the lists that are not per 10, these are likely only to be collected on a per match or map basis, so this isn't that useful for comparing players against each other. The only stats that people care about when it comes to the total number over the course of a very long period of time are: total damage, total final blows, total eliminations. That's only really for comparing people who have been in the league for a very long time and are comparing back over several seasons of data, like for Profit and Carpe for example.

At this point though, just to tidy up all of the mess and now that I have a plan in place, I'm going to start a new page where I am going to implement all of these functions.
"""



#%%












# Let's aggregate all of the data for each player into a mean statistic

Means = Mei.groupby("player_name").mean()

# Now let's drop all of the data for which a mean statistic is not useful

Means["Damage Per Ten"] = Means["All Damage Done"] / Means["Time Played"] * 60

# I have realised that it might be useful to have a function or just a variable that tells you all of the stats available for each hero, so that you can select what data you are interested in



# Now let's do the challenge of ranking every single player relative to all the others for every stat.

Means_rank = Means.rank(ascending=False)
