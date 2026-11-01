import glob
import re

for pronoun in ['Your', 'His', 'Our', 'Their']:
    for f in sorted(glob.glob('data/light_novel/vol-*.json')):
        with open(f, 'r', encoding='utf-8') as fp:
            c = fp.read()
        # Find pronoun followed by Portuguese word
        m = re.findall(r'.{0,30}\b' + pronoun + r'\s+[A-Za-zÀ-ÿ]+.{0,30}', c)
        if m:
            print(pronoun, f, m[:3])
