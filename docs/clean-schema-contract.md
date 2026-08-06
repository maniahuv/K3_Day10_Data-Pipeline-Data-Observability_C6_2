# Clean data contract

## Input and output

`build_clean_dataframe` receives parsed `PaperRecord` values from the raw snapshot and produces one row per stable `paper_id` for the embedding index.

The output columns are `paper_id`, `title`, `summary`, `authors`, `categories`, `primary_category`, `published`, `updated`, `abs_url`, `pdf_url`, `comment`, `authors_joined`, `categories_joined`, `summary_chars`, `age_days`, and `text_for_embedding`.

## Cleaning rules

- `paper_id`, `title`, `summary`, and `published` are required. Rows missing one of these values are filtered and logged with a reason.
- `published` must be a valid ISO date and cannot be later than the pipeline run date. `updated` is optional; an invalid value becomes empty.
- Duplicate rows use the canonical, case-insensitive `paper_id`; keep the first source row and log every removed duplicate.
- `authors` and `categories` are optional lists. Normalize whitespace, remove blank values and duplicates while preserving order. Their joined fields are empty when the list is empty.
- `primary_category` is the first normalized category, or empty when no category exists.

## Derived fields

`text_for_embedding` is built from non-empty `title`, `summary`, `authors_joined`, and `categories_joined`, with labels for each field.

`age_days` is the non-negative difference in days between the supplied run date and `published`.

## CP1 validation fixture

`tests/fixtures/raw_records_sample.json` provides a valid record, a duplicate ID, a missing summary, and an invalid date. CP1 validation must confirm that only the valid first record remains, derived fields are correct, and filtering/deduplication counts are traceable.
