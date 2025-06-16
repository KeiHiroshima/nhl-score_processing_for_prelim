import pandas as pd
import streamlit as st

from main import get_zip


def outputtext(groups, top4=None, flag_history=False):
    if not flag_history:
        sep_str = " "
        # audition_number, name, represent -> audition_number+'space'+name/represent
        top4_processed = [
            f"{int(onedata[0])} {onedata[1]} ({onedata[2]})"
            for onedata in top4.values.tolist()
        ]
        top4_order_to_cypher = [3, 2, 4, 1]  # not index

        judge_names = ["HIRO", "Masae", "KENJI", "MOTOKI"]
        guest_names = [
            f"Torch{sep_str}(Cracker)",
            f"NUE{sep_str}(Natural Movementz)",
            f"SINVY{sep_str}(Seren:D)",
            f"minami{sep_str}(soil)",
        ]

        # concat top4 and guests
        top4_guests_list = []

        num_groups = 8
        guest_index, top4_index = 0, 0
        for i in range(num_groups):
            if i >= len(judge_names):
                judge_index = i - len(judge_names)
                judge_index += 1 if judge_index % 2 == 0 else -1  # switch latter half
            else:
                judge_index = i

            if i % 2 == 0:  # pick top4 in odd circle
                guest_row = [
                    "GUEST:",
                    " ",
                    top4_processed[top4_order_to_cypher[top4_index] - 1],
                ]
                top4_index += 1
            else:  # pick guest in even circle
                guest_row = ["GUEST:", " ", guest_names[guest_index]]
                guest_index += 1

            top4_guests_list.append(
                pd.DataFrame(
                    [
                        ["JUDGE:", " ", judge_names[judge_index]],
                        guest_row,
                    ]
                )
            )

        group_list = []
        for i, group in enumerate(groups):
            one_group = pd.DataFrame(
                {
                    0: group["audition_number"].astype(int),
                    1: " ",
                    2: group.apply(
                        lambda x: f"{x['name']}"
                        if pd.isna(x["represent"])
                        else f"{x['name']}{sep_str}({x['represent']})",
                        axis=1,
                    ),
                }
            )
            group_list.append(one_group)

        # concat top4s and groups
        output_list = []
        for i, group in enumerate(group_list):
            one_output = pd.concat((top4_guests_list[i], group), axis=0).reset_index(
                drop=True
            )
            one_output.columns = ["audition_number", "space", f"name{sep_str}represent"]
            output_list.append(one_output)

    else:
        output_list = groups

    # display text in capyable format
    st.write("### Groups for 2nd prelim")
    group_names = ["A", "B", "C", "D", "E", "F", "G", "H"]

    col1, col2 = st.columns(2)
    with col1:
        # print even circles
        for i in range(0, len(output_list), 2):
            output = output_list[i]
            output = output.drop(columns="space")

            st.write(f"#### {group_names[i]} circle")
            st.write(output)
    with col2:
        # print odd circles
        for i in range(1, len(output_list), 2):
            output = output_list[i]
            output = output.drop(columns="space")

            st.write(f"#### {group_names[i]} circle")
            st.write(output)

    get_zip(output_list)

    return output_list


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
