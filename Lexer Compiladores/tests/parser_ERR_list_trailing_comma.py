# Comma issues
double_comma = [1,,2]
leading_comma = [,1]
missing_value = [1, ]            # comma with no following element
missing_comma = [1 2]            # needs a comma between items

# Structural problems
missing_close = [1, 2
missing_open  = 1, 2]
comp = [x for x in xs]           # list comprehensions unsupported in this grammar