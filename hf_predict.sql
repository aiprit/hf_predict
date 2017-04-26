CREATE TABLE lab_events
( row_id INT NOT NULL,
  subject_id INT NOT NULL,
  hadm_id INT NOT NULL,
  itemid INT NOT NULL,
  charttime DATETIME,
  value VARCHAR(50),
  valuenum DECIMAL,
  valueom VARCHAR(20),
  flag VARCHAR(40)
);

truncate table lab_events;

select count(*) from lab_events;


# ADMISSION, PATIENTS, ICUSTAYS, LABEVENTS, D_LABITEMS, DIAGNOSTIC_ICD, D_ICD_DIAGNOSES, and PRESCRIPTION


CREATE TABLE admissions (
  row_id int not null,
  subject_id int not null,
  hadm_id int not null,
  admittime datetime,
  dischtime datetime,
  deathtime datetime,
  admission_type varchar(30),
  admission_location varchar(50),
  discharge_location varchar(50),
  insurance varchar(30),
  language varchar(30),
  religion varchar(30),
  marital_status varchar(20),
  ethnicity varchar(30),
  edregtime datetime,
  edouttime datetime,
  diagnosis varchar(50),
  hospital_expire_flag int,
  has_chartevents_data int
);

# "ROW_ID","SUBJECT_ID","GENDER","DOB","DOD","DOD_HOSP","DOD_SSN","EXPIRE_FLAG"
create table patients (
  row_id int not null,
  subject_id int not null,
  gender varchar(5),
  dob datetime,
  dod datetime,
  dod_hosp datetime,
  dod_ssn varchar(10),
  expire_flag int
);

# "ROW_ID","SUBJECT_ID","HADM_ID","ICUSTAY_ID","DBSOURCE","FIRST_CAREUNIT","LAST_CAREUNIT","FIRST_WARDID","LAST_WARDID","INTIME","OUTTIME","LOS"
create table icustays (
  row_id int not null,
  subject_id int not null,
  hadm_id int not null,
  icustay_id int not null,
  dbsource varchar(20),
  first_careunit varchar(20),
  last_careunit varchar(20),
  first_wardid int not null,
  last_wardid int not null,
  intime datetime,
  outtime datetime,
  los decimal
);

# ROW_ID","ITEMID","LABEL","FLUID","CATEGORY","LOINC_CODE"
create table d_labitems (
  row_id int not null,
  itemid int not null,
  label varchar(100),
  fluid varchar(100),
  category varchar(50),
  loinc_code varchar(50)
);


select count(*) from diagnostic_icd;
select * from diagnostic_icd;

select COUNT(*) AS row_count from (
  SELECT
    subject_id,
    icd9
  FROM diagnostic_icd
  GROUP BY subject_id, icd9
);

select count(*) from PRESCRIPTIONS;


drop table diagnostic_icd;


select * from d_icd_diag;
select * from d_icd_diag where icd9 like '40301';

select * from DIAGNOSES_ICD;


UPDATE DIAGNOSES_ICD SET ["ICD9_CODE"] = REPLACE( ["ICD9_CODE"],'"','');


select diags.*, ddi.*
from DIAGNOSES_ICD diags
join d_icd_diag ddi ON ddi.icd9 = diags.["ICD9_CODE"];

create view full_diagnostics as (
  select diags.*, ddi.*
  from DIAGNOSES_ICD diags
  join d_icd_diag ddi ON ddi.icd9 = diags.["ICD9_CODE"]
);

drop view full_diagnostics;


select * from full_diagnostics;

select * from admissions;

select patients.*, admissions.admittime, admissions.dischtime, full_diagnostics.*
FROM patients
JOIN admissions on admissions.subject_id = patients.subject_id
LEFT JOIN full_diagnostics on full_diagnostics.["SUBJECT_ID"] = patients.subject_id;


select patients.subject_id,
  fd.icd9,
  fd.["HADM_ID"] as hadm_id,
  fd.["SEQ_NUM"] as seq_num,
  fd.short_title
from patients
join full_diagnostics fd on fd.["SUBJECT_ID"] = patients.subject_id;

create view patient_diagnosis as (
  select patients.subject_id,
  fd.icd9,
  fd.["HADM_ID"] as hadm_id,
  fd.["SEQ_NUM"] as seq_num,
  fd.short_title
from patients
join full_diagnostics fd on fd.["SUBJECT_ID"] = patients.subject_id
);


select patients.subject_id, adm.hadm_id, adm.admittime, adm.dischtime
from patients
join admissions adm on adm.subject_id = patients.subject_id;

create view patient_admissions as (
  select patients.subject_id, adm.hadm_id, adm.admittime, adm.dischtime
  from patients
  join admissions adm on adm.subject_id = patients.subject_id
);

select * from prescription;

select count(*) from PRESCRIPTIONS;




select * from prescription;

create view patient_rx as (
  SELECT
    patients.subject_id,
    rx.startdate,
    rx.enddata,
    rx.drug_type,
    rx.drug_name_poe,
    rx.drug_name_generic,
    rx.formulary_drug_df,
    rx.gsn,
    rx.ndc
  FROM patients
    JOIN prescription rx ON rx.subject_id = patients.subject_id
);


create view hf_diagnosed_patients as (
  SELECT *
  FROM patient_diagnosis
  WHERE icd9 IN ('39891', '40201', '40211', '40291', '40401', '40403', '40411', '40413', '40491', '40493',
                 '42800', '42810', '42820', '42821', '42822', '42823', '42830', '42831', '42832', '42833',
                 '42840', '42841', '42842', '42843', '42890')
);

create view non_hf_diagnosed_patients as (
    select *
    from patient_diagnosis
    where icd9 not in ('39891', '40201', '40211', '40291', '40401', '40403', '40411', '40413', '40491', '40493',
                       '42800', '42810', '42820', '42821', '42822', '42823', '42830', '42831', '42832', '42833',
                       '42840', '42841', '42842', '42843', '42890')
);



select count(distinct patients.subject_id) from patients;

select * from hf_diagnosed_patients where subject_id = 249;

select * from patients_with_threeplus_hf_diagnoses where subject_id = 249;

create view patients_with_threeplus_hf_diagnoses as (
  SELECT
    subject_id,
    count(subject_id) AS subj_count
  FROM hf_diagnosed_patients
  GROUP BY subject_id
  HAVING count(subject_id) >= 3
);

create view patients_with_oneplus_hf_diagnoses as (
  SELECT
    subject_id,
    count(subject_id) AS subj_count
  FROM hf_diagnosed_patients
  GROUP BY subject_id
  HAVING count(subject_id) >= 1
);

select count(*) from patients_with_oneplus_hf_diagnoses;

select * from lab_events;


delete from lab_events where row_id in (
  select row_id
  from lab_events
  group by row_id
  having count(row_id) > 1
);


With cte AS
(select row_id
  from lab_events
  group by row_id
  having count(row_id) > 1)
SELECT COUNT(*)
FROM cte;

select count(*) from lab_events;


select * from patients_with_threeplus_hf_diagnoses;

select *
from patient_diagnosis pd
join patients_with_threeplus_hf_diagnoses pt on pt.subject_id = pd.subject_id;


create view hf_encounters as (
  select subject_id, fd.["HADM_ID"] as hadm_id, fd.["SEQ_NUM"] as seq_num
  from patients_with_threeplus_hf_diagnoses pat
  join full_diagnostics fd on fd.["SUBJECT_ID"] = pat.subject_id
  where fd.icd9 in ('39891', '40201', '40211', '40291', '40401', '40403', '40411', '40413', '40491', '40493',
                   '42800', '42810', '42820', '42821', '42822', '42823', '42830', '42831', '42832', '42833',
                   '42840', '42841', '42842', '42843', '42890')
);

drop view hf_encounters;


select subject_id, fd.["HADM_ID"] as hadm_id, fd.["SEQ_NUM"] as seq_num
from patients_with_threeplus_hf_diagnoses pat
join full_diagnostics fd on fd.["SUBJECT_ID"] = pat.subject_id
where fd.icd9 in ('39891', '40201', '40211', '40291', '40401', '40403', '40411', '40413', '40491', '40493',
                 '42800', '42810', '42820', '42821', '42822', '42823', '42830', '42831', '42832', '42833',
                 '42840', '42841', '42842', '42843', '42890');


select
  adm.subject_id,
  min(adm.hadm_id) as min_hadm_id,
  max(adm.hadm_id) as max_hadm_id,
  min(adm.admittime) as min_admittime,
  max(adm.admittime) as max_admittime,
  min(adm.dischtime) as min_dischtime,
  max(adm.dischtime) as max_dischtime
from admissions adm
join hf_encounters hfe on hfe.subject_id = adm.subject_id and hfe.hadm_id = adm.hadm_id
group by adm.subject_id;

select
  adm.subject_id,
  adm.hadm_id,
  adm.admittime,
  adm.dischtime
from admissions adm
join hf_encounters hfe on hfe.subject_id = adm.subject_id and hfe.hadm_id = adm.hadm_id
order by subject_id, admittime;


select subject_id, gender, dob from patients;

select * from control_patients
where subject_id in (select subject_id from patient_hfdx);

select * from control_patients;

select * from prescription;
select * from DIAGNOSES_ICD;

select * from full_diagnostics;

alter table prescription
    add event_id varchar(50);

update prescription set event_id = CONCAT('MED',gsn);

alter table DIAGNOSES_ICD
    add event_id varchar(50);

update DIAGNOSES_ICD set event_id = CONCAT('DIAG', ["ICD9_CODE"])

select ["SUBJECT_ID"], ["HADM_ID"], icd9, short_title, event_id, ["SEQ_NUM"] from full_diagnostics;

select subject_id, hadm_id, gsn, formulary_drug_df,event_id from prescription;

select * from patient_hfdx;
select * from control_patients;


create view all_events as (
  (SELECT
     ["SUBJECT_ID"] AS subject_id,
     ["HADM_ID"]    AS hadm_id,
     CAST(fd.event_id AS CHAR(50)) 'event_id',
     ["SEQ_NUM"]    AS seq_num
   FROM full_diagnostics fd
  )
    UNION
  (
    SELECT
      row_id as seq_num,
      hadm_id,
      subject_id,
     CAST(p.event_id as CHAR(50)) 'event_id'
    FROM prescription p
  )
);

Select * into new_table  from  old_table

drop view all_events;

select * from all_events;



SELECT * INTO all_events FROM (
  SELECT
     ["SUBJECT_ID"] AS subject_id,
     ["HADM_ID"]    AS hadm_id,
     CAST(fd.event_id AS CHAR(50)) 'event_id',
     ["SEQ_NUM"]    AS seq_num
   FROM full_diagnostics fd
  UNION All
  SELECT
      row_id as seq_num,
      hadm_id,
      subject_id,
     CAST(p.event_id as CHAR(50)) 'event_id'
    FROM prescription p
) as tmp


drop table all_events;


(select pat.subject_id, all_e.event_id, all_e.hadm_id, all_e.seq_num, adm.admittime, '1' as hf
  from patient_hfdx pat
  join (SELECT
         ["SUBJECT_ID"] AS subject_id,
         ["HADM_ID"]    AS hadm_id,
         event_id,
         ["SEQ_NUM"]    AS seq_num
        FROM full_diagnostics fd
        UNION All
        SELECT
          subject_id,
          hadm_id,
          event_id,
          row_id as seq_num
        FROM prescription p) all_e on all_e.subject_id = pat.subject_id
  join admissions adm on adm.hadm_id = all_e.hadm_id
  where event_id != 'MED' and adm.admittime <= pat.hfdx
    UNION ALL
  select pat.subject_id, all_e.event_id, all_e.hadm_id, all_e.seq_num, adm.admittime, '0' as hf
  from control_patients pat
  join (SELECT
         ["SUBJECT_ID"] AS subject_id,
         ["HADM_ID"]    AS hadm_id,
         event_id,
         ["SEQ_NUM"]    AS seq_num
        FROM full_diagnostics fd
        UNION All
        SELECT
          subject_id,
          hadm_id,
          event_id,
          row_id as seq_num
        FROM prescription p) all_e on all_e.subject_id = pat.subject_id
  join admissions adm on adm.hadm_id = all_e.hadm_id
  where event_id != 'MED' and adm.admittime <= pat.hdfx
);


select count(distinct pat.subject_id)
  from control_patients pat
  join (SELECT
         ["SUBJECT_ID"] AS subject_id,
         ["HADM_ID"]    AS hadm_id,
         event_id,
         ["SEQ_NUM"]    AS seq_num
        FROM full_diagnostics fd
        UNION All
        SELECT
          subject_id,
          hadm_id,
          event_id,
          row_id as seq_num
        FROM prescription p) all_e on all_e.subject_id = pat.subject_id
  join admissions adm on adm.hadm_id = all_e.hadm_id
  where event_id != 'MED' and adm.admittime <= pat.hdfx;



select count(distinct subject_id) from control_patients;


truncate table control_patients;
truncate table patient_hfdx;

select * from control_patients;