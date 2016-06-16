'''
Created on 21 de abr de 2016

@author: Filipe Damasceno
'''
import matplotlib.pyplot as plt
import random
from copy import deepcopy
vetor = [1,2,3,4,5,6,7]

p = plt
for i in range(10):
    random.shuffle(vetor)
    v1 = deepcopy(vetor) 
    random.shuffle(vetor)
    v2 = deepcopy(vetor) 
    p.plot(v1,v2, label=str(i))
p.xlabel("Geracoes")
p.ylabel("aproximacao")
p.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3,
           ncol=2, mode="expand", borderaxespad=0.)
p.show()
class coisa():
    
    def __init__(self,a,b):
        self.a=a
        self.b=b

vet = [coisa(1,4),coisa(1,3),coisa(2,2),coisa(1,1),coisa(1,6),coisa(1,5)]

vet.sort(key=lambda a: a.b)
for i in vet:
    print(i.a,i.b)
print("__"*20)
vet.sort(key=lambda b: b.a)
for i in vet:
    print(i.a,i.b)


a = set()
a.add([1,2,3,4,5])
b = [1,2,3,4,5]

print(b in a)

