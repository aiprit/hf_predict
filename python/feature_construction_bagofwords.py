import numpy as np
import pandas as pd
import csv

df = pd.read_csv('patient_event_data.csv')
df.sort_values(['subject_id', 'admittime', 'seq_num'])
print(df.head(20))

patient_id_set = set(df['subject_id'])
event_set = set(df['event_id'])

# create dict for event_id to index
unique_event_ids = dict(zip(event_set, range(len(event_set))))

# create empty matrix where each column corresponds to an event_id, and the last column is 0 or 1 for HF label
result = np.empty([len(patient_id_set), len(event_set)])
last_col_idx = len(event_set) - 1

i = 0
for patient_id in patient_id_set:
    patient_data = df[df['subject_id'] == patient_id]
    hf = patient_data['hf'].values[0]
    
    for event in list(patient_data['event_id']):
        idx = unique_event_ids[event]
        result[i][idx] += 1

    # set last column with HF value
    result[i][last_col_idx] = hf

    # if np.sum(result[i]) < 50:
    #     continue
    for value in result[i]:
        if value > 0:
            print(value)

    i += 1

print(result)

# with open("feature_construction_output_50_events.csv", "w") as f:
with open("feature_construction_output_50_dates.csv", "w") as f:
    writer = csv.writer(f)
    writer.writerows(result)
