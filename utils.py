import io
import random
import zipfile

import pandas as pd
import streamlit as st


def process(scores, judges):
    """
    (score - mean) / deviation
    """
    scores_processed = scores[["audition_number", "name", "represent"]].copy()

    scores_mean = scores[judges].mean(axis=0)
    scores_std = scores[judges].std(axis=0)

    for judge in judges:
        scores_processed.loc[:, judge] = (
            scores.loc[:, judge] - scores_mean.loc[judge]
        ) / scores_std.loc[judge]

    scores_processed["sum"] = scores_processed[judges].sum(axis=1)

    return scores_processed


def manual_formatting(df):
    """
    Format the 'represent' column in the DataFrame.
    """
    df_processed = df.copy()

    with st.form("formatting_form"):
        st.write("### Formatting represent column")
        for i, row in df_processed.iterrows():
            if not pd.isna(row["represent"]):
                df_processed.at[i, "represent"] = st.text_input(
                    row["name"], value=row["represent"], key=f"represent_{i}"
                )

        st.form_submit_button("update represent")

    return df_processed


def top36(scores_processed):
    scores_des = scores_processed.sort_values(by="sum", ascending=False).reset_index(
        drop=True
    )
    scores_des.index += 1  # start from 1
    st.write("### Results of 1st prelim")
    st.write(scores_des)

    col_names = ["audition_number", "name", "represent"]
    players_top36 = scores_des.iloc[:36][col_names].copy()

    players_top36_formatted_rep = manual_formatting(players_top36)

    players_top4 = players_top36_formatted_rep.iloc[:4]
    # sort_values(by="audition_number", ascending=True)

    players_top5to36 = players_top36_formatted_rep.iloc[4:36]

    st.write("### Top 4")
    st.write(players_top4)

    st.write("### Top 5 to 36")
    st.write(players_top5to36.copy().sort_values(by="audition_number", ascending=True))

    # download button for score_des.csv
    st.download_button(
        label="Download result on 1stprelim.csv",
        data=scores_des.to_csv(index=False, sep=","),
        file_name="result-1stprelim.csv",
        mime="text/csv",
    )

    return players_top4, players_top5to36


def get_zip(groups):
    group_names = ["A", "B", "C", "D", "E", "F", "G", "H"]
    with io.BytesIO() as buffer:
        with zipfile.ZipFile(buffer, "w") as z:
            # output each circle into its own file (in-memory, no temp files on disk)
            for i, group in enumerate(groups):
                content = "".join(f"{line}\n" for line in group["line"].tolist())
                z.writestr(f"{group_names[i]}_circle.txt", content)

            # output all circles altogether (in-memory, no temp files on disk)
            all_parts = []
            for i, group in enumerate(groups):
                all_parts.append(f"{group_names[i]} Circle\n")
                all_parts.extend(f"{line}\n" for line in group["line"].tolist())
                all_parts.append("\n")
            z.writestr("circles_wo_audition_number.txt", "".join(all_parts))

        buffer.seek(0)

        st.download_button(
            label="Download groups csv files",
            data=buffer.getvalue(),
            file_name="groups_for_cypher.zip",
            mime="application/zip",
            key=f"download_groups_zip_{random.randint(0, 999)}",  # random key to avoid caching
        )
