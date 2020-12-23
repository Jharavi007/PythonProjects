a = [5, 4, 0, 6,-3,-5, 7, 7,-3,4]
a_dict = {}
for i in a:
    if i in a_dict:
        a_dict[i] +=1
    else:
        a_dict[i] = 1
count = 0
for key, value in a_dict.items():
    if value == 1:
        if count == 0:
            result = key
        if key > result:
            result = key
        count += 1
print(result)
