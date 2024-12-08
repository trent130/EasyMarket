""" 
applicable in devide and concur algorithms like binary search
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
