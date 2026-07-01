# InsightForge - Multi-Agent BI Requirement Analysis System

## Overview

The Multi-Agent BI Requirement Analysis System is an AI-powered application that converts natural language business requirements into interactive Power BI dashboard prototypes.

The application follows a modular multi-agent architecture where each agent performs a single responsibility in the BI development lifecycle.

The system is built using:

- Python
- Streamlit
- Google Gemini
- LangGraph
- Pandas
- Plotly

---

# Architecture

```
Business Requirement
        │
        ▼
Clarification Agent
        │
        ▼
Requirement Agent
        │
        ▼
Mock Data Agent
        │
        ▼
Prototype Agent
        │
        ▼
Reporter Agent
        │
        ▼
Interactive Dashboard
```

---

# Agents

## 1. Clarification Agent

Purpose

- Understands the business requirement.
- Detects ambiguity.
- Identifies missing information.
- Generates follow-up questions.
- Produces a clarified business requirement.

Output

- ClarifiedRequirement

---

## 2. Requirement Agent

Purpose

Converts the clarified business requirement into a structured BI specification.

Generates:

- Dashboard Title
- Business Objective
- Business Domain
- KPIs
- Measures
- Dimensions
- Fact Tables
- Dimension Tables
- Relationships
- Business Questions
- Filters
- Success Criteria

Output

- RequirementContext

---

## 3. Mock Data Agent

Purpose

Creates realistic datasets for dashboard development.

Features

- Dynamic Star Schema generation
- Fact Tables
- Dimension Tables
- Relationships
- Mock Business Data
- Data Dictionary
- Metadata
- Referential Integrity Validation

Output

- Mock DataFrames
- Metadata
- Data Dictionary

---

## 4. Prototype Agent

Purpose

Generates a dashboard prototype from the structured requirements.

Creates

- KPI Cards
- Column Charts
- Line Charts
- Pie Charts
- Treemaps
- Tables
- Filters
- Drill Downs
- Dashboard Layout

Output

- Prototype JSON

---

## 5. Reporter Agent

Purpose

Converts the prototype JSON into an interactive dashboard.

Uses

- Plotly
- Pandas

Generates

- Interactive KPI Cards
- Charts
- Tables
- Dashboard Layout

Output

- Interactive Plotly Dashboard

---

# Project Structure

```
project/

│

├── agents/

│ ├── clarification_agent.py

│ ├── requirement_agent.py

│ ├── mock_data_agent.py

│ ├── prototype_agent.py

│ └── reporter_agent.py

│

├── utils/

│ ├── agent_factory.py

│ ├── agent_trace.py

│ └── llm_helper.py

│

├── StreamlitApp.py

├── requirements.txt

├── README.md

└── .env

```

---

# Installation

Clone the repository

```bash
git clone <repository-url>
```

Install dependencies

```bash
pip install -r requirements.txt
```

Create a `.env` file

```
GOOGLE_API_KEY=YOUR_API_KEY
```

---

# Running the Application

```bash
streamlit run StreamlitApp.py
```

---

# Example Workflow

Input

```
Create a sales dashboard that allows regional managers to monitor revenue,
profit, customer performance and monthly sales trends.
```

Pipeline

```
Clarification Agent
        ↓
Requirement Agent
        ↓
Mock Data Agent
        ↓
Prototype Agent
        ↓
Reporter Agent
```

Output

- Structured BI Specification
- Mock Dataset
- Prototype Layout
- Interactive Dashboard

---

# Technologies Used

- Python
- Streamlit
- Google Gemini
- LangGraph
- Plotly
- Pandas
- NumPy

---

# Features

- Multi-Agent Architecture
- AI-powered Requirement Analysis
- Business Requirement Clarification
- Automatic Star Schema Generation
- Mock Data Generation
- Dashboard Prototype Generation
- Interactive Plotly Dashboard
- Modular and Extensible Design

---

# Future Enhancements

- Power BI PBIP Generation
- DAX Measure Generation
- SQL Query Generation
- Fabric Lakehouse Integration
- Data Source Connectors
- Export to Power BI Desktop
- Conversational Dashboard Refinement

---

# License

This project is intended for educational and research purposes.
