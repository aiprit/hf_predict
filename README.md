# Predicting Onset heart failure from MIMIC III ICU dataset

To run the RNNs:  <br>
RNN_one_hot_vector.py: python RNN_one_hot_vector.py   [featurefile]   [outputnameforRNNmodel] <br>
RNN_one_hot_time_vector: python RNN_one_hot_time_vector.py   [featurefile]   [relatedtimefile]   [outputnameforRNNmodel] <br>
<br>
Baseline models are in ipython notebook format<br>
Featurefile is a csv with labels as 1st column and patient diagnositic events for the rest. <br><br>
MIMIC III dataset was uploaded and  transformed on  an SQL server using sql code from hf_predict.sql 
