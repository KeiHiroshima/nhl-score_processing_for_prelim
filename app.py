import pandas as pd
import streamlit as st

from main import process, top36
from makegroup import split_random
from outputtext import get_zip, outputtext, outputtext_history

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

random_seed = 42

st.title("Processing 1st prelim and grouping to 8")

# input total entry number to session state
st.write("### Input total entry number")
st.session_state["num_entry"] = st.number_input(
    "Total entry number", min_value=0, value=254
)

st.write("## Upload files to start ")

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
    st.dataframe(scores)


if uploaded_files:
    name_list = name_list[-4:]  # judges name

    scores_processed = process(scores, name_list)

    players_top4, players_top5to36 = top36(scores_processed)

    st.session_state["top4"] = players_top4

st.write("## Grouping to 8 groups")

if st.button("Random 8 groups"):
    groups = split_random(players_top5to36, random_seed)

    output_list = outputtext(groups, st.session_state["top4"])

    history = st.session_state.get("history", [])
    history.append(output_list)

    st.session_state["history"] = history


st.write("### Logs")

if len(st.session_state["history"]) > 1:
    history = st.session_state["history"]
    st.write(f"{len(history)} logs found")

    index = st.slider("Select history", 0, len(history) - 1, 0)
    st.session_state["index"] = index
    # st.write(history[index])
    outputtext_history(history[index])

    if st.button("Looks good to this output?"):
        groups = history[index]
        get_zip(groups)
