# FAIL: top_level_stmt doesn’t include if_stmt/while_stmt/for_stmt
# (Unless you extend top_level_stmt to allow them.)
x = 5
if x > 4:
    print("hi")
