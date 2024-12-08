""" 
applicable in devide and concur algorithms like binary search

This is a binary search algorithm - this cut down the search to half as soon as it finds the middle ground of a sorted list. The middle element is looked at to check if it is greater than or less than the value to be searched. Accordingly, a search is done in either halves of the given list.
"""

def binary_search(arr, target):
    low, high = 0,len(arr) - 1
    while low <= high:
        mid = (low + high)
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            low = mid + 1
        else:
            high = mid -1
    return -1
print(binary_search([1, 2, 3, 4, 5, 6,], 5))
