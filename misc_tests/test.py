flist = []

for i in range(10):
    flist.append(lambda x=i: print(i))

for i, f in enumerate(flist):
    flist[i]()
    f()
    print(flist[i], f)

for k in flist:
    print(k)
    k()

for i, f in enumerate(flist):
    flist[i]()
    f()
    print(flist[i], f)