import pandas as pd

# Load and preview
df = pd.read_csv('data/raw/superstore.csv', encoding='latin-1')

print("Shape:", df.shape)
print("\nColumns:", list(df.columns))
print("\nFirst 3 rows:")
print(df.head(3))
print("\nNull values:")
print(df.isnull().sum())