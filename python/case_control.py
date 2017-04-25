import csv
from datetime import datetime

results = []
csv_rows = []
with open('hf_patient_enctrs.csv') as csvfile:
    reader = csv.reader(csvfile)

    for row in reader:
        csv_rows.append(row)


cur_patient_id = ''
i = 1
while i < len(csv_rows):
    row = csv_rows[i]
    patient_id = row[0]
    if patient_id == cur_patient_id:
        i += 1
        continue
    cur_patient_id = patient_id

    first_enctr_date = row[2]

    # next_row = csv_rows[i + 1]
    # second_enctr_date = next_row[2]
    #
    # d1 = datetime.strptime(first_enctr_date, "%Y-%m-%d %H:%M:%S.%f")
    # d2 = datetime.strptime(second_enctr_date, "%Y-%m-%d %H:%M:%S.%f")

    # diff = d2.year - d1.year
    hfdx_date = first_enctr_date
    # if diff >= 1:
    #     hfdx_date = second_enctr_date

    result_row = [patient_id, row[1], hfdx_date]
    results.append(result_row)
    print(result_row)

with open("case_patients.csv", "w") as f:
    writer = csv.writer(f)
    writer.writerows(results)
