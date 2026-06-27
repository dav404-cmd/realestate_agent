import psycopg2
from psycopg2.extras import RealDictCursor,Json

from dotenv import load_dotenv
import os

from pydantic import BaseModel
from typing import Optional,Dict,Any

class Preference(BaseModel):
    user_id : str

    user_name : Optional[str] = None
    user_type : Optional[str] = None

    property_type : Optional[str] = None

    min_price : Optional[int] = None
    max_price : Optional[int] = None
    target_price : Optional[int] = None

    min_size : Optional[int] = None
    max_size : Optional[int] = None
    target_size : Optional[int] = None

    min_land_area : Optional[int] = None
    max_land_area :  Optional[int] = None
    target_land_area : Optional[int] = None

    prefecture : Optional[str] = None
    city : Optional[str] = None
    district : Optional[str] = None

    structure: Optional[str] = None
    layout: Optional[str] = None
    direction_facing : Optional[str] = None

    occupancy : Optional[str] = None
    transaction_type : Optional[str] = None
    parking : Optional[str] = None

    investment_goal : Optional[str] = None
    living_goal : Optional[str] = None

    ns_name : Optional[str] = None
    ns_distance_min : Optional[int] = None
    ns_mode : Optional[str] = None
    ns_line : Optional[str] = None

    preference_weight : Optional[Dict[str,int]] = None
    custom_pref : Optional[Dict[str,Any]] = None

load_dotenv()
class UserPreference:
    def __init__(self):
        self.conn = psycopg2.connect(
            dbname=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT")
        )
        self.cursor = self.conn.cursor(cursor_factory=RealDictCursor)

    def close_conn(self):
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()

    def create_table(self):
        query = """
        CREATE TABLE IF NOT EXISTS user_preference (
            id SERIAL PRIMARY KEY,

            user_id UUID NOT NULL UNIQUE,
            user_name TEXT,

            user_type TEXT,

            property_type TEXT,

            min_price BIGINT,
            max_price BIGINT,
            target_price BIGINT,

            min_size INT,
            max_size INT,
            target_size INT,

            district TEXT,
            city TEXT,
            prefecture TEXT,

            min_land_area INT,
            max_land_area INT,
            target_land_area INT,

            structure TEXT,
            layout TEXT,

            direction_facing TEXT,

            transaction_type TEXT,
            occupancy TEXT,
            parking TEXT,

            investment_goal TEXT,
            living_goal TEXT,

            preference_weight JSONB DEFAULT '{}'::jsonb,
            custom_pref JSONB DEFAULT '{}'::jsonb,

            ns_name TEXT, 
            ns_distance_min INT,
            ns_mode TEXT,
            ns_line TEXT,

            created_at TIMESTAMPTZ DEFAULT NOW(),
            updated_at TIMESTAMPTZ DEFAULT NOW(),

            CONSTRAINT fk_user_preference_user
                FOREIGN KEY (user_id)
                REFERENCES users(id)
                ON DELETE CASCADE
        );
        """

        self.cursor.execute(query)
        self.conn.commit()
        print("table created")

    def insert_pref(self,pref: Preference):
        data = pref.model_dump(exclude_none=True)

        for field in ("preference_weight", "custom_pref"):
            if field in data:
                data[field] = Json(data[field])

        columns = (", ").join(data.keys())
        placeholders = (", ").join(["%s"]*len(data))
        values = list(data.values())
        query = f"""
        INSERT INTO user_preference
        ({columns})
        VALUES ({placeholders})
        RETURNING id
        """
        self.cursor.execute(query,values)
        _id = self.cursor.fetchone()["id"]
        self.conn.commit()
        if _id:
            return _id
        return None


    def update_pref(self, new_pref: Preference, user_id: str):

        data = new_pref.model_dump(exclude_none=True,exclude={"user_id"})

        for field in ("preference_weight", "custom_pref"):
            if field in data:
                data[field] = Json(data[field])

        if not data:
            return

        set_clause = ", ".join(
            f"{column} = %s"
            for column in data.keys()
        )

        values = list(data.values())
        values.append(user_id)

        query = f"""
        UPDATE user_preference
        SET {set_clause} , updated_at = NOW()
        WHERE user_id = %s
        RETURNING id
        """

        self.cursor.execute(query, values)
        if self.cursor.rowcount == 0:
            raise ValueError(
                f"No preference found for user {user_id}"
            )
        _id = self.cursor.fetchone()["id"]
        self.conn.commit()
        if _id :
            return _id
        return None

    def get_pref(self,user_id : str):
        query = """
        SELECT * FROM user_preference 
        WHERE user_id = %s 
        """
        self.cursor.execute(query,(user_id,))
        prefs = self.cursor.fetchone()
        return prefs

if __name__ == "__main__":
    db = UserPreference()
    test_pref = Preference(
        user_id = "",
        max_price= 24249450,
        target_price= 16166300,
        user_name= "dom",
        user_type= "buyer",
        property_type="house",
        preference_weight= {
            "property_type" : 3,
            "max_price" : 2
        }
    )
    data = db.get_pref("dbb2b64d-4080-4294-963b-c3cd0178b6c8")
    print(data)
    db.close_conn()