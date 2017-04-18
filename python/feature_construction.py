import pandas as pd
import csv

df = pd.read_csv('patient_event_data.csv')
print(df.head())

patient_events = df.groupby('subject_id')['event_id']

patient_id_set = set(df['subject_id'])

print(len(patient_id_set))

result = []
for patient_id in patient_id_set:
    patient_data = df[df['subject_id'] == patient_id]
    events = list(patient_data['event_id'])
    result.append(events)

print(len(result))
with open("feature_construction_output.csv", "w") as f:
    writer = csv.writer(f)
    writer.writerows(result)
