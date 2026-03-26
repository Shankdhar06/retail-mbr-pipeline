

import pandas as pd
import pymysql
from sqlalchemy import create_engine
from sqlalchemy.engine import URL
from sqlalchemy import text

# ------------------------------------------------
# Connect to MySQL
# ------------------------------------------------

url = URL.create(
    drivername="mysql+pymysql",
    username="root",
    password="Anubhav@25",
    host="localhost",
    database="retail_mbr"
)

engine = create_engine(url)

# ------------------------------------------------
# Load raw CSV
# ------------------------------------------------
df = pd.read_csv('data/raw/superstore.csv', encoding='latin-1')

# Clean column names — remove spaces
df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_').str.replace('-', '_')

print("Columns after cleaning:", list(df.columns))
print("Shape:", df.shape)

# ------------------------------------------------
# Load dim_customer
# ------------------------------------------------
existing_ids = pd.read_sql("SELECT customer_id FROM dim_customer", engine)
dim_customer = df[['customer_id', 'customer_name', 'segment',
                    'city', 'state', 'region', 'country']].drop_duplicates()

dim_customer['customer_id'] = dim_customer['customer_id'].astype(str).str.strip()
existing_ids['customer_id'] = existing_ids['customer_id'].astype(str).str.strip()
existing_id_set = set(existing_ids['customer_id'])

dim_customer_new = dim_customer[
    ~dim_customer['customer_id'].isin(existing_id_set)
]

dim_customer_new = dim_customer_new.drop_duplicates(subset=['customer_id'])

dim_customer_new.to_sql(
    'dim_customer',
    engine,
    if_exists='append',
    index=False
)

print(f"✅ New customers inserted: {len(dim_customer_new)}")
print(f"⏭️ Skipped existing customers: {len(dim_customer) - len(dim_customer_new)}")

print(len(dim_customer))