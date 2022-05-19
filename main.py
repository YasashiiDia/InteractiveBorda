import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

import utility as ut
import style as sty
from options import options_dict_all

TOP_WEIGHT_DISTRIBUTION = list(np.linspace(0.1, 0.9, 10)) + list(np.linspace(1, 5, 11))


@st.experimental_memo
def get_results_df(vote_matrix, top_weight, pop_weight, _pop_multiplier, size_dependent, multiply_by_votes):
    results = pd.DataFrame(index=vote_matrix.index)
    results["Votes"] = vote_matrix.astype(bool).sum(axis=1)
    list_sizes = ut.get_list_sizes_from_vote_matrix(vote_matrix) if size_dependent else vote_matrix.max().max()
    score_matrix = vote_matrix.mask(vote_matrix > 0, ut.superellipse(vote_matrix - 1,
                                           n=top_weight, a=1, b=1, size=list_sizes))  # vm-1 to move superellipse upwards
    results["Score"] = score_matrix.sum(axis=1)
    most_votes = max(results["Votes"])
    results["Score"] *= _pop_multiplier(results["Votes"], most_votes, pop_weight)
    if multiply_by_votes: results["Score"] *= results["Votes"]
    results["Score"] = results["Score"].round(1)
    results["Score"] += 0.00001 * results["Votes"]  # hacky way of breaking ties by number of votes AND use method="min" for tied votes
    results["Rank"] = results["Score"].rank(ascending=False, method='min').astype(int)
    results["Score"] = results["Score"].round(1)
    results.index.set_names(['ID', 'Title'], inplace=True)
    results.sort_values(by="Rank", inplace=True)
    return results, vote_matrix


@st.experimental_memo
def load_data(**options):
    vote_matrix = pd.read_csv(options["vote_matrix_csv"],index_col=[0,1])
    meta_df = pd.read_csv(options["titles_csv"], index_col=[0,1])
    return vote_matrix, meta_df


def display_interactive_chart(**options):

    # Weights
    top_weight = st.sidebar.slider('Top Weight', -10, 10, 0)
    top_weight = TOP_WEIGHT_DISTRIBUTION[top_weight + 10]
    pop_weight = 10*st.sidebar.slider('Pop Weight', -20, 20, 0)

    if np.abs(pop_weight) <= 100:
        pop_multiplier = ut.linear_pop_multiplier
    else:
        pop_weight -= np.sign(pop_weight) * 100
        pop_multiplier = ut.elliptical_pop_multiplier

    # Other widgets
    size_dependent_borda = st.sidebar.checkbox('Size-dependent Borda count')
    multiply_by_votes = st.sidebar.checkbox('Multiply by # votes')

    # Calculate results
    vote_matrix, meta_df = load_data(**options)
    ranked_vote_matrix = ut.get_ranked_vote_matrix(vote_matrix)
    results, rvm = get_results_df(ranked_vote_matrix, top_weight, pop_weight, pop_multiplier, size_dependent_borda, multiply_by_votes)

    # Add metadata
    metacols = options["metacols"] + ["IMGID"]
    meta_df_display = meta_df[metacols]
    results = pd.concat([results, meta_df_display], axis=1)

    # Style results
    cols = results.columns.to_list()
    cols.remove("IMGID")
    results["ID"] = results.index.get_level_values(level=0)
    results["Title"] = results.index.get_level_values(level=1)
    results.index = results["IMGID"].apply(sty.path_to_tmdb_image_html)
    results.index.name = None
    results = results[["Title"]+cols+["ID"]]

    n_results = st.sidebar.slider('Results', 0, 250, 20, 10)
    results = results[:n_results]
    results_styled = results

    # show_id = st.sidebar.checkbox('Show title ID')
    # if not show_id:
    #     results_styled = results_styled.hide(axis="index")  # doesn't work with st.dataframe()

    # https://stackoverflow.com/questions/50807744/apply-css-class-to-pandas-dataframe-using-to-html
    # https://towardsdatascience.com/pagination-in-streamlit-82b62de9f62b
    # https://docs.streamlit.io/library/components/components-api
    # https://pagination.js.org/
    # https://www.jqueryscript.net/blog/best-table-pagination.html

    table = results_styled.to_html(classes="styled-table", escape=False)
    st.write(table, unsafe_allow_html=True)

    #results_styled = sty.style_df(results, metacols)
    #st.dataframe(results_styled)


def display_correlations(method="pearson", **options):
    vote_matrix, _ = load_data(**options)
    voter = st.sidebar.selectbox("Select voter:", vote_matrix.columns)
    method = st.sidebar.radio("Correlation metric:", ["Pearson", "Spearman", "Kendall"])
    ranked_vote_matrix = ut.get_ranked_vote_matrix(vote_matrix)
    MAX_LENGTH = vote_matrix.max().max()
    vmc = ranked_vote_matrix.mask(ranked_vote_matrix > 0, MAX_LENGTH + 1 - ranked_vote_matrix).corr(method=method.lower())
    #vmc = ranked_vote_matrix.corr(method=method)
    all_user_votes = ut.get_votes_df_from_vote_matrix(ranked_vote_matrix)
    voter_corr = ut.voter_corr(vmc, all_user_votes, voter)
    table = voter_corr.to_html(classes="styled-table", escape=False)
    st.write(table, unsafe_allow_html=True)


def main():
    choice = st.sidebar.radio("", ["Interactive Chart", "Voter Correlations"])
    dataset = st.sidebar.selectbox('Select dataset:', options_dict_all.keys())
    options_dict = options_dict_all[dataset]

    if choice == "Interactive Chart":
        display_interactive_chart(**options_dict)
    elif choice == "Voter Correlations":
        display_correlations(**options_dict)


if __name__ == '__main__':
    st.set_page_config(layout='wide')
    with open("style.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    st.title("RYM Interactive Poll Results")
    st.write("Very early work in progress. More features can be found in the [Google Colab Notebook](https://colab.research.google.com/drive/1hOq6fSF2a7t00FXl-KBUVlYifpz9ZkHp). Note that the combined film charts are not yet normalized for voter turnout.")
    main()