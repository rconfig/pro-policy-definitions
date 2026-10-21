#!/usr/bin/env python3
"""Lint rConfig policy definitions without needing rConfig Pro.

Usage: python3 .tooling/scripts/lint.py [--root DIR]

Checks every *.policy file outside dot-folders, plus the metadata, samples and expected-results
files that go with them, and that every visible top-level folder holds a template.
Drafts in .drafts/ are not checked as policies; only their sidecar pairing is checked. Each check
mirrors rConfig V8 Pro behaviour; the Pro file and line are cited next to each check.
Pro line numbers refer to the commit recorded in .tooling/scripts/methods.json.

Exit status is 1 when any error is found, 0 otherwise.
Dependencies: Python 3.9+ standard library and PyYAML.
"""
import argparse
import json
import os
import re
import sys

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))

SAMPLES_DIR = '.tooling/samples'
EXPECTED_DIR = '.tooling/expected'
DRAFTS_DIR = '.drafts'

CONFIG_FORMATS = (
    'ios-running-config', 'junos-display-set', 'junos-brace',
    'fortios-full-config', 'routeros-export', 'bigip-scf',
)
KINDS = ('hardening', 'operational', 'template')
STATUSES = ('lab-tested', 'synthetic-tested', 'under-review')
SOURCES = ('sanitised-real', 'lab', 'synthetic')
META_REQUIRED = (
    'title', 'description', 'vendor', 'os', 'config_format', 'collection_command',
    'kind', 'min_rconfig_version', 'status', 'framework_claim',
)
SAMPLE_REQUIRED = ('file', 'name', 'os', 'os_version', 'config_format', 'source', 'hardened')

# PHP trim() default character list.
PHP_TRIM = ' \t\n\r\0\x0b'

# PolicyAstBuilder.php:27 and :29
AST_OPERATORS = ('any', 'all', 'not')
AST_TYPED_LEAVES = ('contains', 'equals', 'regex', 'wildcard')


class Issue:
    def __init__(self, path, line, check, message):
        self.path, self.line, self.check, self.message = path, line, check, message

    def __str__(self):
        loc = f'{self.path}:{self.line}' if self.line else self.path
        return f'{loc}: [{self.check}] {self.message}'


class Yaml12Loader(yaml.SafeLoader):
    """SafeLoader with YAML 1.2 booleans only, as Symfony YAML (used by Pro) treats yes/no/on/off as strings."""


Yaml12Loader.yaml_implicit_resolvers = {
    key: [(tag, rx) for tag, rx in resolvers if tag != 'tag:yaml.org,2002:bool']
    for key, resolvers in yaml.SafeLoader.yaml_implicit_resolvers.items()
}
Yaml12Loader.add_implicit_resolver(
    'tag:yaml.org,2002:bool', re.compile(r'^(?:true|True|TRUE|false|False|FALSE)$'), list('tTfF'))


def load_methods(path=None):
    with open(path or os.path.join(HERE, 'methods.json'), encoding='utf-8') as fh:
        return json.load(fh)


def read_bytes(path):
    with open(path, 'rb') as fh:
        return fh.read()


def read_yaml(path):
    with open(path, encoding='utf-8') as fh:
        return yaml.safe_load(fh)


def version_tuple(v):
    return tuple(int(x) for x in str(v).split('.'))


# ---------------------------------------------------------------------------
# Mirrors of Pro logic
# ---------------------------------------------------------------------------

def php_save_check(text):
    """Mirror of app/Rules/PolicyDefinitionFileFormattedCorrectly.php:18-62. Returns an error message or None."""
    expect_directive = expect_code = has_block = False
    for line in re.split(r'\r\n|\r|\n', text):                      # :18
        trimmed = line.strip(PHP_TRIM)                               # :24
        if trimmed == '':                                            # :26
            if expect_directive or expect_code:
                return 'blank line between the description, directive and first config line (PolicyDefinitionFileFormattedCorrectly.php:28)'
            continue
        if trimmed.startswith('//'):                                 # :35
            expect_directive, expect_code = True, False
            continue
        if trimmed.startswith('#['):                                 # :42
            if not expect_directive:
                return "directive not immediately preceded by a // description (PolicyDefinitionFileFormattedCorrectly.php:44)"
            expect_directive, expect_code = False, True
            continue
        if expect_code:                                              # :55
            has_block, expect_code = True, False
    if not has_block:                                                # :61
        return 'no complete // description, #[ directive and config line block (PolicyDefinitionFileFormattedCorrectly.php:62)'
    return None


def editor_check(text):
    """Mirror of resources/js/composables/usePolicyFormatValidator.js:6-56. Returns (line, message) pairs."""
    problems = []
    has_block = False
    state = 'idle'
    for idx, line in enumerate(re.split(r'\r?\n', text)):            # :7
        trimmed = line.strip()                                        # :14 (JS trim also strips U+FEFF)
        trimmed = trimmed.strip('﻿')
        if trimmed == '':
            if state == 'needDirective':
                problems.append((idx + 1, 'blank line between description and directive (usePolicyFormatValidator.js:19)'))
            elif state == 'needCode':
                problems.append((idx + 1, 'blank line between directive and first config line (usePolicyFormatValidator.js:22)'))
            continue
        if trimmed.startswith('//'):
            state = 'needDirective'
            continue
        if trimmed.startswith('#['):
            if state != 'needDirective':
                problems.append((idx + 1, 'directive not preceded by a // description (usePolicyFormatValidator.js:37)'))
            else:
                state = 'needCode'
            continue
        if state == 'needCode':
            has_block, state = True, 'inCode'
        elif state != 'inCode':
            problems.append((idx + 1, 'config line outside a // description and #[ directive block (usePolicyFormatValidator.js:50)'))
    if not has_block:
        problems.append((1, 'no complete // description, #[ directive and config line block (usePolicyFormatValidator.js:56)'))
    return problems


def find_last_delimiter(pattern, delimiter):
    """Mirror of RegexPatternUtility::findLastDelimiterPosition (RegexPatternUtility.php:144-192)."""
    last = pattern.rfind(delimiter)
    if '[' in pattern:
        in_class = escaped = False
        real = 0
        for i in range(1, len(pattern)):
            ch = pattern[i]
            if escaped:
                escaped = False
                continue
            if ch == '\\':
                escaped = True
                continue
            if ch == '[' and not in_class:
                in_class = True
                continue
            if ch == ']' and in_class:
                in_class = False
                continue
            if ch == delimiter and not in_class:
                real = i
        if real > 0:
            last = real
    return last


def is_delimited(pattern, delimiters):
    """True when Pro would use the pattern as written rather than wrapping it in /.../ (RegexPatternUtility.php:14-29)."""
    if pattern == '' or pattern[0] not in delimiters:
        return False
    return find_last_delimiter(pattern, pattern[0]) > 0


def ast_valid(node_yaml):
    """Mirror of PolicyAstBuilder::build (PolicyAstBuilder.php:34-59). True when Pro accepts the rule tree."""
    if not isinstance(node_yaml, dict):
        return False
    data = dict(node_yaml)
    if 'scope' in data:                                              # :41
        if not isinstance(data['scope'], str) or data['scope'].strip(PHP_TRIM) == '':
            return False
        del data['scope']
    if len(data) != 1:                                               # :49
        return False
    return ast_node_valid(data)


def ast_node_valid(spec):
    """Mirror of PolicyAstBuilder::buildNode and buildOperator (PolicyAstBuilder.php:61-117)."""
    if isinstance(spec, bool):
        return False
    if isinstance(spec, (str, int, float)):
        return True
    if not isinstance(spec, dict) or len(spec) != 1:                 # :71
        return False
    key, value = next(iter(spec.items()))
    if key in AST_OPERATORS:                                         # :78
        if key == 'not':
            return ast_node_valid(value)
        return isinstance(value, list) and value != [] and all(ast_node_valid(c) for c in value)   # :103
    # typed leaves (:82) and literal "key: value" lines (:87) both need a scalar value
    return isinstance(value, (str, int, float, bool))


def regex_leaves(spec):
    """Yield every regex: leaf value in an evaluate_block rule tree."""
    if isinstance(spec, dict):
        for key, value in spec.items():
            if key == 'regex' and len(spec) == 1:
                yield value
            elif key in AST_OPERATORS or key == 'scope':
                yield from regex_leaves(value)
    elif isinstance(spec, list):
        for child in spec:
            yield from regex_leaves(child)


def parse_like_pro(text, methods):
    """Mirror of PolicyDefinitionParser::parse and parsedBlockArrayValidator (PolicyDefinitionParser.php:18-97).
    Returns the list of (method, description) rules Pro would load."""
    rules = []
    for block in [b for b in text.split('//') if b != '']:         # :25 PREG_SPLIT_NO_EMPTY
        block = block.strip(PHP_TRIM)                                # :30
        if block in ('', '0'):                                       # :31 empty()
            continue
        if '#[' not in block:                                        # :37
            continue
        m = re.match(r'^([^\n]+)\n#\[(\w+)\]\n(.+)$', block, re.S | re.A)   # :42
        if not m:
            continue
        description, method, content = (g.strip(PHP_TRIM) for g in m.groups())   # :50-52
        if method == 'evaluate_block':                               # :54
            try:
                structure = yaml.load(content, Loader=Yaml12Loader)  # :108
            except yaml.YAMLError:
                continue
            if not ast_valid(structure):                             # :115
                continue
            rules.append((method, description))
            continue
        single = len(content.split('\n')) == 1                       # :63-65
        if method in methods['array_methods'] and single:            # :87-93
            continue
        rules.append((method, description))
    return rules


# ---------------------------------------------------------------------------
# Repository checks
# ---------------------------------------------------------------------------

def policy_blocks(lines):
    """Split normalised lines into description blocks: (desc_index, [directive indexes], body by directive)."""
    blocks = []
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith('//'):
            blocks.append({'desc': i, 'directives': []})
        elif stripped.startswith('#[') and blocks:
            blocks[-1]['directives'].append(i)
    return blocks


def rule_body(lines, directive_index):
    body = []
    for line in lines[directive_index + 1:]:
        stripped = line.strip()
        if stripped.startswith('//') or stripped.startswith('#['):
            break
        body.append(line)
    while body and body[-1].strip() == '':
        body.pop()
    return body


def lint_policy(path, rel, methods):
    issues = []
    raw = read_bytes(path)

    # Encoding. The parser needs "\n" straight after "#[method]" (PolicyDefinitionParser.php:42),
    # so CRLF files load with zero rules. A BOM makes the PHP save check reject the first line
    # (PolicyDefinitionFileFormattedCorrectly.php:24, trim() keeps U+FEFF).
    if raw.startswith(b'\xef\xbb\xbf'):
        issues.append(Issue(rel, 1, 'bom', 'file starts with a UTF-8 byte order mark'))
    if b'\r' in raw:
        first = raw[:raw.index(b'\r')].count(b'\n') + 1
        issues.append(Issue(rel, first, 'line-endings', 'CR or CRLF line endings; use LF only'))
    if raw and not raw.endswith(b'\n'):
        issues.append(Issue(rel, None, 'final-newline', 'file does not end with a newline (repository convention, not a Pro requirement)'))

    text = raw.decode('utf-8', errors='replace')
    lines = text.replace('\r\n', '\n').replace('\r', '\n').split('\n')

    # Save checks: PHP form request rule and the editor validator.
    msg = php_save_check(text)
    if msg:
        issues.append(Issue(rel, None, 'save-check', msg))
    for line_no, msg in editor_check(text):
        issues.append(Issue(rel, line_no, 'editor-check', msg))

    for i, line in enumerate(lines):
        stripped = line.strip()
        # Block comments are not comment syntax: the parser only splits on "//" (PolicyDefinitionParser.php:25).
        if stripped.startswith('/*') or stripped.endswith('*/'):
            issues.append(Issue(rel, i + 1, 'block-comment', '/* */ comments are not supported; use a // description'))
        # The parser splits the whole file on every "//" (PolicyDefinitionParser.php:25), so a "//"
        # anywhere but the start of a description line cuts the rule in two.
        rest = stripped[2:] if stripped.startswith('//') else stripped
        if '//' in rest:
            issues.append(Issue(rel, i + 1, 'double-slash', '"//" inside a line splits the rule (PolicyDefinitionParser.php:25)'))

    blocks = policy_blocks(lines)
    for block in blocks:
        d = block['desc']
        nxt = lines[d + 1].strip() if d + 1 < len(lines) else ''
        # The parser needs a non-empty description line followed directly by "#[" (PolicyDefinitionParser.php:42).
        if not nxt.startswith('#['):
            issues.append(Issue(rel, d + 1, 'description-directive', '// line is not followed directly by a #[ line'))
        if lines[d].strip()[2:].strip(PHP_TRIM) == '':
            issues.append(Issue(rel, d + 1, 'description-directive', 'empty // description; Pro drops the rule (PolicyDefinitionParser.php:42)'))
        # A second "#[" under one description is captured into the first rule's body by the
        # /s pattern at PolicyDefinitionParser.php:42 and split into an array at :63.
        for extra in block['directives'][1:]:
            issues.append(Issue(rel, extra + 1, 'one-directive', 'more than one #[ under one // description'))

    for block in blocks:
        for di in block['directives']:
            directive = lines[di]
            m = re.fullmatch(r'#\[(\w+)\]', directive, re.A)
            if not m:
                # PolicyDefinitionParser.php:42 needs the line to be exactly "#[" word characters "]".
                issues.append(Issue(rel, di + 1, 'unknown-method', f'malformed directive line {directive!r}'))
                continue
            method = m.group(1)
            # PolicyMethod.php:13-27; the evaluator calls the method by name (PolicyDefinitionEvaluator.php:39, :45).
            if method not in methods['methods']:
                issues.append(Issue(rel, di + 1, 'unknown-method', f'method {method!r} is not in .tooling/scripts/methods.json'))
                continue
            body = rule_body(lines, di)
            content = '\n'.join(body).strip(PHP_TRIM)
            single = len(content.split('\n')) == 1

            # PolicyMethod::arrayMethods (PolicyMethod.php:37-46) with a one-line body is dropped by
            # PolicyDefinitionParser::parsedBlockArrayValidator (PolicyDefinitionParser.php:87-93).
            if method in methods['array_methods'] and single:
                issues.append(Issue(rel, di + 1, 'array-multiline', f'{method} needs a body of two or more lines'))

            # Undelimited patterns are wrapped as /.../ with no flags (RegexPatternUtility.php:22-23),
            # so ^ and $ anchor to the whole file.
            if method in methods['regex_methods']:
                if not single:
                    issues.append(Issue(rel, di + 1, 'regex-delimited', f'{method} needs a one-line pattern'))
                elif not is_delimited(content, methods['regex_delimiters']):
                    issues.append(Issue(rel, di + 2, 'regex-delimited', f'pattern {content!r} is not delimited, for example /.../m'))

            if method == 'evaluate_block':
                # PolicyDefinitionParser.php:105-126: Symfony YAML, then PolicyAstBuilder.
                try:
                    structure = yaml.load(content, Loader=Yaml12Loader)
                except yaml.YAMLError as exc:
                    issues.append(Issue(rel, di + 2, 'yaml', f'evaluate_block body is not valid YAML: {str(exc).splitlines()[0]}'))
                    continue
                if not ast_valid(structure):
                    issues.append(Issue(rel, di + 2, 'yaml', 'evaluate_block body is not a valid rule tree (PolicyAstBuilder.php:34-59)'))
                    continue
                # regex: leaves go through the same utility (LeafNode.php:29, PolicyMatcher.php:70-77).
                for leaf in regex_leaves(structure):
                    if not isinstance(leaf, str) or not is_delimited(leaf, methods['regex_delimiters']):
                        issues.append(Issue(rel, di + 2, 'regex-delimited', f'regex: leaf {leaf!r} is not delimited'))

    directives = sum(1 for l in lines if l.strip().startswith('#['))
    parsed = parse_like_pro(text, methods)
    if len(parsed) != directives:
        issues.append(Issue(rel, None, 'parsed-count', f'Pro would load {len(parsed)} rules but the file has {directives} #[ directives'))

    used = {m for m in re.findall(r'^#\[(\w+)\]$', '\n'.join(lines), re.M) if m in methods['methods']}
    return issues, used


def lint_meta(meta_path, rel, used_methods, methods):
    issues = []
    try:
        meta = read_yaml(meta_path)
    except yaml.YAMLError as exc:
        return [Issue(rel, None, 'metadata', f'not valid YAML: {str(exc).splitlines()[0]}')]
    if not isinstance(meta, dict):
        return [Issue(rel, None, 'metadata', 'top level must be a mapping')]
    for key in META_REQUIRED:
        if key not in meta:
            issues.append(Issue(rel, None, 'metadata', f'missing field {key!r}'))
    if meta.get('config_format') not in CONFIG_FORMATS:
        issues.append(Issue(rel, None, 'metadata', f"config_format must be one of {', '.join(CONFIG_FORMATS)}"))
    if meta.get('kind') not in KINDS:
        issues.append(Issue(rel, None, 'metadata', f"kind must be one of {', '.join(KINDS)}"))
    if meta.get('status') not in STATUSES:
        issues.append(Issue(rel, None, 'metadata', f"status must be one of {', '.join(STATUSES)}"))
    if meta.get('status') == 'under-review' and not meta.get('notes'):
        issues.append(Issue(rel, None, 'metadata', 'status under-review needs a notes entry'))
    claim = meta.get('framework_claim', None)
    if claim is not None and (not isinstance(claim, dict) or not isinstance(claim.get('ids_local'), bool)):
        issues.append(Issue(rel, None, 'metadata', 'framework_claim must be null or a mapping with a boolean ids_local'))

    declared = str(meta.get('min_rconfig_version', ''))
    if not re.fullmatch(r'\d+\.\d+\.\d+', declared):
        issues.append(Issue(rel, None, 'metadata', 'min_rconfig_version must look like 8.0.2'))
    elif used_methods:
        needed = max((methods['min_version'][m] for m in used_methods), key=version_tuple)
        if version_tuple(declared) < version_tuple(needed):
            culprits = sorted(m for m in used_methods if methods['min_version'][m] == needed)
            issues.append(Issue(rel, None, 'min-version', f"min_rconfig_version {declared} is below {needed}, needed by {', '.join(culprits)}"))
    return issues


def lint_samples(root):
    issues = []
    base = os.path.join(root, SAMPLES_DIR)
    formats = set()
    if not os.path.isdir(base):
        return issues, formats
    for vendor in sorted(os.listdir(base)):
        folder = os.path.join(base, vendor)
        if not os.path.isdir(folder):
            continue
        rel = f'{SAMPLES_DIR}/{vendor}/samples.yaml'
        index = os.path.join(folder, 'samples.yaml')
        if not os.path.exists(index):
            issues.append(Issue(rel, None, 'samples', 'missing samples.yaml'))
            continue
        data = read_yaml(index) or {}
        listed = set()
        for entry in data.get('samples') or []:
            for key in SAMPLE_REQUIRED:
                if key not in entry:
                    issues.append(Issue(rel, None, 'samples', f"{entry.get('file', '?')}: missing field {key!r}"))
            if entry.get('config_format') not in CONFIG_FORMATS:
                issues.append(Issue(rel, None, 'samples', f"{entry.get('file')}: unknown config_format"))
            if entry.get('source') not in SOURCES:
                issues.append(Issue(rel, None, 'samples', f"{entry.get('file')}: source must be one of {', '.join(SOURCES)}"))
            if not isinstance(entry.get('hardened'), bool):
                issues.append(Issue(rel, None, 'samples', f"{entry.get('file')}: hardened must be true or false"))
            if not os.path.exists(os.path.join(folder, str(entry.get('file')))):
                issues.append(Issue(rel, None, 'samples', f"{entry.get('file')}: file not found"))
            listed.add(entry.get('file'))
            formats.add(entry.get('config_format'))
        for name in sorted(os.listdir(folder)):
            if name != 'samples.yaml' and name not in listed:
                issues.append(Issue(f'{SAMPLES_DIR}/{vendor}/{name}', None, 'samples', 'not listed in samples.yaml'))
    return issues, formats


def lint_import_folders(root):
    """Every top-level folder rConfig shows in Import Templates must hold at least one importable template.

    Pro lists the cloned repository's folders with File::directories() (PolicyDefinitionGithubController.php:73),
    which uses Symfony Finder (vendor/laravel/framework/src/Illuminate/Filesystem/Filesystem.php:615), and Finder hides
    dot-folders by default (vendor/symfony/finder/Finder.php:76). It then lists each folder's templates with
    File::glob("{$directory}/*.policy") (PolicyDefinitionGithubController.php:104).
    A visible folder with no *.policy file shows an error instead of a template list.
    """
    issues = []
    for name in sorted(os.listdir(root)):
        folder = os.path.join(root, name)
        if name.startswith('.') or not os.path.isdir(folder):
            continue
        if not any(f.endswith('.policy') and os.path.isfile(os.path.join(folder, f)) for f in os.listdir(folder)):
            issues.append(Issue(name + '/', None, 'import-folders',
                                'folder appears in Import Templates but has no *.policy file; move it under a dot-folder'))
    return issues


def lint_draft_pairing(root):
    """Drafts are not checked as policies, but any sidecar under .drafts/ must have a matching *.policy.draft."""
    issues = []
    base = os.path.join(root, DRAFTS_DIR)
    for dirpath, _, filenames in os.walk(base):
        for name in sorted(filenames):
            if name.endswith('.meta.yaml'):
                stem = name[:-len('.meta.yaml')]
                if stem + '.policy.draft' not in filenames:
                    issues.append(Issue(os.path.relpath(os.path.join(dirpath, name), root), None, 'metadata-pair',
                                        'no matching .policy.draft file'))
    return issues


def lint_repo(root, methods):
    issues = []
    policies, metas = {}, {}
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if not d.startswith('.')]
        for name in filenames:
            full = os.path.join(dirpath, name)
            if name.endswith('.policy'):
                policies[full[:-len('.policy')]] = full
            elif name.endswith('.meta.yaml'):
                metas[full[:-len('.meta.yaml')]] = full

    for stem in sorted(policies):
        rel = os.path.relpath(policies[stem], root)
        file_issues, used = lint_policy(policies[stem], rel, methods)
        issues += file_issues
        if stem not in metas:
            issues.append(Issue(rel, None, 'metadata-pair', f'no {os.path.basename(stem)}.meta.yaml next to this file'))
        else:
            issues += lint_meta(metas[stem], os.path.relpath(metas[stem], root), used, methods)
        expected = os.path.join(root, EXPECTED_DIR, os.path.basename(stem) + '.yaml')
        if not os.path.exists(expected):
            issues.append(Issue(rel, None, 'expected-pair', f'no {EXPECTED_DIR}/{os.path.basename(stem)}.yaml'))
    for stem in sorted(set(metas) - set(policies)):
        issues.append(Issue(os.path.relpath(metas[stem], root), None, 'metadata-pair', 'no matching .policy file'))

    issues += lint_draft_pairing(root)
    issues += lint_import_folders(root)
    sample_issues, _ = lint_samples(root)
    issues += sample_issues
    return issues, len(policies)


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('--root', default=REPO)
    parser.add_argument('--methods', default=os.path.join(HERE, 'methods.json'))
    args = parser.parse_args()
    issues, count = lint_repo(args.root, load_methods(args.methods))
    for issue in issues:
        print(issue)
    print(f'{count} policy files checked, {len(issues)} problems')
    return 1 if issues else 0


if __name__ == '__main__':
    sys.exit(main())
