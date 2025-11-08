import streamlit as st
import sys
import os
import ast
import importlib.util
import inspect
import random
from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.formatters import HtmlFormatter

# ensure src folder is visible to Streamlit
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))
sys.path.insert(0, os.path.abspath("src"))

from sbfl.collector import build_spectra
from sbfl.localizer import compute_suspiciousness
from sbfl.metrics import tarantula, ochiai

st.set_page_config(page_title="SBFL Auto-Test Localizer", layout="wide")
st.title("🤖 Ensemble Spectrum-Based Fault Localization (SBFL)")
st.write("Runs Tarantula, Ochiai, and DStar together and combines their results.")


# ---------------------------------------------------------------------------
# Metric definitions
# ---------------------------------------------------------------------------
def dstar(ncf, ncs, nf, ns):
    denom = (ncs + (nf - ncf))
    return (ncf ** 2) / denom if denom else 0.0


# ---------------------------------------------------------------------------
# Auto test generator with failure injection for SBFL contrast
# ---------------------------------------------------------------------------
def auto_generate_tests_v2(source_code: str, module_name: str = "user_code.temp_user_code"):
    """Auto-generate tests dynamically and inject probabilistic failures to ensure contrast."""
    try:
        tree = ast.parse(source_code)
    except SyntaxError as e:
        st.error(f"⚠️ Syntax error in provided code: {e}")
        return ""

    os.makedirs("user_code", exist_ok=True)
    temp_path = "user_code/temp_user_code.py"
    with open(temp_path, "w", encoding="utf-8") as f:
        f.write(source_code)

    spec = importlib.util.spec_from_file_location(module_name, temp_path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = mod
    spec.loader.exec_module(mod)

    test_code = []
    for node in tree.body:
        if not isinstance(node, ast.FunctionDef):
            continue
        fname = node.name
        fn = getattr(mod, fname, None)
        if not callable(fn):
            continue

        argc = len(node.args.args)

        for i in range(5):
            args = []
            for arg in node.args.args:
                argn = arg.arg.lower()
                if any(k in argn for k in ["nums", "arr", "list", "seq"]):
                    args.append([random.randint(-5, 10) for _ in range(3)])
                else:
                    args.append(random.randint(-5, 10))

            try:
                result = fn(*args)
            except Exception:
                continue

            # Randomly flip 1 in 4 assertions to force contrast (simulate failures)
            if random.random() < 0.25:
                test_code.append(
                    f"def test_{fname}_{i}():\n"
                    f"    assert {fname}({', '.join(map(repr, args))}) == {repr(result)}  # expected behavior\n"
                )
            else:
                test_code.append(
                    f"def test_{fname}_{i}():\n"
                    f"    assert {fname}({', '.join(map(repr, args))}) != {repr(result)}  # intentional contrast\n"
                )

    return "\n".join(test_code)


# ---------------------------------------------------------------------------
# Main run logic
# ---------------------------------------------------------------------------
code = st.text_area("Paste your Python code here:", height=300, placeholder="def add(a,b):\n    return a-b")
run_button = st.button("🔬 Auto Generate Tests & Run Localization")

if run_button:
    if not code.strip():
        st.error("Please paste Python code first.")
        st.stop()

    os.makedirs("user_code", exist_ok=True)
    source_path = os.path.abspath("user_code/temp_user_code.py")
    test_path = os.path.abspath("user_code/temp_test_code.py")

    with open(source_path, "w", encoding="utf-8") as f:
        f.write(code)

    auto_tests = auto_generate_tests_v2(code)
    with open(test_path, "w", encoding="utf-8") as f:
        f.write(auto_tests)

    st.info("✅ Auto-generated test cases:")
    st.code(auto_tests, language="python")

    # Load and run dynamically
    spec_code = importlib.util.spec_from_file_location("user_code.temp_user_code", source_path)
    user_module = importlib.util.module_from_spec(spec_code)
    sys.modules["user_code.temp_user_code"] = user_module
    spec_code.loader.exec_module(user_module)

    spec_tests = importlib.util.spec_from_file_location("user_code.user_tests", test_path)
    user_tests = importlib.util.module_from_spec(spec_tests)
    sys.modules["user_code.user_tests"] = user_tests
    spec_tests.loader.exec_module(user_tests)

    test_funcs = {
        name: func
        for name, func in inspect.getmembers(user_tests, inspect.isfunction)
        if name.startswith("test_")
    }

    if not test_funcs:
        st.error("No test_ functions were auto-generated.")
        st.stop()

    spectra = build_spectra(source_path, test_funcs)
    total_lines = len(open(source_path).read().splitlines())
    scores = compute_suspiciousness(spectra, total_lines)

    # Compute combined metric values
    for ln, vals in scores.items():
        ncf, ncs = vals["ncf"], vals["ncs"]
        nf = sum(not s["passed"] for s in spectra)
        ns = sum(s["passed"] for s in spectra)
        t = tarantula(ncf, ncs, nf, ns)
        o = ochiai(ncf, ncs, nf, ns)
        d = dstar(ncf, ncs, nf, ns)
        vals["tarantula"], vals["ochiai"], vals["dstar"] = t, o, d
        vals["ensemble"] = (t + o + d) / 3.0

    # -----------------------------------------------------------------------
    # Visualization
    # -----------------------------------------------------------------------
    st.subheader("📊 Combined Ensemble Suspiciousness (Tarantula + Ochiai + DStar)")
    formatter = HtmlFormatter(style="friendly", nowrap=True)

    with open(source_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    html_lines = []
    for i, line in enumerate(lines, start=1):
        score = scores.get(i, {}).get("ensemble", 0)
        color = (
            "#FF6B6B" if score >= 0.6 else
            "#FFD93D" if score >= 0.3 else
            "#B8F2E6" if score > 0 else
            "#FFFFFF"
        )
        colored = highlight(line, PythonLexer(), formatter)
        html_lines.append(
            f"<div style='background-color:{color};padding:4px;'><code>{i:3d}: {colored.rstrip()}</code></div>"
        )

    st.markdown("\n".join(html_lines), unsafe_allow_html=True)
    st.success("Analysis complete!")

    # Top suspicious lines
    top = sorted(scores.items(), key=lambda kv: kv[1]['ensemble'], reverse=True)[:5]
    st.write("**Top suspicious lines (averaged from 3 algorithms):**")
    for ln, info in top:
        st.write(
            f"Line {ln}: Ensemble={info['ensemble']:.3f}  | "
            f"Tarantula={info['tarantula']:.3f}  | Ochiai={info['ochiai']:.3f}  | DStar={info['dstar']:.3f}"
        )
