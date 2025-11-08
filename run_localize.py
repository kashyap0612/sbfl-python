#!/usr/bin/env python3
import sys, os
sys.path.insert(0, os.path.abspath("src"))

import inspect
from sbfl.collector import build_spectra
from sbfl.localizer import compute_suspiciousness
from sbfl.viz import visualize_file_with_scores
import tests.test_subject_tests as test_module

SOURCE = 'examples/test_subject.py'

def collect_test_functions(module):
    '''Collects all functions starting with test_ from a test module.'''
    tests = {}
    for name, obj in inspect.getmembers(module):
        if name.startswith('test_') and inspect.isfunction(obj):
            tests[name] = obj
    return tests

if __name__ == '__main__':
    print('=== Collecting tests ===')
    tests = collect_test_functions(test_module)
    print('Found:', list(tests.keys()))

    print('\n=== Building spectra ===')
    spectra = build_spectra(SOURCE, tests)
    total_lines = len(open(SOURCE).read().splitlines())

    print('\n=== Computing suspiciousness ===')
    scores = compute_suspiciousness(spectra, total_lines)

    print('\n=== Visualization (Tarantula metric) ===')
    visualize_file_with_scores(SOURCE, scores, metric='tarantula')

    print('\n=== Top suspicious lines ===')
    ranked = sorted(scores.items(), key=lambda kv: kv[1]['tarantula'], reverse=True)
    for ln, info in ranked[:10]:
        if info['tarantula'] > 0:
            print(f'Line {ln}: Susp={info["tarantula"]:.3f}  ncf={info["ncf"]}  ncs={info["ncs"]}')
