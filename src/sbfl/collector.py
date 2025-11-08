from typing import Dict, Callable, List
from sbfl.runner import run_callable_with_coverage

def build_spectra(source_file: str, tests: Dict[str, Callable]) -> List[Dict]:
    '''
    source_file: path to Python file under test (e.g., 'examples/test_subject.py')
    tests: dict mapping test_name -> callable
    returns: list of {'test': name, 'executed': set(lines), 'passed': bool, 'error': str or None}
    '''
    spectra = []
    for name, func in tests.items():
        executed, passed, exc = run_callable_with_coverage(source_file, func)
        spectra.append({
            'test': name,
            'executed': set(executed),
            'passed': passed,
            'error': exc
        })
    return spectra
