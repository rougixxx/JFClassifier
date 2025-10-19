# 🧠 JFClassifier

**My Final Graduation Project from ESI-SBA, specialising in Computer Systems Engineering**.


---

## 🚀 Overview

**JFClassifier** is an end-to-end software security solution that combines deep learning–based vulnerability detection with practical developer tools.
The system is composed of three main components:

1. JFClassifier Core Model — A deep learning architecture that classifies Java functions as safe or vulnerable based on multiple program representations (AST, CFG, DFG, CSS).

2. Web Application — A user-friendly interface that allows users to upload, test, and analyze Java code for potential vulnerabilities.

3. VS Code Extension — Integrates vulnerability detection directly into the development environment for real-time feedback and secure coding assistance.

This project was developed as part of my Master’s and Engineering final project at **ESI-SBA (Higher School of Computer Science Sidi Bel Abbès, Algeria)**.

---

## 🧩 Project Architecture

JFClassifier is organized into three main components, each with its own detailed `README`:

| Component | Description |
|------------|-------------|
| **[`arch-dev/`](./arch-dev)** | Core development and experimentation environment for model training, code representation extraction (AST, CFG, DFG), and architecture evaluation. |
| **[`jfc/`](./jfc)** | Vs code extension to integrate real-time vulnerability detection directly into the developer workflow. |
| **[`jfc-web-app/`](./jfc-web-app)** | Web interface for testing and visualizing code analysis results. Built with modern web technologies for usability and interactivity. |

Each component has a dedicated README with setup and implementation details.

---

## ⚙️ Key Features

- **Web Interface** — Test and visualize Java code analysis results directly in the browser.

- **VS Code Integration** — Real-time vulnerability detection embedded in the IDE.

- **End-to-End Pipeline** — From dataset preparation and model training to deployment and user interaction.

- **Modular Architecture** — Each component (model, web app, extension) is self-contained with its own detailed documentation.

- **Multi-representation Learning:** — Uses AST (Abstract Syntax Tree), CFG (Control Flow Graph), and DFG (Data Flow Graph) to represent code semantics and structure.

- **Deep Learning-based Detection:** — Integrates transformer-based models and attention mechanisms for precise vulnerability classification.

- **Reduced False Positives:** — Combines static analysis heuristics with ML predictions for improved accuracy.

- **Web Visualization:** — Offers a user-friendly web interface to inspect detected vulnerabilities interactively.

---

## 📊 Project Goals

1. Develop a hybrid **AI-based static code analysis system**.  
2. Leverage multiple code representations for enhanced understanding of program behavior.  
3. Reduce false positives in vulnerability detection.  
4. Provide a developer-friendly visualization and reporting tool.  

---

## 🧪 Research Context

This work is part of ongoing research in **software security, static analysis, and AI-assisted vulnerability detection**.  
It explores how **deep learning models** can complement traditional static analysis for secure software development.

---
## 📦 Installation & Setup

Each component includes its own `README.md` with specific setup steps:

- [`JFClassifier Model`](./arch-dev)
- [`JFC web app`](./jfc-web-app)
- [`VS Code Extenstion Setup`](./jfc)
---
## 📚 Future Work

- Extend support for other programming languages (Python, C/C++).

- Integrate with CI/CD pipelines for automated code scanning.

- Enhance model robustness against obfuscated code.

- **Hybrid analysis**: Combine static, dynamic, and symbolic analysis to improve detection coverage and accuracy.

- **Dataset enhancement**: Build larger, more diverse, and realistic datasets for better generalization and benchmarking.

- **CWE-specific models**: Develop specialized models for individual vulnerability categories and combine them in an ensemble framework.

- **Scalability & efficiency**: Optimize inference time and resource usage for large-scale industrial deployment.

- **Pipeline integration**: Integrate vulnerability detection into IDEs, CI/CD systems, and code review workflows for seamless adoption.

## 🧾 License

MIT License © 2025 — [Remmane Mohamed / ESI-SBA]

For anything: please contact this mail: med.remmane@gmail.com
