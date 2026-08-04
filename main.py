a = (1, 2)
arr = [(1, 2), (2, 3), (3, 4)]
while a in arr:
    a = (a[0]+1, a[1]+1)
print(a)