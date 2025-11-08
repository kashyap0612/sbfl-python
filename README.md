# 🔍 Spectrum-Based Fault Localization (SBFL) for Python

A web-based system to automatically detect suspicious lines in Python programs using statistical fault localization metrics — **Tarantula**, **Ochiai**, and **DStar**.

🚀 **Live Demo:** [https://sbfl-python-kashyap0612.streamlit.app](https://sbfl-python-kashyap0612.streamlit.app)

---

### ✨ Features
- Paste any Python code (≤ 20 lines)
- Auto-generate test cases using AI mutation logic
- Computes multiple metrics (Tarantula, Ochiai, DStar)
- Ensemble view combining all three
- Interactive Streamlit UI with color-coded visualization

---

### 🧠 Architecture


- **Backend:** Python (Coverage.py, PyTest)
- **Frontend:** Streamlit
- **Metrics:** Tarantula, Ochiai, DStar
- **Optional Extension:** Mutation-based testing and ML-based ranking

---

### ⚙️ Setup Locally (Optional)
```bash
git clone https://github.com/kashyap0612/sbfl-python.git
cd sbfl-python
pip install -r requirements.txt
streamlit run app.py


📊 Example Output
Top suspicious lines:
Line 5: Susp=1.000 | likely faulty statement
Line 3: Susp=0.750