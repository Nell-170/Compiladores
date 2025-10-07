# FAIL: missing ':' and/or wrong indentation after if.
if 3 > 2
    x = 1

# FAIL: else must align with its if (lexer should emit DEDENT/INDENT mismatch).
if True:
    x = 1
  else:
    x = 2
