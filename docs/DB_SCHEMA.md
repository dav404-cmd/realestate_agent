# Database Scheme.

## Existing Tables 
- jp_realestate 
- users

---

## jp_realestate 
This database contains the scraped data from *realestate.co.jp* site .

**Schema:**
- id : Primary key
- source : Text
- scraped_at : TIMESTAMPTZ
- data : *Jsonb*
- status : Text
- last_update : TIMESTAMPTZ
- price_yen : BIGINT NOT NULL
- source_listing_id : BIGINT NOT NULL

**Unique Constraints:** UNIQUE (source,source_listing_id)

### data
This is a jsonb which contains all the extracted data . 

**Some of the data .**
- building_description
- building_name 
- potential_annual_rent
- investment_situation

*Others*
"date_updated","unit_number","unit_summary","url","next_update_schedule","landmarks","manager_style","manage_type","other_expenses","sell_situation","road_width","city","district", *etc*

### status
Stores the status of listings .

**Values** : active , expired 

### last_update
Stores date when the listing was last updated by updater .

**default** : scraped_at

---

## users.
This database contains the login data of users .

**Schema** 
- id : Primary key
- email : Text
- google_sub : Text 
- created_at : Timestamp 

---

## user_preference

This database contains the preference data of users . 
It has a table join  with users db vie id (uuid) . 

- id : Primary key
- user_name : Text
- user_id : UUID REFERENCE users(id)
- user_type : Text (investor,buyer,agent)
- property_type : Text (House, land , apartment, .)
- min_price : BIGINT
- max_price : BIGINT NOT
- target_price : BIGINT
- min_size : INT
- max_size : INT
- target_size : INT
- district : Text
- city : Text
- prefecture : Text
- min_land_area : INT
- max_land_area : INT
- target_land_area : INT
- structure : Text
- layout : Text
- direction_facing : Text 
- transaction_type :  Text
- occupancy : Text
- parking :Text
- investment_goal : Text (rental_apartment , resell) 
- living_goal : Text (live_alone,small_family[2-4], ...) 
- preference_weight : Jsonb 
- custom_pref : Jsonb (any other imported matches)
- ns_name : Text
- ns_distance_min : INT
- ns_mode : Text
- ns_line : Text


### Preference_weight
 
key (non-null column name of user_preference) : value (3 , -3)  
3 = must have  
2 = strongly preferred  
1 = preferred   
0 = ignore  
-1 = avoid  
-2 = strongly avoid  
-3 = exclude

```json
{
  "prefecture": 3,
  "parking" : 2,
  "layout" : 1 ,
  "structure" : -3
}
```

---


## jp_realestate_image

- id : Primary key 
- listing_id : Reference jp_realestate_v1(id)
- storage_path : TEXT
- image_url : TEXT
- image_order : INT

---

## agent_message

- id : Primary key

- thread_id : thread_id REFERENCES agent_threads(id)

- user_input
- response

- intent
- extracted_filters JSONB

- result_ids : JSONB [{id:int , score:int|float}]

- created_at TIMESTAMPTZ

---

## agent_thread 

- id UUID PRIMARY KEY
- user_id : REFERENCE users(id:uuid)
- title : TEXT
- created_at : TIMESTAMPTZ
- updated_at : TIMESTAMPTZ

---