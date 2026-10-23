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

if count_file is not None:
    count_data = read_table(count_file,count_file.name)
    st.subheader("Count matrix preview")
    st.dataframe(count_data.head())
    gene_count,sample_count = count_data.shape
    st.write(f"{gene_count} gene x {sample_count} samples")
