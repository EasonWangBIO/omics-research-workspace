from pathlib import Path
from uuid import uuid4

import pandas as pd
import streamlit as st

from omics_workspace import __version__
from omics_workspace.deseq2 import run_deseq2
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
        type=["csv", "tsv"],
        help="Genes in rows and samples in columns.",
    )

with meta_column:
    metadata_file = st.file_uploader(
        "Sample metadata",
        type=["csv", "tsv"],
        help="One row per sample, including sample IDs and groups",
    )

# Validation flags remain false until each check passes.
count_is_valid = False
metadata_is_valid = False
sample_ids_match = False

# Read uploaded files only when they are available.
if count_file is not None:
    count_data = read_table(count_file, count_file.name)
    st.subheader("Count matrix preview")
    st.dataframe(count_data.head())
    gene_count, sample_count = count_data.shape
    st.write(f"{gene_count} gene x {sample_count} samples")

if metadata_file is not None:
    metadata_data = read_table(metadata_file, metadata_file.name)

    st.subheader("Sample metadata preview")
    st.dataframe(metadata_data.head())

    sample_count, column_count = metadata_data.shape
    st.write(f"{sample_count} samples x {column_count} metadata columns")

    # Check the experimental group column.
    if "group" not in metadata_data.columns:
        st.error("Metadata must contain group column.")
    elif metadata_data["group"].isna().any():
        st.error("Group column contains missing values.")
    elif metadata_data["group"].nunique() < 2:
        st.error("At least two groups are required.")
    else:
        group_counts = metadata_data["group"].value_counts()
        if (group_counts < 2).any():
            st.error("Each group must contain at least two samples.")
        else:
            metadata_is_valid = True
            st.success("Metadata contains valid experimental groups.")
            st.dataframe(group_counts.rename("sample_count"))


# Check sample ID agreement and count values.
if count_file is not None and metadata_file is not None:
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

    non_numeric_columns = count_data.select_dtypes(exclude="number").columns.tolist()

    if non_numeric_columns:
        st.error(f"Non-numeric values found in columns: {non_numeric_columns}")
    elif count_data.isna().any().any():
        st.error("Count matrix contains missing values.")
    elif (count_data < 0).any().any():
        st.error("Count matrix contains negative values.")
    elif ((count_data % 1) != 0).any().any():
        st.error("Count matrix contains non-integer values.")
    else:
        count_is_valid = True
        st.success("Count matrix contains valid non-negative integer counts.")

analysis_is_ready = count_is_valid and metadata_is_valid and sample_ids_match
if analysis_is_ready:
    st.success("Input validation completed. Analysis setup is ready")
    st.divider()
    st.subheader("Analysis setup")

    groups = sorted(metadata_data["group"].astype(str).unique())

    reference_group = st.selectbox(
        "Reference group",
        options=groups,
    )
    comparison_options = [group for group in groups if group != reference_group]
    comparison_group = st.selectbox(
        "Comparison group",
        options=comparison_options,
    )

    st.info(f"Comparison: {comparison_group} vs {reference_group}")

    run_clicked = st.button(
        "Run DESeq2 analysis",
        type="primary",
    )
    if run_clicked:
        run_id = uuid4().hex
        run_dir = Path("runs") / run_id

        run_dir.mkdir(
            parents=True,
            exist_ok=False,
        )

        count_suffix = Path(count_file.name).suffix.lower()
        count_path = run_dir / f"counts{count_suffix}"

        count_path.write_bytes(count_file.getvalue())

        metadata_suffix = Path(metadata_file.name).suffix.lower()
        metadata_path = run_dir / f"metadata{metadata_suffix}"

        metadata_path.write_bytes(metadata_file.getvalue())
        try:
            with st.spinner("Running DESeq2 analysis..."):
                result_path, run_log = run_deseq2(
                    count_path=count_path,
                    metadata_path=metadata_path,
                    reference_group=reference_group,
                    comparison_group=comparison_group,
                    output_dir=run_dir,
                )

        except (RuntimeError, FileNotFoundError) as error:
            st.error(f"DESeq2 analysis failed: {error}")
        else:
            st.session_state["analysis_result"] = {
                "result_path": str(result_path),
                "run_log": run_log,
                "reference_group": reference_group,
                "comparison_group": comparison_group,
            }

            st.success("DESeq2 analysis completed successfully.")

    saved_result = st.session_state.get("analysis_result")
    if saved_result is not None:
        result_path = Path(saved_result["result_path"])
        result_data = pd.read_csv(result_path)

        total_genes = len(result_data)

        significant_genes = int(result_data["padj"].lt(0.05).sum())

        st.divider()
        st.subheader("Differential expression results")

        comparison_column, total_column, significant_column = st.columns(3)

        comparison_column.metric(
            "Comparison",
            (
                f"{saved_result['comparison_group']} vs "
                f"{saved_result['reference_group']}"
            ),
        )

        total_column.metric(
            "Genes in result",
            f"{total_genes:,}",
        )

        significant_column.metric(
            "padj < 0.05",
            f"{significant_genes:,}",
        )

        st.dataframe(
            result_data.head(20),
            hide_index=True,
        )

        result_bytes = result_path.read_bytes()

        st.download_button(
            label="Download complete results",
            data=result_bytes,
            file_name=result_path.name,
            mime="text/csv",
            on_click="ignore",
        )

        st.subheader("Analysis log")

        st.code(
            saved_result["run_log"],
            language="text",
        )
