import torch
import torch.autograd as autograd
from torch.autograd import Variable
import torch.nn.functional as F

import numpy as np
import pickle
from gensim.models.keyedvectors import KeyedVectors

# hyper parameter
batch_size = 32
embedding_dim = 300
hiddenstate_dim = 300

# define the tree
class Tree(object):
    def __init__(self, nodetype = None, parent = None, data = None):
        self.root = nodetype
        self.child = []
        self.parent = parent
        self.data = None

# function about tree
def add_new_child(parent_tree):
    new_tree = Tree()
    new_tree.parent = parent_tree
    parent_tree.child.append(new_tree)
    return new_tree

def get_new_type(data):
    if type(data) == dict:
        if type(data['type']) == dict:
            temp = data['type']['type']
        if type(data['type']) == str:
            temp = data['type']        
        return temp
    
def tree_split(data, parent_tree, vocabulary, key = None):
    if type(data) == dict:
        if parent_tree.nodetype == 'root':
            nodetype = get_new_type(data)
            vocabulary[1].add(nodetype)
            parent_tree.nodetype = nodetype
        for key, data_key in data.items():            
            if key in ['comment','type']:
                continue
            else:
                new_tree = add_new_child(parent_tree)
                new_tree.nodetype = get_new_type(data_key)
                vocabulary[1].add(new_tree.nodetype)            
                tree_split(data_key, new_tree, vocabulary, key = key)
    
    if type(data) == list:
        new_tree = add_new_child(parent_tree)
        new_tree.nodetype = key
        vocabulary[1].add(key)
        for dataitem in data:
            tree_split(dataitem, new_tree, vocabulary)

    if type(data) == str:
        new_tree = add_new_child(parent_tree)
        if len(combine_name_split(data)) == 1:
            new_tree.nodetype = 'String'
            vocabulary[1].add('String')
            new_tree.data = data
        else:
            new_tree.nodetype = 'CombineName'
            vocabulary[1].add('CombineName')
            new_tree.data = []
            for word_temp in combine_name_split(data):
                vocabulary[0].add(word_temp)
                new_tree.data.append(word_temp)

# build vocabulary
def build_vocabulary(vocabulary):
	type_voc = vocabulary[1]
	word_voc = set()
	for key in vocabulary[0]:
		for word in key:
			word_voc.add(word)
	return word_voc, type_voc

# make embedding file
def make_embedding_file(word_voc, type_voc):
	word_vectors = KeyedVectors.load_word2vec_format('./GoogleNews-vectors-negative300.bin',binary = True)
	count = 0
	# word_embedding
	words = list(word_voc)
	embeddings = {}
	for i in range(len(words)):
		cur_wd = words[i]
		cur_id = index[i]
		if cur_wd in word_vectors.wv:
			cur_embedding = word_vectors.wv['cur_wd']
		else:
			cur_embedding = np.random.random(embedding_dim)
			cur_embedding.dtype = np.float32
			count += 1
		embeddings[cur_wd] = cur_embedding
		del cur_embedding

	print('words:',len(words), '  ', 'oov words:', count, '\n')
	
	# type_embedding
	types = list(type_voc)
	for i in range(len(types)):
		cur_tp = types[i]
		if cur_tp in word_vectors.wv:
			cur_embedding = word_vectors.wv['cur_tp']
		else:
			cur_embedding = np.random.random(embedding_dim)
			cur_embedding.dtype = np.float32
		embeddings[cur_tp] = cur_embedding

	with open('embedding.pkl','wb') as outfile:
		pickle.dump(embeddings, outfile)

# encoder
def get_tree_vector(tree, embedding, model):
	# Leaf, nodevec = embedding
	if tree.nodetype == 'String':
		node_vec = torch.from_numpy(embedding[tree.data])
		#node_vec = torch.unsqueeze(node_vec, dim=1)
		node_vec = Variable(node_vec, requires_grad=False)
		return node_vec

	# CombineName, nodevec = node_emb + subtree
	if tree.nodetype == 'CombineName'
		node_vec = embedding['CombineName']
		node_vec = Variable(node_vec, requires_grad=False)
		#node_vec = torch.unsqueeze(node_vec, dim=1)

		# init subtree_vec
		subtree_vec = np.zeros([embedding_dim])
		subtree_vec = torch.from_numpy(subtree_vec)
		for word in tree.data:
			subtree_vec += torch.from_numpy(embedding[word])
		subtree_vec = Variable(subtree_vec, requires_grad=False)
		subtree_vec = model(subtree_vec)
		node_vec += F.relu(subtree_vec)
		return node_vec

	# tree node, dict
	if tree.nodetype not in ['String','CombineName']:
		node_vec = embedding[tree.nodetype]
		node_vec = Variable(node_vec, requires_grad=False)
		#node_vec = torch.unsqueeze(node_vec, dim=1)

		# init subtree_vec
		subtree_vec = np.zeros([embedding_dim])
		subtree_vec = torch.from_numpy(subtree_tree)
		subtree_vec = Variable(subtree_vec, requires_grad=False)
		for child in tree.child:
			subtree_vec += get_tree_vector(child, embedding, W, b)
		subtree_vec = model(subtree_vec)
		node_vec += F.relu(subtree_vec)
		return node_vec			

# main
if __name__ == '__main__':
	# if we need to search for word embeddings
	t = 0

	if t == 0:
		print("making vocabulary......\n")
		voc1 = set()
		voc2 = set()
		voc2.add('root')
		voc = [voc1, voc2]
		for file in filelist :
		    if file in success:
		        json_data = json.load(open(file,'r'))
		        root = Tree()
		        root.nodetype = 'root'
		        tree_split(json_data, root, voc)
		word_voc, type_voc = build_vocabulary(voc)
		print("making word embedding file......\n")
		make_embedding_file(word_voc, type_voc)
	else:
		print("we already have the embeddings! \n")

	pkl_file = open('embedding.pkl', 'rb')
	embeddings = pickle.load(pkl_file)
	pkl_file.close()

	
	# define the linear model
	model = torch.nn.linear(embedding_dim, embedding_dim)
	
	# here the json--tree--vec, the vec is a variable
	# and we need to train the parameter in Linear model
	# in the decoder part
	vec = get_tree_vector(tree, embedding, model)
	