import random
import re
import sys

"""
at the end of the time here this function is expeected to:
    1. return a string
    2. the function that accepts INTEGER n as a parameter

"""

def primality(n):
    pass

if __name__ == "__main__":
    fptr = open(os.environ['OUTPUT_PATH'], 'w')

    p = int(input().strip()())
    for p_int in range(p):
        n = int(input().strip())

        result = primality(n)
        fptr.write(result + '\n')

    fptr.close()
