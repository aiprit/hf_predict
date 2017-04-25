import pandas as pd
import csv

df = pd.read_csv('patient_event_data.csv')

df.sort_values(['subject_id', 'admittime', 'seq_num'])
print(df.head())

patient_id_set = set(df['subject_id'])

print(len(patient_id_set))

result = []
for patient_id in patient_id_set:
    patient_data = df[df['subject_id'] == patient_id]
    events = [patient_data['hf'].values[0]]
    for event in list(patient_data['admittime']):
    # for event in list(patient_data['event_id']):
        events.append(event)
    if len(events) < 50:
        continue
    result.append(events)

print(len(result))

# with open("feature_construction_output_50_events.csv", "w") as f:
with open("feature_construction_output_50_dates.csv", "w") as f:
    writer = csv.writer(f)
    writer.writerows(result)
