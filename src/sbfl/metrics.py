from math import sqrt

def tarantula(ncf: int, ncs: int, nf: int, ns: int) -> float:
    '''
    Tarantula formula:
        Suspiciousness = (ncf / nf) / ((ncf / nf) + (ncs / ns))
    where:
        ncf = # of failed tests that executed this line
        ncs = # of successful tests that executed this line
        nf  = total failed tests
        ns  = total successful tests
    '''
    if nf == 0:
        return 0.0
    fail_ratio = ncf / nf if nf else 0
    pass_ratio = ncs / ns if ns else 0
    denom = fail_ratio + pass_ratio
    return (fail_ratio / denom) if denom else 0.0


def ochiai(ncf: int, ncs: int, nf: int, ns: int) -> float:
    '''
    Ochiai formula:
        Suspiciousness = ncf / sqrt(nf * (ncf + ncs))
    '''
    denom = sqrt(nf * (ncf + ncs)) if (nf and (ncf + ncs)) else 0
    return (ncf / denom) if denom else 0.0
