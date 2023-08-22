import argparse

from .api import complete

parser = argparse.ArgumentParser()
parser.add_argument('--language', default='python', choices=[
    'python', 'javascript', 'java', 'csharp', 'typescript', 'c', 'cpp', 'go',
    'kotlin', 'php', 'ruby', 'rust', 'scala', 'shell', 'sql'
])
ns = parser.parse_args()

completions = complete(None, language=ns.language)
for c in completions:
    print(c)
