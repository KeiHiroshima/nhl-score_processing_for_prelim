import numpy as np
import pandas as pd
import streamlit as st

from main import get_zip


def outputtext(groups, top4):
    # audition_number, name, represent -> audition_number+'space'+name/represent
    top4_processed = [
        f"{int(onedata[0])} {onedata[1]}/{onedata[2]}"
        for onedata in top4.values.tolist()
    ]

    # concat top4 and guests
    top4_guests_list = []
    top4_guests = np.array(
        [
            [["JUDGE:", " ", "KAZUKIYO"], ["GUEST:", " ", top4_processed[2]]],
            [["JUDGE:", " ", "KEIN"], ["GUEST:", " ", "Mei/タイ"]],
            [["JUDGE:", " ", "HIRO"], ["GUEST:", " ", top4_processed[1]]],
            [["JUDGE:", " ", "SU→"], ["GUEST:", " ", "MEI/大阪"]],
            [["JUDGE:", " ", "KEIN"], ["GUEST:", " ", top4_processed[3]]],
            [["JUDGE:", " ", "KAZUKIYO"], ["GUEST:", " ", "SAKI"]],
            [["JUDGE:", " ", "SU→"], ["GUEST:", " ", top4_processed[0]]],
            [["JUDGE:", " ", "HIRO"], ["GUEST:", " ", "Juaena"]],
        ]
    )
    for i in range(top4_guests.shape[0]):
        top4_guests_list.append(pd.DataFrame(top4_guests[i]))

    # pre-process on groups
    # audition_number, name, represent -> audition_number+"space"+name/represent

    group_list = []
    for i, group in enumerate(groups):
        one_group = pd.DataFrame(
            {
                0: group["audition_number"].astype(int),
                1: " ",
                2: group.apply(
                    lambda x: f"{x['name']}"
                    if pd.isna(x["represent"])
                    else f"{x['name']}/{x['represent']}",
                    axis=1,
                ),
            }
        )
        group_list.append(one_group)

    # concat top4s and groups
    output_list = []
    for i, group in enumerate(group_list):
        one_output = pd.concat((top4_guests_list[i], group), axis=0)
        output_list.append(one_output)

    # display text in capyable format
    st.write("### Groups for 2nd prelim")
    group_names = ["A", "B", "C", "D", "E", "F", "G", "H"]

    for i, output in enumerate(output_list):
        # drop " " column
        output = output.drop(columns=1)
        st.write(f"#### Group {group_names[i]}")
        st.write(output)

    """
    # display output_list in txt format
    output_list_txt = {}
    for i, output in enumerate(output_list):
        # drop " " column
        output = output.drop(columns=1)

        # add to output_list_txt, key: group name, value: output in txt format
        output_list_txt[group_names[i]] = output.to_string(index=False, header=False)

    st.write("### Output in txt format")
    st.write(output_list_txt)
    for key, value in output_list_txt.items():
        st.write(f"#### Group {key}")
        st.write(value)"""

    get_zip(output_list)

    return


def main():
    sample_top4 = pd.DataFrame(
        {
            "audition_number": [1, 2, 3, 4],
            "name": ["A", "B", "C", "D"],
            "represent": ["a", "b", "c", "d"],
        }
    )

    sample_groups = []
    for i in range(8):
        sample_group = pd.DataFrame(
            {
                "audition_number": [1, 2, 3, 4],
                "name": ["A", "B", "C", "D"],
                "represent": ["a", "b", "c", "d"],
            }
        )
        sample_groups.append(sample_group)

    print("### test run")
    # test run
    outputtext(sample_groups, sample_top4)


if __name__ == "__main__":
    main()
