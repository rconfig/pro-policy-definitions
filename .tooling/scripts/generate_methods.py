#!/usr/bin/env python3
"""Regenerate .tooling/scripts/methods.json from an rConfig V8 Pro checkout.

Usage: python3 .tooling/scripts/generate_methods.py [path-to-rconfig-pro]
The Pro path defaults to $RCONFIG_PRO_PATH, then ../rconfig8.

Method names and the array-method list are read from app/Enums/PolicyMethod.php.
Regex delimiters are read from app/Services/Utilities/RegexPatternUtility.php.
The first release for each method is not in the Pro source, so it is kept in
FIRST_RELEASE below with the Pro commit that introduced the method.
"""
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))

# Pro commit that introduced each method, and the first release branch that contained it.
# Methods not listed here predate V8.0.0.
FIRST_RELEASE = {
    'must_not_match_regex': ('8.0.2', 'fac16f7ccc', 'RCO-263 negative matching methods'),
    'wildcard_must_not_match_single_string': ('8.0.2', 'fac16f7ccc', 'RCO-263 negative matching methods'),
    'match_code_block_strict': ('8.2.2', 'f7bdef7302', 'match_code_block_strict'),
    'evaluate_block': ('8.3.0', '33807feb8d', 'RCO-956 nested AND/OR/NOT with block scoping'),
}
BASELINE = '8.0.0'


def main():
    pro = sys.argv[1] if len(sys.argv) > 1 else os.environ.get('RCONFIG_PRO_PATH', os.path.join(REPO, '..', 'rconfig8'))
    enum_path = os.path.join(pro, 'app/Enums/PolicyMethod.php')
    util_path = os.path.join(pro, 'app/Services/Utilities/RegexPatternUtility.php')
    enum_src = open(enum_path, encoding='utf-8').read()
    util_src = open(util_path, encoding='utf-8').read()

    cases = dict(re.findall(r"case\s+(\w+)\s*=\s*'(\w+)';", enum_src))
    body = re.search(r'function arrayMethods\(\).*?return \[(.*?)\];', enum_src, re.S).group(1)
    array_methods = [cases[name] for name in re.findall(r'self::(\w+)->value', body)]
    delimiters = re.findall(r"'(.)'", re.search(r'\$validDelimiters\s*=\s*\[(.*?)\];', util_src).group(1))

    commit = subprocess.run(['git', '-C', pro, 'rev-parse', 'HEAD'], capture_output=True, text=True, check=True).stdout.strip()

    methods = list(cases.values())
    data = {
        'source': {
            'project': 'rConfig V8 Pro',
            'commit': commit,
            'files': ['app/Enums/PolicyMethod.php', 'app/Services/Utilities/RegexPatternUtility.php'],
            'generated_by': '.tooling/scripts/generate_methods.py',
        },
        'methods': methods,
        'array_methods': array_methods,
        'regex_methods': [m for m in methods if m in ('must_match_regex', 'must_not_match_regex')],
        'regex_delimiters': delimiters,
        'min_version': {m: FIRST_RELEASE.get(m, (BASELINE,))[0] for m in methods},
        'min_version_sources': {m: {'commit': c, 'change': d} for m, (_, c, d) in FIRST_RELEASE.items() if m in methods},
    }
    out = os.path.join(HERE, 'methods.json')
    with open(out, 'w', encoding='utf-8', newline='\n') as fh:
        json.dump(data, fh, indent=2)
        fh.write('\n')
    print(f'wrote {out} from {pro} at {commit[:10]}: {len(methods)} methods, {len(array_methods)} array methods')


if __name__ == '__main__':
    main()
