import pandas as pd
import numpy as np
import sqlalchemy as sa
from sklearn.neighbors import NearestNeighbors
from datetime import datetime


case_df = pd.read_csv('case_patients.csv', header=None, names=['subject_id', 'hadm_id', 'hdfx'])
knn_df = pd.read_csv('patient_knn_data.csv')


def calculate_age(born):
    future_date = datetime.strptime('2217-04-14', '%Y-%m-%d')
    born = datetime.strptime(born, '%Y-%m-%d %H:%M:%S.%f')
    return future_date.year - born.year - ((future_date.month, future_date.day) < (born.month, born.day))

# create age column from dob
knn_df['age'] = knn_df['dob'].apply(calculate_age)
print(knn_df['age'].max())
print(knn_df['age'].min())
knn_df['gender'] = knn_df['gender'].apply(lambda x: 1 if x == 'M' else 0)

# remove case patients before fitting KNN
print(knn_df.shape)
case_patient_ids = set(case_df['subject_id'])
mask = np.logical_not(knn_df['subject_id'].isin(case_patient_ids))
fit_df = knn_df[mask]
print(fit_df.shape)

mask = knn_df['subject_id'].isin(case_patient_ids)
test_df = knn_df[mask]
print(test_df.shape)

# get the 9 closest patients by age and sex
X = fit_df[['gender', 'age']].as_matrix()
knn_mdl = NearestNeighbors(50).fit(X)

patient_id_set = set()

print(fit_df.head())

control_patient_rows = []
for case in list(case_patient_ids):
    knn_data = knn_df[knn_df['subject_id'] == case][['gender', 'age']].as_matrix()
    distances, indices = knn_mdl.kneighbors(knn_data)
    hdfx = case_df[case_df['subject_id'] == case]['hdfx'].values[0]

    control_count = 0
    for idx in indices[0]:

        if control_count == 10:
            break

        patient_row = list(fit_df.iloc[idx])
        subject_id = patient_row[0]
        gender = patient_row[1]
        dob = patient_row[2]
        age = patient_row[3]

        patient_row_dict = {
            'subject_id': subject_id,
            'gender': gender,
            'dob': dob,
            'age': age,
            'hdfx': hdfx
        }

        if subject_id in patient_id_set:
            print('Duplicate control patient')
            continue

        patient_id_set.add(subject_id)
        control_count += 1

        control_patient_rows.append(patient_row_dict)

control_patients = pd.DataFrame(control_patient_rows)
# print('control patients df')
print(control_patients.head(10))
control_patients.to_csv('control_patients.csv')
