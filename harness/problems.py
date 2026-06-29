# 20 executable Python coding problems. Each: prompt (what the model sees) + test (hidden unit tests).
# The model must return one function with the exact name/signature. test code asserts behavior.
PROBLEMS = [
    {
        "id": "two_sum",
        "prompt": "Write a Python function `two_sum(nums, target)` that returns the indices [i, j] (i < j) of the two numbers in the list `nums` that add up to `target`. Exactly one solution exists. Return a list of two ints.",
        "test": """
assert sorted(two_sum([2,7,11,15], 9)) == [0,1]
assert sorted(two_sum([3,2,4], 6)) == [1,2]
assert sorted(two_sum([3,3], 6)) == [0,1]
""",
    },
    {
        "id": "is_palindrome",
        "prompt": "Write a Python function `is_palindrome(s)` that returns True if the string `s` is a palindrome considering only alphanumeric characters and ignoring case, else False.",
        "test": """
assert is_palindrome("A man, a plan, a canal: Panama") is True
assert is_palindrome("race a car") is False
assert is_palindrome("") is True
assert is_palindrome(".,") is True
""",
    },
    {
        "id": "fibonacci",
        "prompt": "Write a Python function `fibonacci(n)` returning the nth Fibonacci number (0-indexed: fibonacci(0)=0, fibonacci(1)=1) computed iteratively.",
        "test": """
assert fibonacci(0) == 0
assert fibonacci(1) == 1
assert fibonacci(10) == 55
assert fibonacci(20) == 6765
""",
    },
    {
        "id": "merge_intervals",
        "prompt": "Write a Python function `merge_intervals(intervals)` that merges all overlapping intervals (each a [start, end] list) and returns the merged list sorted by start.",
        "test": """
assert merge_intervals([[1,3],[2,6],[8,10],[15,18]]) == [[1,6],[8,10],[15,18]]
assert merge_intervals([[1,4],[4,5]]) == [[1,5]]
assert merge_intervals([[1,4]]) == [[1,4]]
""",
    },
    {
        "id": "roman_to_int",
        "prompt": "Write a Python function `roman_to_int(s)` that converts a Roman numeral string `s` to an integer.",
        "test": """
assert roman_to_int("III") == 3
assert roman_to_int("IV") == 4
assert roman_to_int("IX") == 9
assert roman_to_int("LVIII") == 58
assert roman_to_int("MCMXCIV") == 1994
""",
    },
    {
        "id": "valid_parentheses",
        "prompt": "Write a Python function `valid_parentheses(s)` that returns True if the string of brackets `s` (containing ()[]{}) is validly matched and nested, else False.",
        "test": """
assert valid_parentheses("()") is True
assert valid_parentheses("()[]{}") is True
assert valid_parentheses("(]") is False
assert valid_parentheses("([)]") is False
assert valid_parentheses("{[]}") is True
assert valid_parentheses("") is True
""",
    },
    {
        "id": "longest_common_prefix",
        "prompt": "Write a Python function `longest_common_prefix(strs)` that returns the longest common prefix string among a list of strings, or '' if none.",
        "test": """
assert longest_common_prefix(["flower","flow","flight"]) == "fl"
assert longest_common_prefix(["dog","racecar","car"]) == ""
assert longest_common_prefix(["a"]) == "a"
assert longest_common_prefix([]) == ""
""",
    },
    {
        "id": "group_anagrams",
        "prompt": "Write a Python function `group_anagrams(strs)` that groups the list of strings into anagram groups. Return a list of groups; order of groups and within groups does not matter.",
        "test": """
res = group_anagrams(["eat","tea","tan","ate","nat","bat"])
norm = sorted(sorted(g) for g in res)
assert norm == sorted([sorted(g) for g in [["ate","eat","tea"],["nat","tan"],["bat"]]])
""",
    },
    {
        "id": "max_subarray",
        "prompt": "Write a Python function `max_subarray(nums)` that returns the largest sum of any contiguous non-empty subarray of the integer list `nums`.",
        "test": """
assert max_subarray([-2,1,-3,4,-1,2,1,-5,4]) == 6
assert max_subarray([1]) == 1
assert max_subarray([5,4,-1,7,8]) == 23
assert max_subarray([-1,-2,-3]) == -1
""",
    },
    {
        "id": "binary_search",
        "prompt": "Write a Python function `binary_search(arr, target)` that returns the index of `target` in the sorted list `arr`, or -1 if not present. Use binary search.",
        "test": """
assert binary_search([-1,0,3,5,9,12], 9) == 4
assert binary_search([-1,0,3,5,9,12], 2) == -1
assert binary_search([], 1) == -1
assert binary_search([5], 5) == 0
""",
    },
    {
        "id": "flatten",
        "prompt": "Write a Python function `flatten(nested)` that flattens an arbitrarily nested list of integers into a single flat list, preserving order.",
        "test": """
assert flatten([1,[2,[3,4],5],[6,[7,[8]]]]) == [1,2,3,4,5,6,7,8]
assert flatten([]) == []
assert flatten([1,2,3]) == [1,2,3]
assert flatten([[[[1]]]]) == [1]
""",
    },
    {
        "id": "run_length_encode",
        "prompt": "Write a Python function `run_length_encode(s)` that returns the run-length encoding of string `s` as e.g. 'aaabbc' -> 'a3b2c1'. Empty string returns ''.",
        "test": """
assert run_length_encode("aaabbc") == "a3b2c1"
assert run_length_encode("") == ""
assert run_length_encode("x") == "x1"
assert run_length_encode("aabbaa") == "a2b2a2"
""",
    },
    {
        "id": "is_prime",
        "prompt": "Write a Python function `is_prime(n)` that returns True if integer `n` is a prime number, else False. Handle n < 2 as False.",
        "test": """
assert is_prime(2) is True
assert is_prime(17) is True
assert is_prime(1) is False
assert is_prime(0) is False
assert is_prime(-7) is False
assert is_prime(100) is False
assert is_prime(7919) is True
""",
    },
    {
        "id": "rotate_list",
        "prompt": "Write a Python function `rotate_list(lst, k)` that returns a new list with elements rotated to the right by k positions (k may exceed len or be 0). Do not mutate input.",
        "test": """
assert rotate_list([1,2,3,4,5], 2) == [4,5,1,2,3]
assert rotate_list([1,2,3], 0) == [1,2,3]
assert rotate_list([1,2,3], 4) == [3,1,2]
assert rotate_list([], 3) == []
""",
    },
    {
        "id": "reverse_words",
        "prompt": "Write a Python function `reverse_words(s)` that reverses the order of words in string `s`, collapsing multiple spaces to single spaces and stripping leading/trailing spaces.",
        "test": """
assert reverse_words("the sky is blue") == "blue is sky the"
assert reverse_words("  hello world  ") == "world hello"
assert reverse_words("a good   example") == "example good a"
""",
    },
    {
        "id": "gcd",
        "prompt": "Write a Python function `gcd(a, b)` that returns the greatest common divisor of two non-negative integers using the Euclidean algorithm.",
        "test": """
assert gcd(48, 18) == 6
assert gcd(17, 5) == 1
assert gcd(0, 5) == 5
assert gcd(100, 0) == 100
""",
    },
    {
        "id": "move_zeroes",
        "prompt": "Write a Python function `move_zeroes(nums)` that returns a new list with all zeroes moved to the end while keeping the relative order of non-zero elements.",
        "test": """
assert move_zeroes([0,1,0,3,12]) == [1,3,12,0,0]
assert move_zeroes([0,0,1]) == [1,0,0]
assert move_zeroes([1,2,3]) == [1,2,3]
assert move_zeroes([0]) == [0]
""",
    },
    {
        "id": "spiral_order",
        "prompt": "Write a Python function `spiral_order(matrix)` that returns all elements of the 2D list `matrix` in spiral order (clockwise from top-left).",
        "test": """
assert spiral_order([[1,2,3],[4,5,6],[7,8,9]]) == [1,2,3,6,9,8,7,4,5]
assert spiral_order([[1,2,3,4],[5,6,7,8],[9,10,11,12]]) == [1,2,3,4,8,12,11,10,9,5,6,7]
assert spiral_order([[1]]) == [1]
""",
    },
    {
        "id": "title_case",
        "prompt": "Write a Python function `title_case(s)` that title-cases a sentence but keeps these small words lowercase unless first: {'a','an','the','and','but','or','for','nor','of','in','on','at','to'}. The first word is always capitalized. Words are space-separated; assume lowercase input.",
        "test": """
assert title_case("the quick brown fox") == "The Quick Brown Fox"
assert title_case("a tale of two cities") == "A Tale of Two Cities"
assert title_case("to be or not to be") == "To Be or Not to Be"
""",
    },
    {
        "id": "atoi",
        "prompt": "Write a Python function `my_atoi(s)` that converts a string to a 32-bit signed integer (like C atoi): skip leading whitespace, optional +/- sign, read digits until a non-digit, ignore the rest; clamp to [-2**31, 2**31-1]; return 0 if no digits.",
        "test": """
assert my_atoi("42") == 42
assert my_atoi("   -42") == -42
assert my_atoi("4193 with words") == 4193
assert my_atoi("words and 987") == 0
assert my_atoi("-91283472332") == -2147483648
assert my_atoi("+1") == 1
""",
    },
]
