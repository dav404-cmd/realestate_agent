# Database Scheme.

## Existing Tables 
- jp_realestate 
- users

## jp_realestate 
This database contains the scraped data from *realestate.co.jp* site .

`!! Expected to change due to issues with date quality.[currently requires a cleaning function at the loading period]`

**Schema:**
- id : Primary key
- source : Text
- scraped_at : Timestamp
- data : *Jsonb*
- status : Text
- last_update : Timestamp

### source 
Stores the originating platform name for the scraped listing.

Example:
- realestate.co

Used for:
- source tracking
- multi-platform expansion support

### scraped_at 
Contains the data at which the listing was scraped . 

### data
This is a jsonb which contains all the extracted data . This currently includes important infos such as price and urls
which is expected to change due to performance issues and add complexity .

**Some of the data .**
- url (also the unique value)
- price
- building_description
- building_name 
- potential_annual_rent
- investment_situation

*Others*
"date_updated","unit_number","unit_summary","url","next_update_schedule","landmarks","manager_style","manage_type","other_expenses","sell_situation","road_width","city","district", *etc*

#### Unique Index
- `data->>'url'` should remain unique to avoid duplicate listings

### status
Stores the status of listings .

**Values** : active , expired 

### last_update
Stores date when the listing was last updated by updater .

**default** : scraped_at

## users.
This database contains the login data of users .

**Schema** 
- id : Primary key
- email : Text
- google_sub : Text 
- created_at : Timestamp 
