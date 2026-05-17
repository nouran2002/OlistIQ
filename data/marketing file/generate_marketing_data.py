import pandas as pd
import numpy as np


months = pd.period_range(start='2016-09', end='2018-10', freq='M')

marketing_records = []
for month in months:
    marketing_records.append({'month_period': str(month), 'channel': 'Google_Ads', 'spend': np.random.randint(10000, 20000)})
    marketing_records.append({'month_period': str(month), 'channel': 'Facebook_Ads', 'spend': np.random.randint(8000, 15000)})

#Save as CSV file 
marketing_df = pd.DataFrame(marketing_records)
marketing_df.to_csv('marketing_spend.csv', index=False)
print("Saved marketing_spend.csv successfully")
