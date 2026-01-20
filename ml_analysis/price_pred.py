from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.metrics import mean_absolute_error,r2_score, mean_squared_error
from sklearn.ensemble import HistGradientBoostingRegressor

from ml_analysis.data_cleaning.data_preprocesser import DataPreprocess
from manage_db.db_manager import DbManager

#loading clean data
db = DbManager("jp_realestate")
cleaner = DataPreprocess()

df = db.load_data()
df = cleaner.run_preprocessor(df)

#feature setup
target = "price_yen"

categorical_features = [
    "prefecture",
    "land_rights",
    "occupancy",
    "structure",
    "zoning",
    "transaction_type",
    "type",
    "ns_station_name"
]
numeric_features = [col for col in df.columns if col not in categorical_features + [target]]

#model layer preprocessing
numeric_transformer = Pipeline(steps=[
    ("imputer",SimpleImputer(strategy="median"))
])

categorical_transformer = Pipeline(steps=[
    ("imputer",SimpleImputer(strategy="most_frequent")),
    ("encoder",OneHotEncoder(handle_unknown="ignore",sparse_output=False))
])

preprocessor = ColumnTransformer(
    transformers=[
        ("num",numeric_transformer,numeric_features),
        ("cat",categorical_transformer,categorical_features)
    ]
)

#model pipeline
model = HistGradientBoostingRegressor(
    max_depth=6,
    learning_rate=0.05,
    max_iter=300,
    random_state=42
)

pipe = Pipeline(steps=[
    ("preprocess",preprocessor),
    ("model",model)
])

#Train and evaluate
x = df.drop(columns=[target])
y = df[target]

X_train,X_test,y_train,y_test = train_test_split(x,y,test_size=0.2,random_state=42)

pipe.fit(X_train,y_train)

preds = pipe.predict(X_test)

mae = mean_absolute_error(y_test, preds)
mse = mean_squared_error(y_test,preds)
r2 = r2_score(y_test, preds)



print(f"MAE: ¥{mae:,.0f}")
print(f"MSE: ¥{mse:,.0f}")
print(f"R2: {r2:.4f}")