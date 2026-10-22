# Architecture v0

## User workflow

count matrix + sample metadata
-> input validation
-> analysis run creation
-> DESeq2 execution
-> result parsing
-> visualization and report export

## Responsibilities

- Streamlit: user interface and interaction state
- Python: validation, orchestration, storage, and report generation
- R/DESeq2: statistical differential-expression analysis
- SQLite: project metadata and run history
- Filesystem: uploaded datasets and generated analysis results

## Design rule

The user interface must not contain statistical-analysis logic.
Analysis functions must be testable without starting Streamlit.
Each analysis run must preserve its inputs, parameters, logs, and outputs.