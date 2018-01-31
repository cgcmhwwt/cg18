import json
import os
import sys

path = "../mkdata/cocos2d-master-result"

def combine_name_split(a):
    temp = list(a)
    temp_list = list(range(len(temp)))
    words = []

    for i in range(len(temp)):
        character = temp[i]
        if character.islower():
            temp_list[i] = 1
        if character.isupper():
            temp_list[i] = 2
        if character.isnumeric():
            temp_list[i] = 3
        if character == '_':
            temp_list[i] = 4        
        if character == '$':
            temp_list[i] = 5

    word = []
    for i in range(len(temp)):  
        if word == []:
            if temp_list[i] in [4,5]:
                continue
            cond = temp_list[i]
            word.append(temp[i])
            if len(temp) == 1:
                words.append(''.join(word))
                return words
            else:
                continue
       
        if temp_list[i] == cond:
            word.append(temp[i])

        if temp_list[i] in [4,5]:
            words.append(''.join(word))
            word = []

        if cond == 3 and temp_list[i] in [1,2]:
            words.append(''.join(word))
            word = []
            word.append(temp[i])            
        if cond in [1,2] and temp_list[i] == 3:
            words.append(''.join(word))
            word = []
            word.append(temp[i])       
        if cond == 1 and temp_list[i] == 2:
            words.append(''.join(word))
            word = []
            word.append(temp[i])
        if cond == 2 and temp_list[i] == 1:
            word.append(temp[i])
        cond = temp_list[i]    
        if i == len(temp)-1:
            words.append(''.join(word))
    words = [word.lower() for word in words]
    return words

if __name__ == '__main__':
    '''     parse detect    '''
    success = []
    failure = []

    filelist = os.listdir(path)
    for file in filelist:
        if file.endswith('.json'):
            with open(os.path.join(path, file)) as f:
                try:
                    temp = json.load(f)
                    success.append(file)
                except json.decoder.JSONDecodeError:
                    failure.append(file)
    del temp

    print('parse failures:', len(failure))

    if len(failure) != 0:
        with open('namelist.txt', 'w') as f:
            for key in failure:
                f.write(key)
                f.write('\n')

'''     tree building   '''
class Tree(object):
    def __init__(self, nodetype = None, parent = None):
        self.root = nodetype
        self.child = []
        self.parent = parent

        
    def __iter__(self):
        return iter(self.child)
        
    
    def __type__(self):
        return self.nodetype
    

    def relation_iter(self):
        yield from self.child.items()
        
        
    def child(self):
        return self.child


def add_new_child(parent_tree):
    new_tree = Tree()
    new_tree.parent = parent_tree
    parent_tree.child.append(new_tree)
    return new_tree

def get_abbr_expansion_for_word(abbr_word, origin):
    # check if number
    try:
        int(abbr_word)
    except:
        pass
    else:
        return [abbr_word]

    # check if is arconym
    expansion = []
    l = 0
    for c in abbr_word:
        while l < len(origin) and origin[l][0] != c:
            l += 1
        if l >= len(origin):
            break
        expansion.append(origin[l])
        l += 1
    else:
        return expansion
    
    # check if is prefix of some word
    for word in origin:
        if word.startswith(abbr_word):
            return [word]

    # check if is just abbreviation of the word (some consonants of the word)
    for c in abbr_word:
        if c in ['a', 'e', 'i', 'o', 'u']:
            break
    else:
        for word in origin:
            l = 0
            for c in abbr_word:
                l = word.find(c, l)
                if l == -1:
                    break
                l += 1
            else:
                return [word[word.find(abbr_word[0]):]]

    return [abbr_word]

def get_abbr_expansion(abbr, origin):
    abbr = combine_name_split(abbr)
    origin = combine_name_split(origin)
    #print(abbr, origin, file=sys.stderr)

    expansions = {}

    for abbr_word in abbr:
        expansion = get_abbr_expansion_for_word(abbr_word, origin)
        if expansion != [abbr_word]:
            expansions[abbr_word] = expansion

    return expansions

def tree_split(data, parent_tree, vocabulary, abbr_expantion, key = None):
    new_tree = add_new_child(parent_tree)
    #print(new_tree.parent.nodetype)
    # 决定新树的nodetype
    if type(data) == dict:
        #print(data['type'])
        if type(data['type']) == dict:
            new_tree.nodetype = data['type']['type']
        if type(data['type']) == str:
            new_tree.nodetype = data['type']
        #print(data,'\n')
        vocabulary[1].add(new_tree.nodetype)

        # expand those abbreviations short for their type(Class) names
        # when they're declared
        try:
            if new_tree.nodetype == 'VariableDeclarationExpr':
                for variable in data['variables']:
                    if variable['type']['type'] == 'ClassOrInterfaceType':
                        class_name = variable['type']['name']['identifier']
                        variable_name = variable['name']['identifier']
                        expansion = get_abbr_expansion(variable_name, class_name)
                        for key, value in expansion.items():
                            abbr_expansion[key] = value
        except:
            json.dump(data, sys.stderr, indent=2)
            raise

        for key, data_key in data.items():            
            if key in ['comment','type']:
                pass
            else:
                tree_split(data_key, new_tree, vocabulary, abbr_expantion, key = key)
    
    if type(data) == list:
        new_tree.nodetype = key
        vocabulary[1].add(key)
        for dataitem in data:
            tree_split(dataitem, new_tree, vocabulary, abbr_expantion)

    if type(data) == str:
        new_tree.nodetype = 'string'
        if key in ['identifier', 'operator']:
            words = combine_name_split(data)
            for word in words:
                tree_split(word, new_tree, vocabulary, abbr_expantion)
        elif key == 'isVarArgs':
            pass
        else:
            vocabulary[0].add(data)

def visit_data(data, s):
    if type(data) == dict:
        for key in data:
            if key in ['comment','type']:
                continue

            if type(data[key]) == str:
                #print(data[key])
                if key == 'identifier':
                    print(data[key], combine_name_split(data[key]))
                    s[0].append(combine_name_split(data[key]))
                if key == 'isVarArgs':
                    s[1].append(data[key])    
                if key == 'operator':
                    s[2].append(combine_name_split(data[key]))
                    
            visit_data(data[key], s)
    if type(data) == str:
        pass
                
    if type(data) == list:
        for key in data:
            visit_data(key, s)
        

if __name__ == '__main__':
    s = [[],[],[]]
    for file in success:
        #print('***** %s *****'%file)
        with open(os.path.join(path, file)) as f:
            json_data = json.load(f)
        visit_data(json_data, s)

    total_abbr = 0
    for file in sorted(success):
        print('***** %s *****' % file)
        with open(os.path.join(path, file)) as f:
            json_data = json.load(f)
        voc1 = set()
        voc2 = set()
        voc2.add('root')
        voc = [voc1, voc2]
        abbr_expansion = {}
        root = Tree()
        root.nodetype = 'root'
        tree_split(json_data, root, voc, abbr_expansion)
        print(voc[0])
        print(abbr_expansion)
        if abbr_expansion:
            total_abbr += len(abbr_expansion)
            print(abbr_expansion, file=sys.stderr)
    print('total_abbr = {}'.format(total_abbr), file=sys.stderr)
