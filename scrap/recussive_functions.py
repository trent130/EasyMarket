# for fibonacci series
# def fibonacci(n):
#      base function
#     if n == 0:
#         return 0
#     elif n == 1:
#         return 1
#      recusive function
#     return fibonacci(n -1) + fibonacci(n -2)

# print(fibonacci(10))

"""
this is very ineficient in the of calculation repetitions( one 
can use memoization to optimize)
"""

# example of memoization tavoid repeated calls of the same function thu ensuring that only one fibonacci is run once
def fibonacci_memo(n, memo = {}):
    if n in memo:
        return memo[n]
    if n == 0:
        return 0
    elif n == 1:
        return 1
    memo[n] = fibonacci_memo(n-1, memo) + fibonacci_memo(n - 2, memo)
    return memo[n]

print(fibonacci_memo(50))    
    