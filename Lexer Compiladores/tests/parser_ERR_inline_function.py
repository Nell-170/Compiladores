# Should fail:
def f(): a = 1; b = 2      # semicolons unsupported in this grammar
def bad(): if x: y         # control-flow can’t be inline

