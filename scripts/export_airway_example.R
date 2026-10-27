suppressPackageStartupMessages({
  library(airway)
})

data(
  "airway",
  package = "airway"
)

cat(
  "airway package version:",
  as.character(packageVersion("airway")),
  "\n"
)

cat(
  "License:",
  packageDescription("airway")$License,
  "\n"
)

cat(
  "Dimensions:",
  nrow(airway),
  "genes x",
  ncol(airway),
  "samples\n"
)

cat(
  "Sample IDs:",
  paste(colnames(airway), collapse = ", "),
  "\n"
)

output_dir <- file.path(
  "examples",
  "example2"
)

dir.create(
  output_dir,
  recursive = TRUE,
  showWarnings = FALSE
)

count_data <- data.frame(
  gene_id = rownames(airway),
  as.data.frame(
    SummarizedExperiment::assay(airway)
  ),
  check.names = FALSE
)

count_file <- file.path(
  output_dir,
  "counts.tsv"
)

write.table(
  count_data,
  file = count_file,
  sep = "\t",
  quote = FALSE,
  row.names = FALSE
)

cat(
  "Count matrix exported to:",
  count_file,
  "\n"
)

metadata_source <- as.data.frame(
  SummarizedExperiment::colData(airway)
)

metadata_data <- data.frame(
  sample_id = rownames(metadata_source),
  group = ifelse(
    metadata_source$dex == "trt",
    "dexamethasone",
    "control"
  ),
  batch = metadata_source$cell,
  cell = metadata_source$cell,
  dex = as.character(metadata_source$dex),
  check.names = FALSE
)

metadata_file <- file.path(
  output_dir,
  "metadata.csv"
)

write.csv(
  metadata_data,
  file = metadata_file,
  row.names = FALSE
)

cat(
  "Metadata exported to:",
  metadata_file,
  "\n"
)
