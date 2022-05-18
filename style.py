import numpy as np
import pandas as pd
import streamlit as st

def color_signs(s):
    '''Color positive values green, negative values red, zero blue'''
    zeros=np.where(s==0)
    s=np.where(s>0, "color: green", "color: red")
    s[zeros]="color: blue"
    return s


def style_df(a, metacols):
    a_styled = a.style.set_properties(**{'text-align': 'center'})#.hide_index("ID") outdated pandas
    a_styled = a_styled.set_table_styles([dict(selector='th', props=[('text-align', 'center')])]) # centering index name
    a_styled = a_styled.format("{:.1f}",subset=['Score'])
    #a_styled = a_styled.format("{:+.0f}",subset=['Diff.'])
    a_styled = a_styled.format("{:.0f}",subset=['Rank','Votes'])
    if "Runtime" in metacols: a_styled = a_styled.format("{:.0f}",subset=['Runtime'])
    if "Episodes" in metacols: a_styled = a_styled.format("{:.0f}",subset=['Episodes'])
    #a_styled.apply(color_signs, axis=0, subset=['Diff.'])
    return a_styled


def path_to_tmdb_image_html(path, width=120):
    return f'<img src="https://image.tmdb.org/t/p/w600_and_h900_bestv2{path}" style="width:{width}px">'