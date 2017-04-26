# Predicting Onset heart failure from MIMIC III ICU dataset

To run the RNNs: <br>
RNN_one_hot_vector.py: python RNN_one_hot_vector.py [featurefile] [outputnameforRNNmodel] <br>
RNN_one_hot_time_vector: python RNN_one_hot_time_vector.py [featurefile] [relatedtimefile] [outputnameforRNNmodel] <br>

Featurefile is a csv with labels as 1st column and patient diagnositic events for the rest. 
