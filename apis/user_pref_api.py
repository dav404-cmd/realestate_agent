from fastapi import APIRouter
from utils.logger import get_logger

from manage_db.user_pref_db_manager import UserPreference , Preference

api_log = get_logger("UserPref")

router = APIRouter()

#todo : store the db conn in lifespan

@router.post("/insert_user_pref")
def insert_user_pref(pref : Preference):
    api_log.info("Received preference")
    try :
        db = UserPreference()
        _id = db.insert_pref(pref)
        api_log.info(f"Inserted pref for user : {_id}")
        return {
            "id" : _id
        }
    except Exception as e:
        api_log.exception(f"Error during insert : {e}")
        return {
            "error" : str(e)
        }
@router.post("/update_user_pref")
def update_user_pref(pref : Preference):
    api_log.info("Received preference update request.")
    try:
        db = UserPreference()
        _id = db.update_pref(pref)
        api_log.info(f"Preference updated for user : {_id}")
        return {
            "id": _id
        }
    except Exception as e :
        api_log.exception(f"Error during update : {e}")
        return {
            "error" : str(e)
        }

@router.get("/get_pref")
def get_user_pref(user_id:str):
    api_log.info(f"Received request to get user preference of : {user_id}")
    try:
        db = UserPreference()
        data = db.get_pref(user_id)
        return data
    except Exception as e :
        api_log.exception(f"Error during update : {e}")
        return {
            "error" : str(e)
        }
