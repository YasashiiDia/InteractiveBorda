import numpy as np
import pandas as pd


def superellipse(x, n=2, a=1, b=1, size=1):
    return b * (size**n - np.abs(x/a)**n)**(1/n)


def linear_pop_multiplier(counts, most_votes, pop_weight):
    theta = np.linspace(-1 / most_votes, 1 / most_votes, 201)[pop_weight + 100]
    b = (1 - theta * most_votes) / 2
    multipliers = theta * counts + b
    return 2 * multipliers


def elliptical_pop_multiplier(counts, most_votes, pop_weight):
    if pop_weight >= 0:  # mirror superellipse along vertical axis
        counts = counts + 2 * (most_votes // 2 - counts) + 1 + most_votes % 2

    n = np.linspace(1, 0.1, 101)[np.abs(pop_weight)]
    multipliers = superellipse(counts - 1, n=n, a=1, b=1 / most_votes,
                               size=most_votes)  # counts-1 to move superellipse upwards
    return 2 * multipliers

def tiers_to_avg_rank(vote_matrix):
    for v in vote_matrix:
        val_counts = vote_matrix[v].value_counts().sort_index()[1:] #ignore zeros
        avg_rank_of_tiers = []
        for tier, val in enumerate(val_counts):
            tier = tier+1
            avg_rank_of_tiers.append(val_counts[:tier-1].sum()+(1+val)/2)
        vote_matrix[v].replace(range(1, len(val_counts)+1), avg_rank_of_tiers, inplace=True)
    return vote_matrix


def get_list_sizes_from_vote_matrix(vote_matrix):
    """
    Needed for size-dependent Borda count
    Cannot use all_user_votes because it doesn't contain info on which lists are unranked
    """
    return vote_matrix.astype(bool).sum(axis=0)


def get_partial_rankings(vote_matrix, size_dependent=False):
    """
    Counts ballot sizes, number of ranked and unranked items,
    avg rank of unranked items (=25.5 for completely unranked list of size 50)
    """
    if size_dependent:
        size = vote_matrix.astype(bool).sum(axis=0)
    else:
        size = pd.Series([max(vote_matrix.max(axis=1)) for _ in range(len(vote_matrix.columns))], index=vote_matrix.columns)

    unranked = np.abs(vote_matrix.mask(vote_matrix>0,0).sum(axis=0))
    ranked = size - unranked
    avg_rank = 1+ranked+(unranked-1)/2
    df = pd.DataFrame([size.values,ranked.values,unranked.values,avg_rank.values],index=["Size","Ranked","Unranked","Avg_Unranked_Rank"],columns=size.index)
    df.loc["Avg_Unranked_Rank"] = df.loc["Avg_Unranked_Rank"].mask(df.loc["Unranked"]==0,0)
    #print("rounding unranked ballots")
    df.loc["Avg_Unranked_Rank"] = df.loc["Avg_Unranked_Rank"].round(0).astype(int) # rounding rank up to 26 => rounding points down to 25
    return df