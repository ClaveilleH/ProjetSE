def f2(li):
    li.append(4)
    li += [5, 6]

def f1():
    li = [1, 2, 3]
    f2(li)

    return li

print(f1())