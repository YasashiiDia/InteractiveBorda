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
def get_results_df_old(vote_matrix, top_weight, size_dependent):
    results = pd.DataFrame(index=vote_matrix.index)
    results["Votes"] = vote_matrix.astype(bool).sum(axis=1)
    weight = TOP_WEIGHT_DISTRIBUTION[top_weight+10]
    partial_rankings = ut.get_partial_rankings(vote_matrix, size_dependent)
    for v in vote_matrix: vote_matrix[v] = vote_matrix[v].mask(vote_matrix[v] < 0,
                                                               partial_rankings[v].loc["Avg_Unranked_Rank"])
    list_sizes = partial_rankings.loc["Size"] if size_dependent else max(partial_rankings.loc["Size"])
    score_matrix = vote_matrix.mask(vote_matrix > 0, ut.superellipse(vote_matrix - 1, n=weight, a=1, b=1,
                                    size=list_sizes))  # vm-1 to move superellipse upwards
    results["Score"] = score_matrix.sum(axis=1)
    return results, vote_matrix


@st.experimental_memo
def get_results_df(vote_matrix, top_weight, size_dependent):
    results = pd.DataFrame(index=vote_matrix.index)
    results["Votes"] = vote_matrix.astype(bool).sum(axis=1)
    weight = TOP_WEIGHT_DISTRIBUTION[top_weight+10]
    vote_matrix = vote_matrix.mask(vote_matrix < 0, 1)  # fix unranked ballots
    ranked_vote_matrix = ut.tiers_to_avg_rank(vote_matrix)
    list_sizes = ut.get_list_sizes_from_vote_matrix(ranked_vote_matrix) if size_dependent else ranked_vote_matrix.max().max()
    score_matrix = ranked_vote_matrix.mask(ranked_vote_matrix > 0, ut.superellipse(ranked_vote_matrix - 1,
                                           n=weight, a=1, b=1, size=list_sizes))  # vm-1 to move superellipse upwards
    results["Score"] = score_matrix.sum(axis=1)
    return results, ranked_vote_matrix


@st.experimental_memo
def load_data(**options):
    vote_matrix = pd.read_csv(options["vote_matrix_csv"],index_col=[0,1])
    meta_df = pd.read_csv(options["titles_csv"], index_col=[0,1])
    return vote_matrix, meta_df


def main(**options):
    top_weight = st.sidebar.slider('Top Weight', -10, 10, 0)
    vote_matrix, meta_df = load_data(**options)
    results, rvm = get_results_df(vote_matrix, top_weight, options["size_dependent"])
    results_old, vm = get_results_df_old(vote_matrix, top_weight, options["size_dependent"])

    # st.write(np.array_equal(rvm.values, vm.values))
    # st.write(rvm.shape,vm.shape)
    # st.write(rvm[rvm != vm])
    # for v in rvm:
    #     a = rvm[v][rvm[v] != vm[v]]
    #     if len(a)>0:
    #         st.write(a, vm[v][rvm[v] != vm[v]])
    # st.write(rvm["[deleted]"],vm["[deleted]"],vote_matrix["[deleted]"])
    return results


if __name__ == '__main__':

    st.title('RYM Interactive Poll Results')

    dataset = st.sidebar.selectbox('Select Dataset', options_dict_all.keys())
    options_dict = options_dict_all[dataset]

    options_dict["size_dependent"] = st.checkbox('Size-dependent Borda')

    results = main(**options_dict)

    st.dataframe(results)

    # st.text_input("Your name", key="name")
    # st.session_state.name