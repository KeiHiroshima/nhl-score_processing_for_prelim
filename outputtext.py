import pandas as pd
import streamlit as st

from utils import get_zip


def _missing_represent(value):
    """True when a represent value should be treated as 'no represent'.

    Covers NaN as well as empty / whitespace-only strings (e.g. a blank CSV cell
    read as '' or a represent field the user cleared in the form), so output
    renders `(123)` instead of a half-formed `(123, )`.
    """
    return pd.isna(value) or (isinstance(value, str) and value.strip() == "")


def build_output_list(groups, top4):
    """
    Pure output-line builder (no Streamlit). Given the 8 groups and the top4
    DataFrame, build a list of 8 DataFrames each holding a single "line" column
    (judge/guest header rows followed by player rows).
    """
    sep_str = " "
    # audition_number, name, represent -> audition_number+'space'+name/represent
    top4_processed = [
        f"{onedata[1]} ({int(onedata[0])})" if _missing_represent(onedata[2]) else f"{onedata[1]} ({int(onedata[0])}, {onedata[2]})"
        for onedata in top4.values.tolist()
    ]
    top4_order_to_cypher = [3, 2, 4, 1]  # not index

    judge_names = ["HIRO", "JAE-SANG", "Take", "SINVY"]
    guest_names = [
        f"Kate",
        f"Bronco",
        f"MARCIA",
        f"YOUTEE",
    ]

    # build judge/guest rows as final single-line strings per circle
    top4_guests_list = []

    num_groups = 8
    guest_index, top4_index = 0, 0
    for i in range(num_groups):
        if i >= len(judge_names):
            judge_index = i - len(judge_names)
            judge_index += 1 if judge_index % 2 == 0 else -1  # switch latter half
        else:
            judge_index = i

        judge_line = f"JUDGE: {judge_names[judge_index]}"

        if i % 2 == 0:  # pick top4 in odd circle
            guest_line = (
                f"GUEST: {top4_processed[top4_order_to_cypher[top4_index] - 1]}"
            )
            top4_index += 1
        else:  # pick guest in even circle
            guest_line = f"GUEST: {guest_names[guest_index]}"
            guest_index += 1

        top4_guests_list.append(pd.DataFrame({"line": [judge_line, guest_line]}))

    # build player rows as final single-line strings
    group_list = []
    for i, group in enumerate(groups):
        one_group = pd.DataFrame(
            {
                "line": group.apply(
                    lambda x: f"{x['name']}{sep_str}({int(x['audition_number'])})"
                    if _missing_represent(x["represent"])
                    else f"{x['name']}{sep_str}({int(x['audition_number'])}, {x['represent']})",
                    axis=1,
                ),
            }
        )
        group_list.append(one_group)

    # concat judge/guest rows and player rows into one "line" column per circle
    output_list = []
    for i, group in enumerate(group_list):
        one_output = pd.concat((top4_guests_list[i], group), axis=0).reset_index(
            drop=True
        )
        output_list.append(one_output)

    return output_list


def outputtext(groups, top4=None, flag_history=False):
    if not flag_history:
        output_list = build_output_list(groups, top4)
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

            st.write(f"#### {group_names[i]} circle")
            st.write(output)
    with col2:
        # print odd circles
        for i in range(1, len(output_list), 2):
            output = output_list[i]

            st.write(f"#### {group_names[i]} circle")
            st.write(output)

    # if not flag_history or (flag_history and st.button("Looks good to this output?")):
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
