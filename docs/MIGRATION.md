# Migration 

**jp_realestate -> jp_realestate_v1**

Date : starting(2026-05-14) / ending(....)

---

## Reason

- To resolve existing issues in the database schema as the stored data's quality is not enough to be usable and requires 1 - 2 more extra cleaning-processes
while loading. Due to this data cannot be directly interacted with due to necessary processes per query.

- Jsonb field **"data"** which is used to store scraped data contains important fields such as price , *unique constrain(data->>'url')* .


**Current solution:**
Currently the table data is pre-cleaned and loaded as dataframe which exist in cache memory in api , AI agent lifecycle. Which becomes efficient as db grows larger .

---

## Objectives 

- Take url and price out of jsonb(data) and make them individual fields .
- Store schema-normalized and query-ready data
- Optimize data querying .
- Reduce processes during data loading .

## Schema Changes 

### Current 
- id : Primary key
- source : Text
- scraped_at : Timestamp
- data : *Jsonb*
- status : Text
- last_update : Timestamp

**Unique index:** (data ->> 'url')

### Future
- id : Primary key
- source : Text
- scraped_at : TIMESTAMPTZ
- data : *Jsonb*
- status : Text
- last_update : TIMESTAMPTZ
- price_yen : BIGINT NOT NULL
- source_listing_id : BIGINT NOT NULL

**Unique Constraints:** UNIQUE (source,source_listing_id)

**Partial Index:**
For faster querying 
```sql
CREATE INDEX idx_active_listings 
ON jp_realestate_v1 (price_yen) 
WHERE status = 'active';
```

---

## Flow Changes 

### Current Flow
- [Flow doc](FLOW.md)

### Future Flow
- Data extraction
- Complete cleaning process
- Stored ready-to-use data
- Interact

---

## Affected Systems 

- [x] ai_agent/(nodes/search_executor.py ; agent_runtime.py)
- [x] manage_db/
- [x] ml_analysis/
- [x] scraper/ (cleaning,inserting process)
- [x] tests/
- [x] ui/backend/apis/data_querying.py

---

## Migration Strategy
- Create new table 
- Implement new schema 
- Test with sample existing data(from old table)
- Validate schema correctness
- Check data integrity (nulls, duplicates, casting)
- Migrate existing data
- Update affected system
- Test end-to-end system interaction
- Deploy


## Migration Status Checklist

- [x] Create new table
- [x] Implement schema
- [x] Create and run migration tests
- [x] Migrate existing data
- [x] Update application systems
- [ ] Deploy and validate