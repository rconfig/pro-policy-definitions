#!/usr/bin/env python3
"""Tests for .tooling/scripts/lint.py: one bad fixture per check, plus a clean control,
including the generated framework file checks.

Usage: python3 .tooling/scripts/test_lint.py
"""
import os
import sys
import tempfile
import textwrap
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import generate_frameworks  # noqa: E402
import lint  # noqa: E402

METHODS = lint.load_methods()

GOOD = '// Example: AAA enabled\n#[must_match_single_string]\naaa new-model\n'

GOOD_META = textwrap.dedent('''\
    title: Example
    description: Example policy used by the lint tests.
    vendor: cisco
    os: ios
    config_format: ios-running-config
    collection_command: show running-config
    kind: hardening
    min_rconfig_version: 8.0.0
    status: synthetic-tested
    framework_claim: null
''')


def policy_checks(text, raw=None):
    """Lint one policy file's text and return the set of check ids that fired."""
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, 'example.policy')
        with open(path, 'wb') as fh:
            fh.write(raw if raw is not None else text.encode('utf-8'))
        issues, _ = lint.lint_policy(path, 'example.policy', METHODS)
        return {i.check for i in issues}


def repo_checks(files):
    """Build a throwaway repository from {relative path: text} and return the set of check ids that fired."""
    with tempfile.TemporaryDirectory() as tmp:
        for rel, text in files.items():
            full = os.path.join(tmp, rel)
            os.makedirs(os.path.dirname(full), exist_ok=True)
            with open(full, 'w', encoding='utf-8', newline='\n') as fh:
                fh.write(text)
        issues, _ = lint.lint_repo(tmp, METHODS)
        return {i.check for i in issues}


class PolicyFileChecks(unittest.TestCase):
    def test_clean_file_has_no_issues(self):
        self.assertEqual(policy_checks(GOOD), set())

    def test_line_endings(self):
        self.assertIn('line-endings', policy_checks(None, GOOD.replace('\n', '\r\n').encode()))

    def test_crlf_also_loads_zero_rules_like_pro(self):
        self.assertIn('parsed-count', policy_checks(None, GOOD.replace('\n', '\r\n').encode()))

    def test_bom(self):
        self.assertIn('bom', policy_checks(None, b'\xef\xbb\xbf' + GOOD.encode()))

    def test_final_newline(self):
        self.assertIn('final-newline', policy_checks(GOOD.rstrip('\n')))

    def test_save_check_blank_line(self):
        self.assertIn('save-check', policy_checks('// Example\n\n#[must_match_single_string]\naaa new-model\n'))

    def test_editor_check_line_outside_block(self):
        checks = policy_checks('aaa new-model\n' + GOOD)
        self.assertIn('editor-check', checks)
        self.assertNotIn('save-check', checks)  # the PHP rule accepts this; only the editor rejects it

    def test_description_not_followed_by_directive(self):
        checks = policy_checks('// Stray comment\n' + GOOD)
        self.assertIn('description-directive', checks)
        self.assertNotIn('save-check', checks)  # Pro accepts it but silently drops the first line

    def test_one_directive_per_description(self):
        text = GOOD + '#[must_not_match_single_string]\nip http server\n'
        self.assertIn('one-directive', policy_checks(text))

    def test_unknown_method(self):
        self.assertIn('unknown-method', policy_checks('// Example\n#[must_match_everything]\naaa new-model\n'))

    def test_malformed_directive(self):
        self.assertIn('unknown-method', policy_checks('// Example\n#[must_match_single_string] \naaa new-model\n'))

    def test_regex_method_not_delimited(self):
        self.assertIn('regex-delimited', policy_checks('// Example\n#[must_match_regex]\n^aaa new-model$\n'))

    def test_regex_method_missing_closing_delimiter(self):
        self.assertIn('regex-delimited', policy_checks('// Example\n#[must_match_regex]\n/^aaa new-model$\n'))

    def test_regex_method_delimited_is_clean(self):
        self.assertEqual(policy_checks('// Example\n#[must_match_regex]\n/^aaa new-model$/m\n'), set())

    def test_regex_leaf_not_delimited(self):
        text = '// Example\n#[evaluate_block]\nall:\n  - regex: "^ntp server "\n'
        self.assertIn('regex-delimited', policy_checks(text))

    def test_block_comment(self):
        self.assertIn('block-comment', policy_checks('/* Example header */\n' + GOOD))

    def test_double_slash_in_body(self):
        text = '// Example\n#[must_match_single_string]\nset server https://example.com\n'
        self.assertIn('double-slash', policy_checks(text))

    def test_evaluate_block_invalid_yaml(self):
        self.assertIn('yaml', policy_checks('// Example\n#[evaluate_block]\nall: [unclosed\n'))

    def test_evaluate_block_invalid_rule_tree(self):
        self.assertIn('yaml', policy_checks('// Example\n#[evaluate_block]\nall: []\n'))

    def test_evaluate_block_yes_is_a_string_not_a_boolean(self):
        # Symfony YAML reads "yes" as a string, so Pro accepts this leaf; the lint must agree.
        self.assertEqual(policy_checks('// Example\n#[evaluate_block]\nall:\n  - yes\n'), set())

    def test_array_method_single_line(self):
        self.assertIn('array-multiline', policy_checks('// Example\n#[must_match_all_from_array]\naaa new-model\n'))

    def test_parsed_count_empty_description(self):
        checks = policy_checks('//\n#[must_match_single_string]\naaa new-model\n')
        self.assertIn('parsed-count', checks)
        self.assertNotIn('save-check', checks)  # Pro saves it, then the parser drops the rule


class RepositoryChecks(unittest.TestCase):
    def base(self):
        return {
            'cisco/example.policy': GOOD,
            'cisco/example.meta.yaml': GOOD_META,
            '.tooling/expected/example.yaml': 'policy: cisco/example.policy\nrules: []\n',
        }

    def test_clean_repository(self):
        self.assertEqual(repo_checks(self.base()), set())

    def test_policy_without_metadata(self):
        files = self.base()
        del files['cisco/example.meta.yaml']
        self.assertIn('metadata-pair', repo_checks(files))

    def test_metadata_without_policy(self):
        files = self.base()
        files['cisco/orphan.meta.yaml'] = GOOD_META
        self.assertIn('metadata-pair', repo_checks(files))

    def test_draft_policies_are_ignored(self):
        files = self.base()
        files['.drafts/juniper/old.policy.draft'] = '/* not checked */\n'
        self.assertEqual(repo_checks(files), set())

    def test_draft_sidecar_without_draft(self):
        files = self.base()
        files['.drafts/juniper/old.policy.draft'] = '/* not checked */\n'
        files['.drafts/juniper/other.meta.yaml'] = GOOD_META
        self.assertIn('metadata-pair', repo_checks(files))

    def test_visible_folder_without_templates(self):
        files = self.base()
        files['samples/cisco/router.txt'] = 'hostname lab-r1\n'
        self.assertIn('import-folders', repo_checks(files))

    def test_folder_with_only_drafts_is_not_importable(self):
        files = self.base()
        files['juniper/old.policy.draft'] = '// Example\n#[must_match_single_string]\naaa new-model\n'
        self.assertIn('import-folders', repo_checks(files))

    def test_dot_folders_are_hidden_from_import(self):
        files = self.base()
        files['.tooling/notes/readme.txt'] = 'not a template\n'
        self.assertEqual(repo_checks(files), set())

    def test_metadata_bad_field(self):
        files = self.base()
        files['cisco/example.meta.yaml'] = GOOD_META.replace('kind: hardening', 'kind: secure')
        self.assertIn('metadata', repo_checks(files))

    def test_under_review_needs_notes(self):
        files = self.base()
        files['cisco/example.meta.yaml'] = GOOD_META.replace('synthetic-tested', 'under-review')
        self.assertIn('metadata', repo_checks(files))

    def test_min_version_below_methods(self):
        files = self.base()
        files['cisco/example.policy'] = '// Example\n#[evaluate_block]\nall:\n  - aaa new-model\n'
        self.assertIn('min-version', repo_checks(files))

    def test_policy_without_expected_results(self):
        files = self.base()
        del files['.tooling/expected/example.yaml']
        self.assertIn('expected-pair', repo_checks(files))

    def test_sample_not_listed(self):
        files = self.base()
        files['.tooling/samples/cisco/samples.yaml'] = 'samples: []\n'
        files['.tooling/samples/cisco/stray.txt'] = 'hostname lab-r1\n'
        self.assertIn('samples', repo_checks(files))


TOPIC_META = GOOD_META.replace('framework_claim: null\n', textwrap.dedent('''\
    framework_claim: null
    rules:
      - description: "Example: AAA enabled"
        references:
          nist_800_53: ["AC-2"]
'''))

RESULTS = textwrap.dedent('''\
    policy: {policy}
    rules:
      -
        rule: 1
        description: '{description}'
        method: must_match_single_string
        results:
          cisco/router.txt: {result}
''')


class GeneratedFrameworkChecks(unittest.TestCase):
    """A topic file tagged with one NIST control, plus the framework file the generator writes from it."""

    def base(self):
        files = {
            'cisco/ios-example.policy': GOOD,
            'cisco/ios-example.meta.yaml': TOPIC_META,
            '.tooling/expected/ios-example.yaml': RESULTS.format(policy='cisco/ios-example.policy', description='Example: AAA enabled', result='pass'),
            '.tooling/expected/ios-nist-800-53.yaml': RESULTS.format(policy='cisco/ios-nist-800-53.policy', description='NIST AC-2: Example: AAA enabled', result='pass'),
        }
        with tempfile.TemporaryDirectory() as tmp:
            for rel, text in files.items():
                os.makedirs(os.path.dirname(os.path.join(tmp, rel)), exist_ok=True)
                with open(os.path.join(tmp, rel), 'w', encoding='utf-8', newline='\n') as fh:
                    fh.write(text)
            files.update(generate_frameworks.generate(tmp))
        return files

    def test_generated_files_in_sync_are_clean(self):
        files = self.base()
        self.assertIn('cisco/ios-nist-800-53.policy', files)
        self.assertNotIn('cisco/ios-hipaa.policy', files)  # no rule tagged, so no file
        self.assertEqual(repo_checks(files), set())

    def test_hand_edited_generated_file(self):
        files = self.base()
        files['cisco/ios-nist-800-53.policy'] = files['cisco/ios-nist-800-53.policy'].replace('aaa new-model', 'aaa new-model ')
        self.assertIn('generated', repo_checks(files))

    def test_missing_generated_file(self):
        files = self.base()
        del files['cisco/ios-nist-800-53.policy']
        del files['cisco/ios-nist-800-53.meta.yaml']
        del files['.tooling/expected/ios-nist-800-53.yaml']
        self.assertIn('generated', repo_checks(files))

    def test_stale_generated_file(self):
        files = self.base()
        files['cisco/ios-example.meta.yaml'] = files['cisco/ios-example.meta.yaml'].replace('nist_800_53: ["AC-2"]', 'hipaa: ["164.312(a)(1)"]')
        self.assertIn('generated', repo_checks(files))  # nist-800-53 file no longer produced, hipaa file missing

    def test_framework_kind_must_be_generated(self):
        files = self.base()
        files['cisco/ios-nist-800-53.meta.yaml'] = files['cisco/ios-nist-800-53.meta.yaml'].replace('generated: true\n', '')
        self.assertIn('metadata', repo_checks(files))

    def test_generated_result_differs_from_source(self):
        files = self.base()
        files['.tooling/expected/ios-nist-800-53.yaml'] = files['.tooling/expected/ios-nist-800-53.yaml'].replace('pass', 'fail')
        self.assertIn('generated-results', repo_checks(files))


if __name__ == '__main__':
    unittest.main(verbosity=2)
