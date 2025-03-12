# Portland-Postmortem

To use this repo now, you need the reproduce-portland branch of votekit installed.

1) Run reformat_csvs.py
2) Run clean_profiles.py
3) To use a profile, load it with the pickle module and you are set to start analyzing.
    ```with open("district_1_profile.pkl", "rb") as f:
        profile = pickle.load(f)
    ```