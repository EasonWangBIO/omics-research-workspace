suppressPackageStartupMessages(
    {
        library(DESeq2)
    }
)

cat("R:", R.version.string,"\n")
cat(
    "DESeq2:",
    as.character(packageVersion("DESeq2")),
    "\n"
)

args<- commandArgs(trailingOnly = TRUE)

if (length(args)!=5) {
   stop(
    paste("Usage: Rscript scripts/run_deseq2.R",
      "<count_file> <metadata_file>",
      "<reference_group> <comparison_group> <output_dir>"
   )
   )
}
count_file <- args[[1]]
metadata_file <- args[[2]]
reference_group <- args[[3]]
comparison_group <- args[[4]]
output_dir <- args[[5]]

cat("Count file:", count_file, "\n")
cat("Metadata file:", metadata_file, "\n")
cat("Reference group:", reference_group, "\n")
cat("Comparison group:", comparison_group, "\n")
cat("Output directory:", output_dir, "\n")

#input data
if(!file.exists(count_file)){
    stop(paste("Count file does not exist:", count_file))
}
if (!file.exists(metadata_file)) {
  stop(paste("Metadata file does not exist:", metadata_file))
}

read_input_table <- function(file_path) {
    extension <- tolower(tools::file_ext(file_path))
    
    if(!extension %in% c("csv","tsv")) {
        stop(paste(
            "Unsupported file type:",extension
        ))
    
}

separator <- if(extension == "tsv") "\t" else {
   ","
}

read.table(file_path, header = TRUE,  sep = separator,row.names= 1, check.names=FALSE)
}

count_data<- read_input_table(count_file)
metadata_data<- read_input_table(metadata_file)

#show the shape of data
cat(
  "Count matrix:",
  nrow(count_data),
  "genes x",
  ncol(count_data),
  "samples\n"
)

cat(
  "Metadata:",
  nrow(metadata_data),
  "samples x",
  ncol(metadata_data),
  "columns\n"
)

#input check like python
count_sample_ids <- colnames(count_data)
metadata_sample_ids <- rownames(metadata_data)

missing_in_metadata <- setdiff(
  count_sample_ids,
  metadata_sample_ids
)

missing_in_counts <- setdiff(
  metadata_sample_ids,
  count_sample_ids
)

if (length(missing_in_metadata) > 0) {
  cat(
    "Missing from metadata:",
    paste(missing_in_metadata, collapse = ", "),
    "\n"
  )
}

if (length(missing_in_counts) > 0) {
  cat(
    "Missing from count matrix:",
    paste(missing_in_counts, collapse = ", "),
    "\n"
  )
}

if (
  length(missing_in_metadata) > 0 ||
  length(missing_in_counts) > 0
) {
  stop("Sample IDs do not match.")
}

metadata_data <- metadata_data[
  count_sample_ids,
  ,
  drop = FALSE
]

cat("Sample IDs match and metadata order is aligned.\n")

if (!"group" %in% colnames(metadata_data)) {
  stop("Metadata must contain a 'group' column.")
}

metadata_data$group <- trimws(
  as.character(metadata_data$group)
)

if (any(is.na(metadata_data$group) | metadata_data$group == "")) {
  stop("The group column contains missing values.")
}

available_groups <- unique(metadata_data$group)

if (!reference_group %in% available_groups) {
  stop(
    paste(
      "Reference group not found:",
      reference_group
    )
  )
}

if (!comparison_group %in% available_groups) {
  stop(
    paste(
      "Comparison group not found:",
      comparison_group
    )
  )
}

if (reference_group == comparison_group) {
  stop("Reference and comparison groups must be different.")
}

metadata_data$group <- factor(metadata_data$group)

metadata_data$group <- relevel(
  metadata_data$group,
  ref = reference_group
)

cat(
  "Available groups:",
  paste(levels(metadata_data$group), collapse = ", "),
  "\n"
)

cat(
  "Contrast:",
  comparison_group,
  "vs",
  reference_group,
  "\n"
)

count_matrix <- as.matrix(count_data)

if (!is.numeric(count_matrix)) {
  stop("Count matrix contains non-numeric values.")
}

if (anyNA(count_matrix)) {
  stop("Count matrix contains missing values.")
}

if (any(count_matrix < 0)) {
  stop("Count matrix contains negative values.")
}

if (any(count_matrix %% 1 != 0)) {
  stop("Count matrix contains non-integer values.")
}

storage.mode(count_matrix) <- "integer"

dds <- DESeqDataSetFromMatrix(
  countData = count_matrix,
  colData = metadata_data,
  design = ~ group
)

cat(
  "DESeqDataSet created:",
  nrow(dds),
  "genes x",
  ncol(dds),
  "samples\n"
)