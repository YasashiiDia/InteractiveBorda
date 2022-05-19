import numpy as np
import pandas as pd
import streamlit as st

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


def get_votes_df_from_vote_matrix(vote_matrix):
  all_user_votes = []
  for v in vote_matrix:
    all_user_votes.append(pd.Series(vote_matrix[v][vote_matrix[v] > 0].sort_values().index.get_level_values(level="Title"), name=v))
  return pd.concat(all_user_votes, axis=1)


def voter_corr(vmc, all_user_votes, voter):
    c = vmc[voter].sort_values(ascending=False)
    col_arrays = [all_user_votes[c.index].columns, c.values.round(2)]
    multi_cols = pd.MultiIndex.from_arrays(col_arrays, names=["Voter", "Correlation"])
    votes = all_user_votes[c.index].values
    results = pd.DataFrame(votes, index=range(1, len(all_user_votes) + 1), columns=multi_cols, copy=True)
    #results.index.name = "Rank"
    return results


def get_ranked_vote_matrix(vote_matrix):
    vote_matrix = vote_matrix.mask(vote_matrix < 0, 1)  # fix unranked ballots
    ranked_vote_matrix = tiers_to_avg_rank(vote_matrix)
    return ranked_vote_matrix


def print_df(df, round_score=False, mode="title"):
    for i in df.index:
        # diff = a.loc[i,'Diff.']
        # if diff > 0: color = "green"
        # elif diff == 0: color = "blue"
        # else: color = "red"
        title = df.loc[i,"Title"] if mode == "title" else df.loc[i,"ID"]
        string = f"[b]{df.loc[i,'Rank']:.0f}.[/b]"
        if round_score: string += f" {title} | Score: {df.loc[i,'Score']:.0f} | Votes: {df.loc[i,'Votes']:.0f}"
        else: string += f" {title} | Score: {df.loc[i,'Score']:.1f} | Votes: {df.loc[i,'Votes']:.0f}"
        #if Display == "RYM Print Diff.": string += f" | [color {color}]{diff:+.0f}[/color]"
        st.text(string)


FILM_DECADE_POLLS = ["Film (1980s)","Film (1990s)", "Film (2000s)", "Film (2010s)"]
def get_norm_factor_dict(cc_dict):
    """Normalization factors for combined charts"""
    max_votes = np.array([len(cc_dict[cc].vote_matrix.columns) for cc in FILM_DECADE_POLLS])
    norm_factors = max(max_votes)/max_votes
    return {cc: norm_factors[i] for i, cc in enumerate(FILM_DECADE_POLLS)}


def normalize_results(results):
    cc_dict = st.session_state["cc_dict"]
    norm_factors = get_norm_factor_dict(cc_dict)
    for cc in cc_dict:
        if cc in FILM_DECADE_POLLS:
            id = cc_dict[cc].vote_matrix.index
            results.loc[id, "Score"] *= norm_factors[cc]
            results.loc[id, "Votes"] *= norm_factors[cc]
    return results