"""
time increases linearly while the program continues to run 

Assume we have a item within an array and the array is in random order but we have to find it, so we start withthe item at the first index while comparing it with the target and run it iteractively until we find it, if not we return a -1, if the indexes have ended and still we do not have the expected outcome we want.
"""

def sum_array(arr):
    total = 0
    for num in arr:
        total += num

    return total

print(sum_array([1, 2, 3, 4, 5, 6]))


# approach two - Linear search algorithm
def linearSearch(array, n, x):
    for i in range(0, n):
        if (array[i] == x:
                return i
    return -1
