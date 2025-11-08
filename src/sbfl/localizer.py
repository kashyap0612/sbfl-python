from typing import Dict, List
from sbfl.metrics import tarantula, ochiai

def compute_suspiciousness(spectra: List[Dict], total_lines: int) -> Dict[int, Dict[str, float]]:
    '''
    spectra: list of {'test': str, 'executed': set(int), 'passed': bool}
    total_lines: total number of lines in the source file
    returns: dict { line_number: {'tarantula': val, 'ochiai': val, 'ncf': x, 'ncs': y} }
    '''

    nf = sum(1 for s in spectra if not s['passed'])  # total failed tests
    ns = sum(1 for s in spectra if s['passed'])      # total successful tests

    # initialize count table for each line
    line_stats = {i: {'ncf': 0, 'ncs': 0} for i in range(1, total_lines + 1)}

    # populate coverage counts
    for s in spectra:
        for ln in s['executed']:
            if ln <= total_lines:
                if s['passed']:
                    line_stats[ln]['ncs'] += 1
                else:
                    line_stats[ln]['ncf'] += 1

    # compute suspiciousness scores
    susp = {}
    for line, v in line_stats.items():
        ncf, ncs = v['ncf'], v['ncs']
        susp[line] = {
            'tarantula': tarantula(ncf, ncs, nf, ns),
            'ochiai': ochiai(ncf, ncs, nf, ns),
            'ncf': ncf,
            'ncs': ncs
        }
    return susp
