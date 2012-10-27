import sys, os, sets

print sys.argv[1]
print sys.argv[2]

a = sets.Set()
for f in os.listdir(sys.argv[1]):
    a.add(f)
    
b = sets.Set()
for f in os.listdir(sys.argv[2]):
    b.add(f)
    
print a - b

print b - a