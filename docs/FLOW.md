# Listing Data Flow

## 1. Data Extraction
- Listings are scraped from external sources.
- Raw listing data is collected in inconsistent formats.

### Responsibility
Scraper modules

---

## 2. First Layer Cleaning (Normalization)
- Normalize column names
- Separate numerical values from strings
- Standardize formats and units
- Basic null handling

### Goal
Convert raw scraper output into a consistent schema.

### Output
Structurally normalized tabular data

---

## 3. Database Storage
- Cleaned records are stored in PostgreSQL.

### Goal
Persist normalized listing data for querying and downstream processing.

---

## 4. Second Layer Cleaning (Structural Safety)
Performed before loading database records into active processing pipelines.

### Operations
- Resolve inconsistent floor/floors fields
- Normalize parking values
- Handle location structure inconsistencies
- Ensure dataframe-safe schema

### Function
`make_df_structurally_safe`

### Goal
Prevent downstream dataframe operations from breaking due to structural inconsistencies.

---

## 5. Third Layer Cleaning (Serialization Safety)
Performed only when converting dataframe records into JSON-compatible formats.

### Operations
- Convert NaN values
- Convert Inf values
- Handle NumPy scalar serialization

### Function
`df_to_json_safe_records`

### Goal
Ensure compatibility with:
- FastAPI responses
- API lifespan loading
- AI search executors

---

## 6. Dataframe Loading
- Cleaned records are loaded into memory as dataframes.

### Reason
Avoid repeating expensive cleaning operations on every database query.

---

## 7. Data Consumption
The processed dataframe is used by:
- APIs
- AI search systems
