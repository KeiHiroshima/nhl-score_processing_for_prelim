import time

import pandas as pd
import streamlit as st

from makegroup import split_random
from outputtext import outputtext
from utils import constant_judges, process, top36

uploaded_files = []

# init session state: num_entry, history, groups
if "num_entry" not in st.session_state:
    st.session_state["num_entry"] = 0
if "history" not in st.session_state:
    st.session_state["history"] = []
if "groups" not in st.session_state:
    st.session_state["groups"] = []
if "top4" not in st.session_state:
    st.session_state["top4"] = []

random_seed = int(time.time())  # use current time as random seed for grouping

st.title("Processing 1st prelim and grouping to 8")

# input total entry number to session state
st.write("### Input total entry number")
st.session_state["num_entry"] = st.number_input(
    "Total entry number", min_value=0, value=255
)

st.write("### Upload files to start ")

# upload entrylist
enterylist_uploaded = st.file_uploader("Upload entrylist", type="csv")
if enterylist_uploaded:
    entrylist = pd.read_csv(
        enterylist_uploaded, header=None, nrows=st.session_state["num_entry"]
    )
    entrylist.columns = ["audition_number", "name", "represent"]


# upload score sheets
uploaded_file = st.file_uploader(
    "Upload score sheets from judges", type="csv", accept_multiple_files=True
)
if uploaded_file:
    if enterylist_uploaded is None:
        st.error("Upload entrylist first. Restart the app.")
        st.stop()
    uploaded_files = uploaded_file

    scores_list = []
    name_list = entrylist.columns.tolist()
    st.write("### Raw scores")
    for i, file in enumerate(uploaded_files):
        df = pd.read_csv(
            file, header=None, index_col=0, nrows=st.session_state["num_entry"]
        )
        scores_list.append(df)

        # get file name for column name
        file_name = file.name
        file_name = file_name[:-4]  # drop .csv
        name_list.append(file_name)

    scores = pd.concat(scores_list, axis=1, ignore_index=True)
    scores.index = range(len(scores))  # give index from 0 to n

    scores = pd.concat([entrylist, scores], axis=1, ignore_index=True)
    scores.columns = name_list

    # persist to session state so processing reads from a single source of truth
    # (also lets tests inject scores directly, bypassing the file uploader)
    st.session_state["scores"] = scores
    st.session_state["judge_names"] = name_list[-4:]  # judges name
    st.dataframe(scores)


if st.session_state.get("scores") is not None and len(st.session_state["scores"]):
    scores = st.session_state["scores"]
    judge_names = st.session_state["judge_names"]

    disabled_judges = constant_judges(scores, judge_names)
    if disabled_judges:
        st.warning(
            "These judges gave identical scores to everyone and were disabled "
            f"(treated as 0, no effect on ranking): {', '.join(disabled_judges)}"
        )

    scores_processed = process(scores, judge_names)

    players_top4, players_top5to36 = top36(scores_processed)

    st.session_state["top4"] = players_top4
    st.session_state["top5to36"] = players_top5to36

st.write("## Grouping to 8")

if st.button("Random grouping to 8"):
    groups = split_random(st.session_state["top5to36"], random_seed)

    output_list = outputtext(groups, st.session_state["top4"])

    st.session_state["history"].append(output_list)


st.write("### Logs")

if len(st.session_state["history"]) > 1:
    history = st.session_state["history"]
    st.write(f"{len(history)} logs found")

    index = st.slider("Select history", 0, len(history) - 1, 0)
    st.session_state["index"] = index

    outputtext(st.session_state["history"][index], flag_history=True)
