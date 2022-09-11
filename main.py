import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

import utility as ut
import style as sty
import plots
from options import options_dict_all
from CompiledCharts import CompiledCharts

TOP_WEIGHT_DISTRIBUTION = list(np.linspace(0.1, 0.9, 10)) + list(np.linspace(1, 5, 11))
FILM_DECADE_POLLS = ["Film (1970s)", "Film (1980s)", "Film (1990s)", "Film (2000s)", "Film (2010s)"]

@st.experimental_memo
def get_results_df(vote_matrix, top_weight, pop_weight, _pop_multiplier, size_dependent, multiply_by_votes, normalize=False):
    """
    :param pandas.DataFrame vote_matrix: Tiers in vote matrix should be converted to ranks using prepare_data.ipynb
    :param float top_weight:
    :param float pop_weight:
    :param function _pop_multiplier:
    :param bool size_dependent:
    :param bool multiply_by_votes:
    :param bool normalize:
    :return:
    """
    results = pd.DataFrame(index=vote_matrix.index)
    results["Votes"] = vote_matrix.astype(bool).sum(axis=1)
    list_sizes = ut.get_list_sizes_from_vote_matrix(vote_matrix) if size_dependent else vote_matrix.max().max()
    score_matrix = vote_matrix.mask(vote_matrix > 0, ut.superellipse(vote_matrix - 1,
                                    n=top_weight, a=1, b=1, size=list_sizes))  # vm-1 to move superellipse upwards
    results["Score"] = score_matrix.sum(axis=1)

    if normalize:
        results = ut.normalize_results(results)
        results["Votes"] = results["Votes"].round(0)

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


#@st.experimental_memo
def load_data(**options):
    dataname = options["dataname"]
    if dataname not in st.session_state["cc_dict"]:
        vote_matrix = pd.read_csv(options["vote_matrix_csv"], index_col=[0,1])
        meta_df = pd.read_csv(options["titles_csv"], index_col=[0,1])
        if "Runtime" in meta_df.columns:
            meta_df["Runtime"] = meta_df["Runtime"].mask(meta_df["Runtime"].isna(),0).astype(int)
        if "Episodes" in meta_df.columns:
            meta_df["Episodes"] = meta_df["Episodes"].mask(meta_df["Episodes"].isna(),0).astype(int)
        st.session_state["cc_dict"][dataname] = CompiledCharts(vote_matrix, meta_df, **options)
    else:
        vote_matrix = st.session_state["cc_dict"][dataname].vote_matrix
        meta_df = st.session_state["cc_dict"][dataname].meta_df
    return vote_matrix, meta_df


def display_interactive_chart(**options):

    # Weights
    top_weight = st.sidebar.slider('Ballot Item Weight', -10, 10, 0)
    top_weight = TOP_WEIGHT_DISTRIBUTION[top_weight + 10]
    pop_weight = 10*st.sidebar.slider('Popularity Weight', -20, 20, 0)

    if np.abs(pop_weight) <= 100:
        pop_multiplier = ut.linear_pop_multiplier
    else:
        pop_weight -= np.sign(pop_weight) * 100
        pop_multiplier = ut.elliptical_pop_multiplier

    # Other widgets
    plot_weights_choice = st.sidebar.checkbox("Plot weights")
    size_dependent_borda = st.sidebar.checkbox('Deweight incomplete ballots')
    multiply_by_votes = st.sidebar.checkbox('Multiply by number of votes')

    # Calculate results
    ranked_vote_matrix, meta_df = load_data(**options)
    results, rvm = get_results_df(ranked_vote_matrix, top_weight, pop_weight, pop_multiplier, size_dependent_borda, multiply_by_votes, options["normalize"])

    # Add metadata
    metacols = options["metacols"] + ["IMGID"]
    meta_df_display = meta_df[metacols]
    results = pd.concat([results, meta_df_display], axis=1)

    # Style results
    cols = results.columns.drop(["IMGID","Votes","Rank"]).to_list()
    results["ID"] = results.index.get_level_values(level=0)
    results["Title"] = results.index.get_level_values(level=1)
    results.index = results["IMGID"].apply(sty.path_to_tmdb_image_html)
    results.index.name = None
    results = results[["Title","Rank","Votes"]+cols+["ID"]]
    n_results = st.sidebar.slider('Results', 0, 250, 20, 10)

    # https://stackoverflow.com/questions/50807744/apply-css-class-to-pandas-dataframe-using-to-html
    # https://towardsdatascience.com/pagination-in-streamlit-82b62de9f62b
    # https://docs.streamlit.io/library/components/components-api
    # https://pagination.js.org/
    # https://www.jqueryscript.net/blog/best-table-pagination.html

    if plot_weights_choice:
        most_votes = results["Votes"].max()
        most_votes_title = results.sort_values(by="Votes", ascending=False)["Title"].iloc[0]
        max_length = ranked_vote_matrix.max().max() if options["dataname"] != "Film (Combined)" else 50
        fig = plots.plot_weights(top_weight, pop_weight, multiply_by_votes, size_dependent_borda, pop_multiplier, most_votes, most_votes_title, max_length)
        st.pyplot(fig)

    n_voters = len(ranked_vote_matrix.columns)
    n_titles = len(results)
    votes = ranked_vote_matrix.astype(bool).sum().sum()
    st.write(f"**Voters:** {n_voters} | **Titles:** {n_titles} | **Votes:** {votes}" + (f"$\quad$(unadjusted)" if options["dataname"] == "Film (Combined)" else ""))
    results = results[:n_results]
    display_option = st.sidebar.radio("Display as:", ["Table", "Raw Text", "RYM Print"])
    if display_option == "Table":
        table = results.to_html(classes=["styled-table"], escape=False)
        st.write(table, unsafe_allow_html=True)
    elif display_option == "Raw Text":
        ut.print_df(results, mode="title")
    elif display_option == "RYM Print":
        ut.print_df(results, mode="rym")

    dupes = results.loc[results.index.duplicated(keep=False)]
    if len(dupes) > 0:
        st.write("Duplicated images found:")
        st.dataframe(dupes)
    # show_id = st.sidebar.checkbox('Show title ID')
    # if not show_id:
    #     results_styled = results_styled.hide(axis="index")  # doesn't work with st.dataframe()
    #results_styled = sty.style_df(results, metacols)
    #st.dataframe(results_styled)


def display_correlations(method="pearson", **options):
    ranked_vote_matrix, _ = load_data(**options)
    voter = st.sidebar.selectbox("Select voter:", ranked_vote_matrix.columns)
    method = st.sidebar.radio("Correlation metric:", ["Pearson", "Spearman", "Kendall"])
    MAX_LENGTH = ranked_vote_matrix.max().max()
    vmc = ranked_vote_matrix.mask(ranked_vote_matrix > 0, MAX_LENGTH + 1 - ranked_vote_matrix).corr(method=method.lower())
    all_user_votes = ut.get_votes_df_from_vote_matrix(ranked_vote_matrix)
    voter_corr = ut.voter_corr(vmc, all_user_votes, voter)

    display_option = st.sidebar.radio("Display as:", ["Table", "Raw Text"])
    if display_option == "Table":
        table = voter_corr.to_html(classes="styled-table", escape=False)
        st.write(table, unsafe_allow_html=True)
    elif display_option == "Raw Text":
        a = vmc[voter].sort_values(ascending=False)
        print_string = ""
        for v in a.index:
            print_string += f"{v}: {a.loc[v]:.2f}  \n"
        st.markdown(print_string)


#@st.experimental_memo(suppress_st_warning=True)
def init_film():
    for decade in FILM_DECADE_POLLS:
        if decade not in st.session_state["cc_dict"]:
            break
    else:
        return
    for decade in FILM_DECADE_POLLS:
        load_data(**options_dict_all[decade])

def main():
    if 'cc_dict' not in st.session_state:
        st.session_state["cc_dict"] = {}

    init_film()

    choice = st.sidebar.radio("", ["Interactive Chart", "Voter Correlations"])
    dataset = st.sidebar.selectbox('Select dataset:', options_dict_all.keys())
    options_dict = options_dict_all[dataset]

    if choice == "Interactive Chart":
        if dataset == "Film (Combined)":
            st.write("Note that the combined film charts are normalized to adjust for differences in voter turnout between the decade polls.")
        display_interactive_chart(**options_dict)
    elif choice == "Voter Correlations":
        display_correlations(**options_dict)


if __name__ == '__main__':
    st.set_page_config(layout='wide')

    with open("style.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    st.title("RYM Interactive Poll Results")
    st.write("Very early work in progress. More features can be found in the [Google Colab Notebook](https://colab.research.google.com/drive/1hOq6fSF2a7t00FXl-KBUVlYifpz9ZkHp).")
    main()
    #st.write("Diagnostic", st.session_state)

    # from streamlit.components.v1 import html
    # https://docs.streamlit.io/library/components/components-api
    # ag-grid images: https://discuss.streamlit.io/t/ag-grid-component-with-input-support/8108/63
    # sorttable scroll: http://output.jsbin.com/enotac/2