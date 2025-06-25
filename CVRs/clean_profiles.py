
from votekit.cvr_loaders import load_csv
from votekit.cleaning import remove_cand, remove_repeated_candidates, condense_profile
from votekit.elections import STV
from votekit.utils import first_place_votes
import pickle, requests, csv
import time


official_tabulation_urls = {1:"https://mcdcselectionsrcvprdst.z5.web.core.windows.net/a18a5db1-04a2-4123-8ccb-de12b485f135_City%20of%20Portland%20Councilor%20District%201/2024-12-02_15-04-43_report_official.csv",
                           2:"https://mcdcselectionsrcvprdst.z5.web.core.windows.net/a18a5db1-04a2-4123-8ccb-de12b485f135_City%20of%20Portland%20Councilor%20District%202/2024-12-02_15-04-45_report_official.csv",
                           3:"https://mcdcselectionsrcvprdst.z5.web.core.windows.net/a18a5db1-04a2-4123-8ccb-de12b485f135_City%20of%20Portland%20Councilor%20District%203/2024-12-02_15-04-48_report_official.csv",
                           4:"https://mcdcselectionsrcvprdst.z5.web.core.windows.net/a18a5db1-04a2-4123-8ccb-de12b485f135_City%20of%20Portland%20Councilor%20District%204/2024-12-02_15-04-55_report_official.csv"}


def get_official_results(file_name):
    """
    Return the threshold, winning candidates, and fpv dict of the given official portland csv election
    results. The fpv dict includes many keys that are not candidates, these should be ignored.
    
    """
    with open(file_name) as file:
        reader = csv.reader(file)

        possible_fpv = {}
        for i, row in enumerate(reader):
            if row:
                if "Election Threshold" == row[0]:
                    threshold = int(row[1].split(" ")[0])
                
                if "Met threshold for election" in row[0]:
                    elected_cand_list = row[1:]
                    elected_cand_list = [c.split("; ") for c in elected_cand_list if c!= ""]
                    elected_cand_list = [c for s in elected_cand_list for c in s]
                
                try:
                    possible_fpv[row[0]] = row[1]
                except:
                    # row too short
                    pass
    
    return(threshold, elected_cand_list, possible_fpv)


for d, link in official_tabulation_urls.items():
    print(f"Downloading district {d} results")
    response = requests.get(link)
    with open(f"./official_city_results/Portland_D{d}_official_tabulations.csv", "wb") as file:
        file.write(response.content)

print()

results = {d:{} for d in range(1,5)}
for d in range(1,5):
    print(f"Formatting district {d} results")
    results[d]["threshold"], results[d]["winner set"], results[d]["fpv_dict"] = get_official_results(f"./official_city_results/Portland_D{d}_official_tabulations.csv")

print()


for d in range(1,5):
    print(f"Cleaning district {d} profile with VoteKit")
    profile = load_csv(f"./raw_votekit_csv/Portland_D{d}_raw_votekit_format.csv", rank_cols=[1,2,3,4,5,6]) 
    writeins = [c for c in profile.candidates if 'Write-in-' in c]
    profile = condense_profile(remove_cand(["overvote"] + writeins, profile))
    profile = condense_profile(remove_repeated_candidates(profile))
    print("cleaned")

    print(f"Computing district {d} results with VoteKit")
    election = STV(profile, m=3)
    # TODO district 2,3 has weird problem where STV fails at certain stage
    # due to a ballot without ranking
    # but the OG profile has no such ballots
    # D4 works but yields: UserWarning: Profile does not contain rankings but max_ranking_length=6. Setting max_ranking_length to 0.
    # so somewhere the rankings are going off

    winner_set_match = set([c for s in election.get_elected() for c in s]) == set(results[d]["winner set"])
    threshold_match = election.threshold == results[d]["threshold"]

    fpv_dict = first_place_votes(profile)
    fpv_match = fpv_dict == {c:float(results[d]["fpv_dict"][c]) for c in fpv_dict.keys()}

    if not threshold_match or not fpv_match or not winner_set_match:
        raise ValueError(f"One of threshold {threshold_match}, fpv {fpv_match}, or winner set {winner_set_match} does not match official results")

    print(f"VoteKit data for District {d} matches official results. Saving profile.")
    profile.to_pickle(f"./cleaned_votekit_profiles/Portland_D{d}_cleaned_votekit_pref_profile.pkl")

    print("\n-------------------------------------------------\n")



