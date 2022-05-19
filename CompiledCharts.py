import streamlit as st

class CompiledCharts:

    def __init__(self, vote_matrix, meta_df, **options):
        self.vote_matrix = vote_matrix
        self.meta_df = meta_df