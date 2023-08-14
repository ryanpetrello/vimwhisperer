from .api import complete

completions = complete(None)
for c in completions:
    print(c)
