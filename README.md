# CargoGuard AI 

**Predictive AI system for cargo risk monitoring and route intelligence.**

CargoGuard AI is a data-driven logistics platform designed to predict and mitigate cargo risks during transit. By leveraging machine learning models and an interactive dashboard, this system provides actionable route intelligence and automated risk reporting to ensure safer and more efficient freight operations.

---

## ✨ Key Features

* **Predictive Risk Modeling:** Utilizes custom-trained machine learning models (`train_model.py`) to forecast potential cargo hazards based on historical and real-time route data.
* **Interactive Dashboard:** A responsive UI built with Streamlit (`app.py`) featuring live demo data badges and optimized routing logic for fleet managers.
* **Automated Reporting:** Generates downloadable, comprehensive PDF risk assessment reports on the fly using `reportlab`.
* **Cloud-Ready Deployment:** Configured with `render.yaml` for seamless continuous deployment and hosting on Render.

## 🛠️ Tech Stack

* **Language:** Python 100%
* **Frontend/UI:** Streamlit
* **Machine Learning:** Python ML ecosystem (data processing & model training)
* **Reporting:** ReportLab (PDF Generation)
* **Deployment:** Render

## 📁 Repository Structure

```text
CargoGuard-AI/
├── data/                   # Datasets and demo data for dashboard badges
├── app.py                  # Main Streamlit application and routing logic
├── train_model.py          # ML pipeline for training predictive risk models
├── requirements.txt        # Python package dependencies
├── render.yaml             # Render deployment configuration
└── .gitignore              # Ignored files (models, venv, LFS)
