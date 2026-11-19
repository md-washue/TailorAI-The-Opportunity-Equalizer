# ✂️ TailorAI — The Opportunity Equalizer

> **Target Event:** Hack the Gap (*"Innovation shouldn't depend on location"*)  
> **Primary Objective:** A single-process, bug-proof, privacy-first ATS resume optimization platform powered by Google Gemini, deterministic gap math, structured Pydantic schemas, and safe LaTeX compilation.

---

## 🌍 The Story: Equalizing Global Opportunity

In a world of remote work and borderless innovation, talent is universal — but opportunity is not. 

Every day, exceptional engineers, researchers, and creators from emerging tech hubs and non-traditional backgrounds submit resumes to global companies, only to be rejected in seconds by automated **Applicant Tracking Systems (ATS)**. These legacy filters don't evaluate raw intellect or potential; they look for exact semantic keywords, industry-standard phrasing, and structured typography.

Candidates from non-elite regions often lack access to expensive executive coaching, insider recruiters, or proprietary resume rewrite tools. Worse, existing "AI resume builders" hallucinate fake metrics, leak personal user data to remote third-party databases, and output brittle raw LaTeX that fails to compile.

**TailorAI** was created to shatter this barrier. Built for **Hack the Gap**, TailorAI is an editorial, mathematical, privacy-first resume optimization studio designed to give every ambitious candidate the same polish, keyword coverage, and presentation quality as a Silicon Valley executive — with zero data retention and zero hallucinated metrics.

---

## 🏛️ System Architecture & Engineering Principles

TailorAI is engineered with strict systems-level:

```
TailorAI-The-Opportunity-Equalizer/
├── .streamlit/
│   └── config.toml            # Editorial Ivory/Burgundy theme configuration
├── assets/
│   └── logo.png               # Circular needle-and-thread LaTeX emblem
├── templates/
│   └── master_resume.tex.j2   # Fixed, known-good LaTeX template with Jinja2 delimiters
├── tailor_venv/               # Local Python virtual environment (Git-ignored)
├── .env                       # Server-side demo key: GEMINI_API_KEY=... (Git-ignored)
├── .gitignore                 # Lists .env, tailor_venv/, __pycache__/, *.sqlite3
├── AGENT.md                   # Master engineering specification
├── app.py                     # Single-process Streamlit application (UI + AI + Telemetry)
├── requirements.txt           # Pinned dependencies
├── test_app.py                # Comprehensive test suite
└── README.md                  # Project documentation & submission story
```

### 1. Single-Process Architecture
Eliminates separate FastAPI/Node backends, dual-port synchronization, and CORS failures. All UI state, Gemini API calls, deterministic math, and telemetry logging execute inside a single Streamlit process (`app.py`).

### 2. Modern Google GenAI SDK (`google-genai`)
Built strictly with the official modern SDK (`from google import genai` and `from google.genai import types`), pinned to `gemini-2.5-flash` for high-throughput, low-latency structured extraction.

### 3. Pydantic Structured Contracts (No Raw LLM LaTeX)
The LLM is never permitted to write or edit raw LaTeX directly. All Gemini passes return strict Pydantic models:
- **Pass 1 (Extraction):** Returns `ResumeModel` (education, experience, projects, skills).
- **Pass 2 (Optimization):** Returns `OptimizationResult` containing `IndexedBullet` entries referencing exact positional indices `(section, item_index, bullet_index)`.

### 4. Deterministic Gap Analysis Math
Zero hallucinated ATS match scores. All keyword coverage percentages, lift deltas, and missing keywords are calculated deterministically in Python using token regex matching and curated stopword filtering:
$$\text{Coverage \%} = \text{round}\left(100 \times \frac{|\text{JD Tokens} \cap \text{Resume Tokens}|}{\max(|\text{JD Tokens}|, 1)}\right)$$

### 5. Safe LaTeX Sanitization & Overleaf Bridge
Structured strings are escaped through a custom LaTeX filter (`tex_escape`) and injected into `templates/master_resume.tex.j2` using custom Jinja2 delimiters (`\BLOCK{...}` and `\VAR{... | tex}`).
- Performs automated sanity checks verifying `\begin{` and `\end{` tag balance.
- Features a **1-Click Overleaf POST Bridge** that launches a compiled, production-grade PDF resume in Overleaf in a new tab without losing local session state.

### 6. Defense-in-Depth & Privacy-First Telemetry
- **Prompt Injection Defense:** Untrusted Job Description text is capped at 4,000 characters, wrapped in `<job_description>...</job_description>` XML tags, and isolated as passive contextual data.
- **PDF Cap:** Ingestion capped at 3 pages maximum via `pypdf`.
- **Ephemeral Telemetry:** SQLite database (`metrics.sqlite3`) operating in **WAL mode** logs only anonymous counters (`parse`, `optimize`, `export_tex`). No resume text or PII is ever written to disk or database.



## ⚡ Quickstart Guide

### Prerequisites
- Python 3.10+
- A Google AI Studio API Key (or use **"⚡ Load Sample Profile & JD"** for instant testing)

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/md-washue/TailorAI-The-Opportunity-Equalizer.git
   cd TailorAI-The-Opportunity-Equalizer
   ```

2. **Activate the local environment:**
   ```powershell
   # Windows PowerShell:
   .\tailor_venv\Scripts\Activate.ps1
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up API Key (Optional):**
   Create a `.env` file or export your Gemini API key:
   ```bash
   # .env
   GEMINI_API_KEY=your_gemini_api_key_here
   ```
   *(You can also input your key directly into the Streamlit sidebar BYOK password field).*

5. **Run the application:**
   ```bash
   streamlit run app.py
   ```
   Open your browser to `http://localhost:8501`.

---

## 🧪 Running the Test Suite

Verify all components (LaTeX escaping, Jinja2 template rendering, deterministic coverage math, and SQLite telemetry) by executing:

```bash
python test_app.py
```

Expected output:
```text
✓ test_tex_escape passed
✓ test_extract_tokens_and_coverage passed
✓ test_render_latex_sanity passed
✓ test_render_plaintext passed
✓ test_telemetry passed

🎉 ALL TESTS PASSED!
```

---

## 🔬 Judge Evaluation Flow (5-Second Demo)

If evaluating for **Hack the Gap**, follow these 3 steps:
1. Launch the app (`streamlit run app.py`).
2. Click **"⚡ Load Sample Profile & JD"** in the top hero. This loads Elena Rostova's full backend engineering profile and a realistic Senior Backend JD from Nexus Core Technologies.
3. Switch to **Tab 2 (Deterministic Tailoring & Diff)** and click **"Run Deterministic Tailoring"** (or inspect the candidate form in Tab 1 and the compiled LaTeX in Tab 3).

---

## 📜 Privacy Statement

> **Privacy-First Architecture:** No resume text, contact details, or personal data is ever stored on our servers. Inputs are processed entirely in-memory via Google Gemini and immediately discarded. Ephemeral telemetry logs anonymous event counts only.

---

*TailorAI — Built with heart and rigor for Hack the Gap 2026.*
