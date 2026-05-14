# 📊 DataPulse — Web-Based Data Analysis Dashboard

> **Capstone Project** — A no-code, AI-powered analytics platform that empowers non-technical users to upload, clean, explore, visualize, and generate AI-driven insights from any tabular dataset, entirely through the browser.

---

## 📌 Abstract

Extracting meaningful insights from raw data typically demands programming expertise in Python, R, or SQL — creating a significant barrier for domain professionals, small businesses, and students. **DataPulse** bridges this gap by delivering a fully interactive, web-based analytics dashboard built on Streamlit. Users simply upload a CSV or Excel file and immediately gain access to automated statistical summaries, interactive visualizations, data-cleaning tools, and an **AI Analysis** module powered by a local LLM (via Ollama). The result is a self-contained, privacy-friendly analytics workflow that runs entirely on the user's own machine — no cloud APIs, no data leaving the device.

---

## ✨ Key Features

| Module | Capabilities |
|---|---|
| **Home** | KPI metrics (rows, columns, missing values), full data preview, summary statistics, correlation heatmap, data composition pie chart |
| **Analytics** | Handle missing data (mean / median / mode / ffill / bfill / drop), groupwise filtering, range-based filtering, column renaming, statistical summary — all with **undo** support |
| **Visualization** | Interactive Bar, Line, Scatter, and Pie charts via Plotly with color-by-category options |
| **AI Analysis** | One-click analysis tasks (Run Analysis, Fix Dataset, Pivot Table, Dashboard Generation, Trend Analysis, Forecast) + free-form natural language queries — powered by PandasAI + Ollama |

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Frontend / UI | Streamlit, Custom CSS (dark theme) |
| Data Processing | Pandas, NumPy |
| Visualization | Plotly Express |
| AI / LLM Backend | PandasAI, Ollama (local LLM) |
| Package Manager | uv |
| Language | Python 3.12+ |

---

## 📐 Architecture Overview

```
┌──────────────┐      ┌──────────────────┐      ┌──────────────┐
│  CSV / XLSX  │─────▶│  Streamlit App   │─────▶│   Plotly      │
│  File Upload │      │  (app.py)        │      │   Charts      │
└──────────────┘      │                  │      └──────────────┘
                      │  ┌────────────┐  │
                      │  │ Pandas /   │  │
                      │  │ NumPy      │  │
                      │  └────────────┘  │
                      │  ┌────────────┐  │      ┌──────────────┐
                      │  │ PandasAI   │──┼─────▶│ Ollama LLM   │
                      │  │ Agent      │  │      │ (localhost)   │
                      │  └────────────┘  │      └──────────────┘
                      └──────────────────┘
```

---

## 🚀 Installation & Setup

### Prerequisites

- **Python 3.12+**
- **uv** (Python package manager) — [Install uv](https://docs.astral.sh/uv/getting-started/installation/)
- **Ollama** — [Install Ollama](https://ollama.com/download) (required for the AI Analysis tab)

### 1. Clone the Repository

```bash
git clone https://github.com/imrupayan/Web-based-DataAnalysis.git
cd Web-based-DataAnalysis
```

### 2. Install Dependencies

```bash
uv sync
```

This reads `pyproject.toml` and installs all required packages into a local `.venv`.

### 3. Pull an Ollama Model

```bash
ollama run qwen3-coder:480b-cloud
```

> You can use any Ollama-compatible model. Update the `model` parameter in `app.py` to match.

### 4. Run the App

```bash
uv run streamlit run app.py
```

The dashboard will open automatically at `http://localhost:8501`.

---

## 📖 Usage

1. **Upload** a `.csv` or `.xlsx` file using the sidebar.
2. **Home** tab shows an instant overview — metrics, data preview, statistics, correlation map.
3. **Analytics** tab lets you clean and transform the data (handle nulls, filter, rename columns).
4. **Visualization** tab lets you build interactive charts with custom axes and color grouping.
5. **AI Analysis** tab lets you run pre-built analysis tasks or ask free-form questions in natural language.

---

## 📁 Project Structure

```
Web-based-DataAnalysis/
├── app.py               # Main application (Ollama-backed AI)
├── pyproject.toml       # Project metadata & dependencies
├── uv.lock              # Locked dependency versions
├── .python-version      # Python version pin
├── .gitignore
└── README.md
```

---

## 🔮 Future Scope

- Cloud LLM integration (OpenAI / NVIDIA NIM) for users without local GPU
- Export cleaned datasets and generated reports as PDF
- Multi-file join and merge support
- User authentication and saved analysis sessions
- Deployment on Streamlit Community Cloud

---

## 👥 Team Members & Contributions

1. **Rupayan Ghosh**: Developed the core data analysis and preprocessing module of the dashboard, including file handling, missing data treatment, group-wise filtering, statistical summaries, column renaming, and AI-powered analysis integration using PandasAI and Ollama-based LLMs.
2. **Tannistha Ghosh**: Developed the data visualization module using Plotly, implementing interactive charts such as bar charts, line charts, scatter plots, and pie charts. Also contributed to homepage design, dashboard styling, and undo functionality.
3. **Mehul Ghosh**: Built the Sign in and Sign up page using HTML, CSS and JavaScript.
4. **Farhan Gazi**: Implemented numeric range filtering, duplicate row removal, outlier detection, negative value detection, datatype viewing, and column search features.
5. **Yashanshi Gautam**: Designed and prepared the project presentation (PPT) and assisted in documenting the project workflow and features.

---

## 📄 License

This project is developed as an academic capstone. All rights reserved.
