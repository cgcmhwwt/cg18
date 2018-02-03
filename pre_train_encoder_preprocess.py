import os
import math
import pickle
import random
import json
import numpy as np

# ***** function


# split data into train/test/valid
def train_test_split(project_name, ratio, path):
	cur_path = path + project_name
	os.chdir(cur_path)
	file_list = os.listdir(cur_path)
	
	success = []
	failure = []

	for file in file_list:
	    if file.endswith('.json'):
	        try:
	            temp = json.load(open(file,'r', encoding = 'utf8'))
	            success.append(file)
	        except json.decoder.JSONDecodeError:
	            failure.append(file)
	del temp

	print('project:', project_name, '\nparse success?? :' , len(failure)==0, '\nproblems:', len(failure))
	total_num = len(success)
	train_num = math.floor(total_num * ratio[0])
	valid_num = math.floor(total_num * ratio[1])
	test_num  = total_num - train_num - valid_num

	assert train_num > 0
	assert valid_num > 0
	assert test_num > 0

	index = list(range(len(success)))
	random.shuffle(index)

	train_dict = {}
	valid_dict = {}
	test_dict = {}
	
	labels = set()

	for i in range(len(success)):
		file_index = index[i]
		file_name  = success[file_index]
		
		label = get_label(file_name)
		labels.add(label)


		if file_index < train_num :
			train_dict[file_name] = label
		elif file_index < train_num + valid_num :
			valid_dict[file_name] = label
		else:
			test_dict[file_name]  = label
	return train_dict, valid_dict, test_dict, labels


# get the classname as the label of json_file
def get_label(json_file_name):
	name = json_file_name
	names = json_file_name.split('-')
	label = names[0]
	return label


# save the labels and we may use the one-hot later
def save_labels(label):
	class_num = len(label)

	index = 0
	# get class array
	lb2id_dict = {}
	id2lb_dict = {}

	for label_name in label:
		lb2id_dict[label_name] = index
		id2lb_dict[index] = label_name
		index += 1
	return lb2id_dict, id2lb_dict


# get class num
def tag_num(lb2id_dict, id2lb_dict, json_dict):
	index_list = []
	for file_name in json_dict:
		label = json_dict[file_name]
		index = lb2id_dict[label]
		index_list.append(index)
	return index_list


# one hot
def one_hot_labels(label_list, fin_labels):
	class_num = len(fin_labels)
	tgt = np.array(label_list).reshape(-1)
	one_hot_tgt = np.eye(class_num)[tgt]
	return one_hot_tgt


# ****************************************************************
# ****************************************************************
# ****************************************************************

path = 'E:/parsetree/result1/'

project_list = os.listdir(path)
print('num of projects：',len(project_list),'\n')

ratio = [0.7, 0.15]

fin_labels = set()


train = {}
valid = {}
test  = {}

# 1st traversal
# get labels and split the data into train/valid/test dataset
for project in project_list:
	train_dict, valid_dict, test_dict, labels = train_test_split(project, ratio, path)
	
	# dict    key,value = file_name, label
	train[project], valid[project], test[project] = train_dict, valid_dict, test_dict

	num_a = len(labels)
	num_b = len(fin_labels)
	fin_labels = fin_labels | labels
	num_c = len(fin_labels)
	print(num_a, num_b, num_c)
	if num_a + num_b != num_c:
		print('*** *** *** *** ***')
		print('we have the same class name in the label,', 'current project is', project)
		print('the difference:', num_a + num_b - num_c)
		print('*** *** *** *** ***')

	print('split done, current project:', project, '\n')

lb2id_dict, id2lb_dict = save_labels(fin_labels)

print('+++ +++ +++ +++ DONE!!! +++ +++ +++ +++\n')
print('transforming the labels into one-hot vector......')
train_oh = {}
valid_oh = {}
test_oh  = {}

# 2nd travelsal
# get one-hot vector for classes in each project
for project in project_list:

	train_list = tag_num(lb2id_dict, id2lb_dict, train[project])
	valid_list = tag_num(lb2id_dict, id2lb_dict, valid[project])
	test_list  = tag_num(lb2id_dict, id2lb_dict,  test[project])

	train_vec = one_hot_labels(train_list, fin_labels)
	valid_vec = one_hot_labels(valid_list, fin_labels)
	test_vec  = one_hot_labels( test_list, fin_labels)

	# train_oh[project][i] = onehotvec for no.i method's class
	train_oh[project], valid_oh[project], test_oh[project] = train_vec, valid_vec, test_vec


# save it by pickle
os.chdir('E:/parsetree/result1/')
print('saving the data......')


print('------saving the split data......')
with open('train.pkl','wb') as outfile:
	pickle.dump(train, outfile)
with open('valid.pkl','wb') as outfile:
	pickle.dump(valid, outfile)
with open('test.pkl','wb') as outfile:
	pickle.dump(test, outfile)

print('------saving the index/label......')
with open('lb2id_dict.pkl','wb') as outfile:
	pickle.dump(lb2id_dict, outfile)
with open('id2lb_dict.pkl','wb') as outfile:
	pickle.dump(id2lb_dict, outfile)

print('------saving the one-hot vectors......')
with open('train_oh.pkl','wb') as outfile:
	pickle.dump(train_oh, outfile)
with open('valid_oh.pkl','wb') as outfile:
	pickle.dump(valid_oh, outfile)
with open('test_oh.pkl','wb') as outfile:
	pickle.dump(test_oh, outfile)

print('\n+++ +++ +++ +++ DONE!!! +++ +++ +++ +++\n')