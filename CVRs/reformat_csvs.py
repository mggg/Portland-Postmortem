import pandas as pd
import gdown

district_to_file = {1:"1ly3IcjeQTpet-zvxd49DM_OmY_i4uftB", 2:"1HgB9oE1L0HgjsAAKvBjnNvmQM8R-igy5",
                    3:"1MrKA8gTxNg2AwdmdGaZ_QS8b2wG3ZN5H", 4:"1OO5njgKIBinASfiaYvNK5Xf8lBgBNxUV"}

for district, file_id in district_to_file.items():
    print(f"Reformatting District {district}")
    url = f"https://drive.google.com/uc?id={file_id}"
    save_to = f"./raw_city_csv/Portland_D{district}_raw_from_city.csv"

    print("Downloading raw data...")
    gdown.download(url, save_to, quiet=False)

    df = pd.read_csv(save_to)

    rank_columns = {i:[col for col in df.columns if f'{i}:Number' in col] for i in range(1,7)}
    all_rank_cols = [col for col_list in rank_columns.values() for col in col_list]

    voters_df = df[df[all_rank_cols].sum(axis=1) > 0].reset_index(drop=True) 

    ranking_data = {i:[-1 for _ in range(len(voters_df))] for i in range(1,7)}

    print("Formatting...")
    for voter_index, row in voters_df.iterrows():
        for rank_position in range(1,7):
            num_votes_cast = row[rank_columns[rank_position]].sum()

            if num_votes_cast == 0:
                cast_vote = ""
            
            elif num_votes_cast > 1:
                cast_vote = "overvote"

            else:
                # find candidate name from column
                pd_series = row[rank_columns[rank_position]]
                cast_vote_column_name = pd_series.loc[pd_series == 1].index.tolist()[0]
                cast_vote = cast_vote_column_name.split(":")[-2]

            ranking_data[rank_position][voter_index] = cast_vote

    for rank_position in range(1,7):
        voters_df[f"Rank {rank_position}"] = ranking_data[rank_position]

    print("Saving...")
    voters_df[[f"Rank {rank_position}" for rank_position in range(1,7)]].to_csv(f"./raw_votekit_csv/Portland_D{district}_raw_votekit_format.csv")
    print("\n-----------\n")
