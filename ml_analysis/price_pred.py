from manage_db.db_manager_v1 import DbManagerV1
from ml_analysis.data_cleaning.data_preprocesser import DataPreprocess
from sklearn.model_selection import train_test_split
from sklearn import metrics
import numpy as np

from catboost import CatBoostRegressor

from pathlib import Path

def load_clean_df():
    db = DbManagerV1("jp_realestate_v1")
    cleaner = DataPreprocess()
    df = db.load_data(include_expired=True)
    clean_df = cleaner.run_preprocessor(df)
    return clean_df

def load_model():
    root = Path(__file__).parents[1].resolve()
    model_path = root / "ml_analysis" / "models" / "catboost_real_estate.cbm"
    model = CatBoostRegressor()
    model.load_model(str(model_path))
    return model

def evaluate(model,x_val,y_val):
    y_pred = model.predict(x_val)

    y_pred = np.clip(y_pred,0,None)

    y_val_log = np.log1p(y_val)

    r2 = metrics.r2_score(y_val_log,y_pred)
    mae = metrics.mean_absolute_error(y_val_log, y_pred)
    mse = np.sqrt(metrics.mean_squared_error(y_val_log, y_pred))

    print(f"R2 : {r2}")
    print(f"mae : {mae}")
    print(f"rmse : {mse}")
    print(f"min target log : {y_val_log.min()} , max : {y_val_log.max()}")

def acc_test(df, model):
    X = df.drop(columns=["price_yen"])

    y = df["price_yen"]

    _, X_test, _, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42
    )

    evaluate(model,X_test,y_test)


if __name__ == "__main__":
    df = load_clean_df()
    model = load_model()
    acc_test(df,model)