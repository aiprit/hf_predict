import pandas as pd
import numpy as np
import sqlalchemy as sa
from sklearn.neighbors import NearestNeighbors
from datetime import datetime


case_df = pd.read_csv('output.csv', header=None, names=['subject_id', 'hadm_id', 'hdfx'])
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
knn_mdl = NearestNeighbors(9).fit(X)

control_patients = pd.DataFrame()
for case in list(case_patient_ids):
    knn_data = knn_df[knn_df['subject_id'] == case][['gender', 'age']].as_matrix()
    distances, indices = knn_mdl.kneighbors(knn_data)
    hdfx = case_df[case_df['subject_id'] == case]['hdfx'].values[0]
    for idx in indices:
        patient_row = fit_df.iloc[idx]
        patient_row['hdfx'] = hdfx
        control_patients = control_patients.append(patient_row)


print('control patients df')
print(control_patients.head(10))
control_patients.to_csv('control_patients.csv')
print(control_patients.shape)