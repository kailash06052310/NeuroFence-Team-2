# NeuroFence

**NeuroFence** is an offline desktop AI security tool that detects suspicious behavior in Large Language Models (LLMs) by analyzing hidden layer activations. The project is designed to identify potential **weight poisoning** and **backdoor attacks** before deploying an LLM in production.

---

## Project Overview

NeuroFence loads an open-source Hugging Face model inside a secure local environment, executes both normal and adversarial prompts, records hidden layer activations using PyTorch hooks, compares them with a baseline, and generates detailed security reports.

The application provides:

- Hidden layer activation monitoring
- Baseline vs adversarial comparison
- Risk score calculation
- Detection verdict
- JSON security report
- PDF security report
- Desktop GUI for analysis and visualization

---

## Features

### Backend

- Hugging Face model loading
- Prompt Fuzzer
- Activation Tracker using PyTorch Hooks
- Baseline generation
- Layer-wise activation comparison
- Detection Logic
- Risk Score calculation
- Confidence Score
- JSON Report Generation
- PDF Report Generation

### Desktop GUI

- Professional Dashboard
- Load Model
- Run Analysis
- Progress Display
- Layer Activity Matrix
- Risk Score Card
- Verdict Display
- Analysis Statistics
- Report Viewer
- Dark / Light Theme

---

## Project Architecture

```text
PyQt6 Desktop GUI
        ↓
Model Loader
        ↓
Prompt Fuzzer
        ↓
Activation Tracker
        ↓
Analyzer
        ↓
Detection Logic
        ↓
JSON Report
        ↓
PDF Report
```

---

## Folder Structure

```text
NeuroFence-Team-2/

├── docs/
├── models/
├── src/
│   ├── app.py
│   ├── main.py
│   ├── model_loader.py
│   ├── activation_tracker.py
│   ├── analyzer.py
│   ├── detection_logic.py
│   ├── fuzzer.py
│   ├── report_generator.py
│   ├── pdf_report.py
│   └── report.json
│
├── requirements.txt
├── README.md
└── .gitignore
```

---

## Technologies Used

- Python 3
- PyTorch
- Transformers (Hugging Face)
- PyQt6
- ReportLab
- NumPy

---

## Installation

Clone the repository:

```bash
git clone <repository-url>
cd NeuroFence-Team-2
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

## Running the Project

Go to the source directory:

```bash
cd src
```

Run the desktop application:

```bash
python app.py
```

Or run the backend directly:

```bash
python main.py
```

---

## Output

After analysis, NeuroFence generates:

- `report.json`
- `Security_Report.pdf`

These reports contain:

- Risk Score
- Confidence Score
- Detection Verdict
- Layer-wise Activation Differences
- Analysis Summary
- Security Statistics

---

## Security Workflow

```text
Load Model
      ↓
Generate Baseline
      ↓
Run Adversarial Prompts
      ↓
Capture Hidden Layer Activations
      ↓
Compare with Baseline
      ↓
Calculate Risk Score
      ↓
Generate Reports
```

---

## Future Scope

- Support for larger transformer models
- Advanced neuron heatmap visualization
- Additional attack datasets
- Enhanced anomaly detection algorithms
- Export reports in multiple formats
- Real-time monitoring support

---

## Team Members

- Kailash Singh Rawat
- Prithvi
- Chirangi
- Rohan

---

## License

This project is developed for academic and research purposes.