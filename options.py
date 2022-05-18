options = {"default_delimiter": ". ",
            "special_delimiters": ["\) "],
            "load_from_sheet": False,
            "size_dependent_borda": False,
            "remove_original_title": True,
            "database_id": "TMDB_id",
            "finalchar": "]",
            "link": "https://www.themoviedb.org/movie/"}

options_film_2010s = options.copy()
options_film_2010s["dataname"] = 'Film (2010s)'
options_film_2010s["SHEETNAME"] = '2010s Movies'
options_film_2010s["vote_matrix_csv"] = "https://raw.githubusercontent.com/YasashiiDia/ModifiedBorda/main/data/2010s%20Movies_vote_matrix.csv"
options_film_2010s["titles_csv"] = "https://raw.githubusercontent.com/YasashiiDia/ModifiedBorda/main/data/2010s%20Movies%20-%20Titles.csv"
options_film_2010s["metacols"] = ['Release','Runtime','Genres','Language','Director','Cast','Producer','Writer','Director of Photography','Editor','Composer','Sound Designer','Art Direction','Production Design','Costume Design','Makeup Artist']
options_film_2010s["type"] = "Film"
options_film_2010s["DEFAULT_RANK_OPTION"] = "BORDA_RANK_CLASSIC"
options_film_2010s["print"] = "ID"

options_film_2000s = options.copy()
options_film_2000s["dataname"] = 'Film (2000s)'
options_film_2000s["SHEETNAME"] = '2000s Movies'
options_film_2000s["vote_matrix_csv"] = "https://raw.githubusercontent.com/YasashiiDia/ModifiedBorda/main/data/2000s%20Movies_vote_matrix.csv"
options_film_2000s["titles_csv"] = "https://raw.githubusercontent.com/YasashiiDia/ModifiedBorda/main/data/2000s%20Movies%20-%20Titles.csv"
options_film_2000s["metacols"] = ['Release','Runtime','Genres','Language','Director','Cast','Producer','Writer','Director of Photography','Editor','Composer','Sound Designer','Art Direction','Production Design','Costume Design','Makeup Artist']
options_film_2000s["type"] = "Film"
options_film_2000s["DEFAULT_RANK_OPTION"] = "BORDA_RANK_CLASSIC"
options_film_2000s["print"] = "ID"

options_film_1990s = options.copy()
options_film_1990s["dataname"] = 'Film (1990s)'
options_film_1990s["SHEETNAME"] = '1990s in film'
options_film_1990s["vote_matrix_csv"] = "https://raw.githubusercontent.com/YasashiiDia/ModifiedBorda/main/data/1990s%20in%20film_vote_matrix.csv"
options_film_1990s["titles_csv"] = "https://raw.githubusercontent.com/YasashiiDia/ModifiedBorda/main/data/1990s%20in%20film_meta_df.csv"
options_film_1990s["metacols"] = ['Release','Runtime','Genres','Language','Director','Cast','Producer','Writer','Director of Photography','Editor','Composer','Sound Designer','Art Direction','Production Design','Costume Design','Makeup Artist']
options_film_1990s["type"] = "Film"
options_film_1990s["DEFAULT_RANK_OPTION"] = "BORDA_RANK_CLASSIC"
options_film_1990s["print"] = "ID"

options_film_1980s = options.copy()
options_film_1980s["dataname"] = 'Film (1980s)'
options_film_1980s["SHEETNAME"] = '1980s in film'
options_film_1980s["vote_matrix_csv"] = "https://raw.githubusercontent.com/YasashiiDia/ModifiedBorda/main/data/1980s%20in%20film_vote_matrix.csv"
options_film_1980s["titles_csv"] = "https://raw.githubusercontent.com/YasashiiDia/ModifiedBorda/main/data/1980s%20in%20film_meta_df.csv"
options_film_1980s["metacols"] = ['Release','Runtime','Genres','Language','Director','Cast','Producer','Writer','Director of Photography','Editor','Composer','Sound Designer','Art Direction','Production Design','Costume Design','Makeup Artist']
options_film_1980s["type"] = "Film"
options_film_1980s["DEFAULT_RANK_OPTION"] = "BORDA_RANK_CLASSIC"
options_film_1980s["print"] = "ID"

options_film_combined = options.copy()
options_film_combined["dataname"] = 'Film (Combined)'
options_film_combined["vote_matrix_csv"] = "https://raw.githubusercontent.com/YasashiiDia/ModifiedBorda/main/data/combined_film_vote_matrix.csv"
options_film_combined["titles_csv"] = "https://raw.githubusercontent.com/YasashiiDia/ModifiedBorda/main/data/combined_film_metadata.csv"
options_film_combined["metacols"] = ['Release','Runtime','Genres','Language','Director','Cast','Producer','Writer','Director of Photography','Editor','Composer','Sound Designer','Art Direction','Production Design','Costume Design','Makeup Artist']
options_film_combined["type"] = "Film"
options_film_combined["DEFAULT_RANK_OPTION"] = "BORDA_RANK_CLASSIC"
options_film_combined["print"] = "ID"

options_anime_series = options.copy()
options_anime_series["dataname"] = 'Anime Series'
options_anime_series["SHEETNAME"] = 'RYM AniChart 4.1'
options_anime_series["finalchar"] = ""
options_anime_series["database_id"] = "AniListID"
options_anime_series["link"] = "https://anilist.co/anime/"
options_anime_series["remove_original_title"] = False
options_anime_series["vote_matrix_csv"] = "https://raw.githubusercontent.com/YasashiiDia/ModifiedBorda/main/data/RYM%20AniChart%204.1_vote_matrix.csv"
options_anime_series["titles_csv"] = "https://raw.githubusercontent.com/YasashiiDia/ModifiedBorda/main/data/RYM%20AniChart%204.1%20-%20Titles.csv"
options_anime_series["metacols"] = ['Genres','Studio','Source','Episodes','First Air Date','Last Air Date']
options_anime_series["type"] = "Series"
options_anime_series["DEFAULT_RANK_OPTION"] = "BORDA_RANK"
options_anime_series["print"] = "Title"
options_anime_series["size_dependent_borda"] = True

options_list = [options_film_2010s,
               options_film_2000s,
               options_film_1990s,
               options_film_1980s,
               options_film_combined,
               options_anime_series]

options_dict_all = {"Film (2010s)": options_film_2010s,
                    "Film (2000s)": options_film_2000s,
                    "Film (1990s)": options_film_1990s,
                    "Film (1980s)": options_film_1980s,
                    "Film (Combined)": options_film_combined,
                    "Anime Series": options_anime_series
                    }