import pandas as pd
import numpy as np
import json
from statsmodels.tsa.arima.model import ARIMA

# Load the data from daily_scores.json
with open('daily_scores.json', 'r') as f:
    data = json.load(f)

df = pd.DataFrame(data, columns=["date", "score"])
df["date"] = pd.to_datetime(df["date"])
df.set_index("date", inplace=True)

# Fill in missing dates
idx = pd.date_range(df.index.min(), df.index.max())
df = df.reindex(idx, fill_value=np.nan)

# Fit ARIMA model (assuming parameters (1, 1, 1) are optimal)
model = ARIMA(df['score'], order=(1, 1, 1))
model_fit = model.fit()

# Predict values for the entire duration and fill NaN values
df['imputed_score'] = model_fit.predict(start=0, end=len(df))
df['score'].fillna(df['imputed_score'], inplace=True)

# Remove the 'imputed_score' column, we don't need it anymore
df.drop('imputed_score', axis=1, inplace=True)

# Prepare data for json dump: reset index and convert the DataFrame back to list of lists
output_data = df.reset_index().values.tolist()

# Convert datetime object to string, as json does not support datetime
output_data = [[str(date.date()), score] for date, score in output_data]

# Write to a new JSON file
with open('daily_scores_imputed.json', 'w') as f:
    json.dump(output_data, f, indent=4)
