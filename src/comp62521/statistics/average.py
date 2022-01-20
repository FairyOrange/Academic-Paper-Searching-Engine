
def mean(X):
    n = len(X)
    if n > 0:
        return float(sum(X)) / float(len(X))
    return 0


def median(X):
    n = len(X)
    if n == 0:
        return 0
    L = sorted(X)
    m = int(n / 2)
    if n % 2:
        return L[m]
    return mean(L[m - 1:m + 1])


def mode(X):
    n = len(X)
    if n == 0:
        return []

    d = {}
    for item in X:
        if item in d:
            d[item] += 1
        else:
            d[item] = 1

    m = (0, 0)
    for key in d.keys():
        if d[key] > m[1]:
            m = ([key], d[key])
        elif d[key] == m[1]:
            m = (sorted(m[0] + [key]), d[key])
    return m[0]
