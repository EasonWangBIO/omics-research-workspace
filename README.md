# Omics Research Workspace

A reproducible Streamlit workspace for two-group bulk RNA-seq differential
expression analysis with Python, R, and DESeq2.

## Current workflow

1. Upload a raw count matrix and sample metadata in CSV or TSV format.
2. Validate count values, experimental groups, biological replicates, and
   sample ID agreement.
3. Select a reference group and comparison group.
4. Run DESeq2 through an isolated Python-to-R interface.
5. Review the comparison, result counts, top result rows, and analysis log.
6. Download the complete differential-expression result as CSV.

Each run stores its inputs and generated result under the ignored `runs/`
directory. Streamlit session state keeps the current result visible during
normal in-app reruns.

## Development setup

The current development environment uses Python 3.12, R 4.5, and DESeq2 1.50.

```bash
conda activate omics
python -m pip install -e ".[dev]"
python -m pytest -v
python -m ruff check .
python -m streamlit run app.py
```

## Reproducible example data

`examples/example2/` is rebuilt from Bioconductor's official `airway` data
package. Its source, LGPL license, study citation, transformations, and rebuild
command are documented in `examples/example2/README.md`.

The small files under `examples/example1/` remain useful for fast input and
validation checks but are too small for a representative DESeq2 model fit.

## Planned increments

- PCA and sample-level quality control
- Volcano, MA, correlation, and expression heat maps
- Configurable thresholds and gene annotation
- GO and KEGG enrichment analysis
- Reproducible reports and run history
