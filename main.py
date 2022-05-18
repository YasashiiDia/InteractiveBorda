# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

import utility as ut
from options import options_dict_all

TOP_WEIGHT_DISTRIBUTION = list(np.linspace(0.1, 0.9, 10)) + list(np.linspace(1, 5, 11))


@st.experimental_memo
def get_results_df(vote_matrix, top_weight, pop_weight, _pop_multiplier, size_dependent):
    results = pd.DataFrame(index=vote_matrix.index)
    results["Votes"] = vote_matrix.astype(bool).sum(axis=1)
    vote_matrix = vote_matrix.mask(vote_matrix < 0, 1)  # fix unranked ballots
    ranked_vote_matrix = ut.tiers_to_avg_rank(vote_matrix)
    list_sizes = ut.get_list_sizes_from_vote_matrix(ranked_vote_matrix) if size_dependent else ranked_vote_matrix.max().max()
    score_matrix = ranked_vote_matrix.mask(ranked_vote_matrix > 0, ut.superellipse(ranked_vote_matrix - 1,
                                           n=top_weight, a=1, b=1, size=list_sizes))  # vm-1 to move superellipse upwards
    results["Score"] = score_matrix.sum(axis=1)
    most_votes = max(results["Votes"])
    results["Score"] *= _pop_multiplier(results["Votes"], most_votes, pop_weight)
    #results["Score"] = results["Score"].round(1)
    results["Score"] += 0.00001 * results["Votes"]  # hacky way of breaking ties by number of votes AND use method="min" for tied votes
    results["Rank"] = results["Score"].rank(ascending=False, method='min').astype(int)
    results["Score"] = results["Score"].round(1)
    return results, ranked_vote_matrix


@st.experimental_memo
def load_data(**options):
    vote_matrix = pd.read_csv(options["vote_matrix_csv"],index_col=[0,1])
    meta_df = pd.read_csv(options["titles_csv"], index_col=[0,1])
    return vote_matrix, meta_df


def main(**options):

    ## Weights
    top_weight = st.sidebar.slider('Top Weight', -10, 10, 0)
    top_weight = TOP_WEIGHT_DISTRIBUTION[top_weight + 10]
    pop_weight = 10*st.sidebar.slider('Pop Weight', -20, 20, 0)

    if np.abs(pop_weight) <= 100:
        pop_multiplier = ut.linear_pop_multiplier
    else:
        pop_weight -= np.sign(pop_weight) * 100
        pop_multiplier = ut.elliptical_pop_multiplier

    size_dependent_borda = st.sidebar.checkbox('Size-dependent Borda')

    vote_matrix, meta_df = load_data(**options)
    results, rvm = get_results_df(vote_matrix, top_weight, pop_weight, pop_multiplier, size_dependent_borda)

    return results


if __name__ == '__main__':

    st.title('RYM Interactive Poll Results')

    dataset = st.sidebar.selectbox('Select Dataset', options_dict_all.keys())
    options_dict = options_dict_all[dataset]

    results = main(**options_dict)

    st.dataframe(results)