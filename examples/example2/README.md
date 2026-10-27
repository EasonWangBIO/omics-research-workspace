# Official airway RNA-seq example

This example is derived reproducibly from Bioconductor's `airway` experiment
data package, version 1.30.0.

## Source and license

- Package: https://bioconductor.org/packages/airway/
- Package license: LGPL
- Study: Himes et al., *PLoS ONE* (2014), PMID 24926665
- GEO accession: GSE52778
- Samples: four human airway smooth-muscle cell lines, untreated or treated
  with dexamethasone

The original package provides a `RangedSummarizedExperiment` containing 63,677
genes and eight samples. The files in this directory are exported by
`scripts/export_airway_example.R` rather than copied from an unidentified
mirror.

## Files

- `counts.tsv`: raw integer count matrix; genes are rows and samples are
  columns.
- `metadata.csv`: sample IDs, analysis group, cell-line batch, original cell
  label, and original dexamethasone treatment label.
- `mistake_test/`: deliberately invalid metadata used to verify input
  validation. These files are test fixtures, not scientific datasets.

The `group` column is derived from the upstream `dex` field:

- `untrt` becomes `control`.
- `trt` becomes `dexamethasone`.

## Rebuild

Install the official data package in the `omics` Conda environment, then run:

```bash
conda install -n omics -c conda-forge -c bioconda bioconductor-airway=1.30.0
Rscript scripts/export_airway_example.R
```

Run the command-line analysis with:

```bash
Rscript scripts/run_deseq2.R \
  examples/example2/counts.tsv \
  examples/example2/metadata.csv \
  control \
  dexamethasone \
  results
```
