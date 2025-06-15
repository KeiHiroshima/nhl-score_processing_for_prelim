import io
import os
import zipfile

import pandas as pd
import streamlit as st


def readcsv(folder_path, file_names):
    exp = ".csv"

    for i, file_name in enumerate(file_names):
        file_name += exp
        file_path = os.path.join(folder_path, file_name)
        data_one = pd.read_csv(file_path)

        if i == 0:
            scores = data_one
        else:
            scores = pd.concat((scores, data_one.iloc[:, 3]), axis=1)

    """
    scores.columns = scores.iloc[0]
    scores = scores.drop(0)"""

    return scores


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


def outputfiles_local(
    folder_path, players_top4, players_top5to36, players_top5to36_sorted
):
    col_names = ["audition_number", "name", "represent"]
    players_top4[col_names].to_csv(
        os.path.join(folder_path, "top4.csv"), index=False, sep=", "
    )
    players_top5to36[col_names].to_csv(
        os.path.join(folder_path, "top5to36.csv"), index=False, sep=", "
    )
    players_top5to36_sorted[col_names].to_csv(
        os.path.join(folder_path, "top5to36_sorted.csv"), index=False, sep=","
    )


def outputfiles(players_top4, players_top5to36, players_top5to36_sorted):
    col_names = ["audition_number", "name", "represent"]
    # dataframes to csv
    top4_csv = players_top4[col_names].to_csv(index=False, sep=", ")
    # top5to36_csv = players_top5to36[["No", "name", "Represent"]].to_csv(index=False)
    top5to36_sorted_csv = players_top5to36_sorted[col_names].to_csv(
        index=False, sep=", "
    )

    # make ZipFile
    with io.BytesIO() as buffer:
        with zipfile.ZipFile(buffer, "w") as z:
            z.writestr("top4.csv", top4_csv)
            # z.writestr("top5to36.csv", top5to36_csv)
            z.writestr("top5to36_sorted.csv", top5to36_sorted_csv)

        buffer.seek(0)

        # st.write("### file name list")
        # st.write(z.namelist())

        # download button
        st.download_button(
            label="Download top4.csv, top5to36.csv",
            data=buffer.getvalue(),  # buffer.getvalue()でzipファイルのバイナリデータを取得
            file_name="top36.zip",
            mime="application/zip",
        )


def get_zip(groups):
    group_names = ["A", "B", "C", "D", "E", "F", "G", "H"]
    with io.BytesIO() as buffer:
        with zipfile.ZipFile(buffer, "w") as z:
            ""  # output in each group
            for i, group in enumerate(groups):
                group = group.drop(columns="space")  # drop " " column

                with open(f"{group_names[i]}_circle.txt", "w") as f:
                    # for i, row in enumerate(group):
                    for index in range(group.shape[0]):
                        row = group.iloc[index]

                        if (
                            type(row["audition_number"]) is not int
                            or row["audition_number"] > 99
                        ):
                            f.write(
                                f"{row['audition_number']} {row['name represent']}\n"
                            )
                        elif row["audition_number"] < 10:
                            f.write(
                                f"{row['audition_number']}   {row['name represent']}\n"
                            )
                        elif (
                            row["audition_number"] > 9 and row["audition_number"] < 100
                        ):
                            f.write(
                                f"{row['audition_number']}  {row['name represent']}\n"
                            )

                z.write(f"{group_names[i]}_circle.txt")

            # output altogether
            with open("circles_wo_audition_number.txt", "w") as f_all:
                for i, group in enumerate(groups):
                    f_all.write(f"{group_names[i]} Circle\n")
                    group = group.drop(columns="space").values.tolist()

                    for i, row in enumerate(group):
                        if i == 0:  # judge
                            f_all.write(f"{row[0]} {row[1]}\n")
                        elif i == 1:  # guest / top 4
                            if row[1].split(" ")[0].isdecimal():
                                # remove audition number
                                row1_to_write = " ".join(row[1].split(" ")[1:])
                            else:
                                row1_to_write = row[1]
                            f_all.write(f"{row[0]} {row1_to_write}\n")
                        else:
                            f_all.write(f"{row[1]}\n")

                    f_all.write("\n")
            # add to zip
            z.write("circles_wo_audition_number.txt")

        buffer.seek(0)

        st.download_button(
            label="Download groups csv files",
            data=buffer.getvalue(),
            file_name="groups_for_cypher.zip",
            mime="application/zip",
        )


if __name__ == "__main__":
    folder_path = "/Users/te_keiero/PycharmProjects/NHL-score-prelim"
    judge_names = ["Judge1", "Judge2", "Judge3", "Judge4"]

    scores = readcsv(folder_path, judge_names)

    scores_processed = process(scores, judge_names)

    players_top4, players_top5to36, players_top5to36_sorted = top36(scores_processed)

    outputfiles_local(
        folder_path, players_top4, players_top5to36, players_top5to36_sorted
    )
