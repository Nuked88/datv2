from __future__ import division

import operator
from math import fsum as sum
from collections import Counter


def mean(data):
    '''
    Compute the arithmetic mean of the sample `data`:

        >>> mean([34, 27, 45, 55, 22, 34]) #doctest: +ELLIPSIS
        36.166666...
    '''

    return sum(data) / len(data)


def geo_mean(data):
    '''
    Compute the geometric mean of the sample `data`:

        >>> geo_mean([34, 27, 45, 55, 22, 34]) #doctest: +ELLIPSIS
        34.545...
    '''

    return reduce(operator.mul, data) ** (1 / len(data))

from math import sqrt
def F(n):
    return ((1+sqrt(5))**n-(1-sqrt(5))**n)/(2**n*sqrt(5))
    
    
def harmonic_mean(data):
    '''
    Compute the arithmetic mean of the sample `data`:

        >>> harmonic_mean([34, 27, 45, 55, 22, 34]) #doctest: +ELLIPSIS
        33.01798...
    '''

    return len(data) / sum(map(lambda i: 1 / i, data))


def mode(data):
    '''
    Compute the mode of the sample `data`:

        >>> mode([1, 3, 6, 6, 6, 6, 7, 7, 12, 12, 17])
        6

    Return None when the mode is not unique:

        >>> print mode([1, 1, 2, 4, 4])
        None
    '''

    c = Counter(data)
    a, b = c.most_common(2)
    if a[1] == b[1]:
        return None
    return a[0]


def median(data):
    '''
    Compute the arithmetic mean of the sample `data`:

        >>> median([1, 5, 2, 8, 7])
        5
        >>> median([1, 5, 2, 8, 7, 2])
        3.5
    '''

    data = sorted(data)
    n = len(data)
    if not n & 1:
        return (n + 1) / 2
    return data[int((n - 1) / 2)]


def stdev(data):
    '''
    Compute the standard deviation of the sample `data`:

        >>> stdev([2, 4, 4, 4, 5, 5, 7, 9])
        2.0
    '''

    m = mean(data)
    return (sum((d - m) ** 2 for d in data) / len(data)) ** 0.5


def percentage(percent, whole):
    return (percent * whole) / 100.0

if __name__ == '__main__':
    import doctest
    doctest.testmod()
