import streamlit as st

from omics_workspace import __version__
from omics_workspace.io import read_table

st.set_page_config(
    page_title="Omics Research Workspace",
    page_icon="🧬",
    layout="wide",
)

st.title("Omics Research Workspace")
st.caption(f"Version {__version__}")

st.write(
    "Upload a count matrix and sample metadata to start a reproducible"
    "bulk RNA-seq analysis"
)

st.divider()
st.subheader("Input files")

count_column, meta_column = st.columns(2)

with count_column:
    count_file = st.file_uploader(
        "count matrix",
        type=["csv","tsv"],
        help="Genes in rows and samples in columns.",
    )

with meta_column:
    metadata_file = st.file_uploader(
        "Sample metadata",
        type=["csv","tsv"],
        help="One row per sample, including sample IDs and groups",
    )

#Assuming all tests failed
count_is_valid = False
metadata_is_valid = False
sample_ids_match = False


#check input empty or not 
if count_file is not None:
    count_data = read_table(count_file,count_file.name)
    st.subheader("Count matrix preview")
    st.dataframe(count_data.head())
    gene_count,sample_count = count_data.shape
    st.write(f"{gene_count} gene x {sample_count} samples")

if metadata_file is not None:
    metadata_data = read_table(metadata_file,metadata_file.name)

    st.subheader("Sample metadata preview")
    st.dataframe(metadata_data.head())

    sample_count,column_count = metadata_data.shape
    st.write(f"{sample_count} samples x {column_count} metadata columns")
    
    #check the group column
    if "group" not in metadata_data.columns:
        st.error("Metadata must contain group column.")
    elif metadata_data["group"].isna().any():
        st.error("please check groups column contains missing values.")
    elif metadata_data["group"].nunique()<2:
        st.error("At least two groups are required.")
    else:
        group_counts = metadata_data["group"].value_counts()
    if (group_counts < 2).any():
            st.error("Each group must contain at least two samples.")
    else:
            metadata_is_valid = True
            st.success("Metadata contains valid experimental groups.")
            st.dataframe(group_counts.rename("sample_count"))



#check sample match correctness
if count_file is not None and metadata_data is not None:
    count_sample_ids = set(count_data.columns.astype(str))
    metadata_sample_ids = set(metadata_data.index.astype(str))

    missing_in_metadata = sorted(count_sample_ids - metadata_sample_ids)
    missing_in_counts = sorted(metadata_sample_ids - count_sample_ids)

    if not missing_in_metadata and not missing_in_counts:
        sample_ids_match = True
        st.success("Sample IDs match between count matrix and metadata.")
    else:
        st.error("Sample IDs do not match.")

        if missing_in_metadata:
            st.write("Missing from metadata:", missing_in_metadata)

        if missing_in_counts:
            st.write("Missing from count matrix:", missing_in_counts)

#numerical check
    non_numeric_columns = count_data.select_dtypes(
        exclude="number"
    ).columns.tolist()

    if non_numeric_columns:
        st.error(
            f"Non-numeric values found in columns:{non_numeric_columns}"
        )
    elif count_data.isna().any().any():
        st.error("Count matrix contains missing values.")
    elif (count_data < 0).any().any():
        st.error("Count matrix contains negative values.")   
    elif ((count_data % 1) != 0).any().any():
        st.error("Count matrix contains non-integer values.")
    else:
        count_is_valid = True
        st.success(
            "Count matrix contains valid non-negative integer counts."
        )

analysis_is_ready = (
    count_is_valid
    and metadata_is_valid
    and sample_ids_match
)
if analysis_is_ready:
    st.success("Input validation completed. Analysis setup is ready")
    st.divider()
    st.subheader("Analysis setup")

    groups = sorted(
        metadata_data["group"].astype(str).unique()
    )

    reference_group = st.selectbox(
        "Reference group",
        options=groups,
    )
    comparison_options = [
        group
        for group in groups
        if group != reference_group
    ]
    comparison_group = st.selectbox(
        "Comparison group",
        options=comparison_options,
    )

    st.info(
        f"Comparison: {comparison_group} vs {reference_group}"
    )