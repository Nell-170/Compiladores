vals = [1, 2,]
for val in vals:
  print(val)

x = 0
y = 1

def f(): return 0

# Empty + basic
empty = []
single = [x]
multi  = [1, 2, 3]

# Nested containers (dicts can have trailing commas per your new rule)
nested_mix = [(1,), (x, y), [3, 4], {"a": 1, "b": 2,}, (x + 1)]

# Multiline list (newlines are ignored inside [] due to paren_level)
multi_line = [
    1,
    2 + f(3),
    (x + 4) // 2 % 3,
    {"k": [7, 8]},
]

# Spacing & grouping vs tuple inside list
spaces = [  1 , 2 , 3  ]
grouping_vs_tuple = [(x), (x, y), (x,)]  # (x) is just x; (x,) is a tuple

# Comments and blank lines inside a list
comments_and_blanks = [
    1,              # ok
    # comment-only line
    2
]

# Trailing commas in lists should be allowed 
trailing1 = [1,]
trailing2 = [1, 2,]
trailing_nested = [{"a": 1,},]

# Comma issues
double_comma = [1,,2]
leading_comma = [,1]
missing_value = [1, ]            # comma with no following element
missing_comma = [1 2]            # needs a comma between items

# Structural problems
missing_close = [1, 2
missing_open  = 1, 2]
comp = [x for x in xs]           # list comprehensions unsupported in this grammar
