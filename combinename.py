# for the identifer like allFound
# we should add the special node named "CombineName"
# the allFound node will be replaced by node CombineName
# and the Combine Node will get several child nodes
# in this example they are "all" and "found"


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
        
        # 空词状态的cond 只可以是upper，lower，123        
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

        # 相同的类型肯定是直接append        
        if temp_list[i] == cond:
            word.append(temp[i])

        # 遇到字符立刻停止
        if temp_list[i] in [4,5]:
            words.append(''.join(word))
            word = []
        
        # 不同的类型： 数字转字母，字母转数字，大写转小写，小写转大写
        if cond == 3 and temp_list[i] in [1,2]:
            words.append(''.join(word))
            word = []
            word.append(temp[i])            
            
        if cond in [1,2] and temp_list[i] == 3:
            words.append(''.join(word))
            word = []

            word.append(temp[i])       


#*************************************        
        # 大写接大写接小写
        if cond == 2 and temp_list[i] == 2:
            if temp_list[i+1] == 1:
                word.pop()
                words.append(''.join(word))
                word = []
                word.append(temp[i])
#*************************************


        # 小写转大写
        if cond == 1 and temp_list[i] == 2:
            words.append(''.join(word))
            word = []
            word.append(temp[i])
        
        # 大写转小写
        if cond == 2 and temp_list[i] == 1:
            word.append(temp[i])
    
        # 更新状态
        cond = temp_list[i]    
    
        # 终止
        if i == len(temp)-1:
            words.append(''.join(word))
    

    words = [word.lower() for word in words]
    return words

w = ['IOException','streamIOInput','IOStream']

for word in w:
    words = combine_name_split(word)
    print(words)
