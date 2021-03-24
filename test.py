def print_w(t):
    print(t)


def p(func):

    for i in range(100):
        func(i)

p(print_w)