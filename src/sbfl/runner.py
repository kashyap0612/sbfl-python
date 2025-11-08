import os
import sys
import importlib.util
import traceback
from coverage import Coverage


def run_callable_with_coverage(module_path, callable_path):
    """
    Run a test callable under coverage, ensuring that
    the target module is freshly imported inside coverage context.
    Returns (executed_lines, passed_bool, traceback_text).
    """

    cov = Coverage()
    cov.start()
    passed = True
    exc_text = None

    try:
        # Fresh import of the target module from disk
        module_name = "temp_target_module"
        spec = importlib.util.spec_from_file_location(module_name, module_path)
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)

        # Run the test inside this coverage session.
        # Rebind globals so test uses the freshly imported module.
        test_globals = callable_path.__globals__
        test_globals.update(module.__dict__)

        callable_path()

    except Exception:
        passed = False
        exc_text = traceback.format_exc()

    finally:
        cov.stop()
        cov.save()

    data = cov.get_data()
    lines = set()
    target_abs = os.path.abspath(module_path).lower()

    for fname in data.measured_files():
        if os.path.abspath(fname).lower() == target_abs:
            lines.update(data.lines(fname) or [])

    cov.erase()
    return lines, passed, exc_text
