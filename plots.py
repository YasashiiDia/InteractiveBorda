import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns; sns.set()
import streamlit as st
import utility as ut


def plot_weights(top_weight, pop_weight, multiply_by_votes, size_dependent_borda, pop_multiplier, most_votes, most_votes_title, max_length):
    fig, ax = plt.subplots(1, 2, figsize=(15, 5))
    # Point distribution
    x = np.arange(1, max_length+1)
    y = ut.superellipse(x - 1, n=top_weight, a=1, b=1, size=max_length)  # x-1 to move superellipse upwards
    ax[0].plot([1, max_length], [max_length, 1], label="Borda", ls="--", c="darkgrey")
    ax[0].scatter(x, y,label=f"Ballot N={max_length:.0f}")
    if size_dependent_borda:
        ax[0].scatter(x[:len(x)//2], y[:len(x)//2]-len(x)//2, label=f"Ballot N={max_length//2:.0f}")
    ax[0].set_xlabel("Ballot Position")
    ax[0].set_ylabel("Points")
    ax[0].set_ylim(0, 1.1 * max_length)

    # Popularity multipliers
    x = np.arange(1, most_votes + 1)
    popm = pop_multiplier(x, most_votes, pop_weight)
    y = x*popm if multiply_by_votes else popm
    ax[1].scatter(x, y)
    ax[1].set_xlabel("Votes")
    ax[1].set_ylabel("Popularity Multiplier")
    if multiply_by_votes:
        ax[1].set_ylim(0, 1.1 * max(y))
    else:
        ax[1].set_ylim(-0.1, 2.1)
    ax[1].axvline(most_votes, ls="--", c="darkgrey", label=f"Most Votes ({most_votes}): {most_votes_title}")

    for a in ax: a.legend(loc="best",fontsize="medium")
    fig.tight_layout()
    return fig