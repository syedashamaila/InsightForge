# InsightForge AI Architecture

## Overall Workflow

Business Requirement

        |
        V

Requirement Agent

        |
        V

Mock Data Agent

        |
        V

Clarification Agent

        |
        V

Prototype Agent

        |
        V

Reporter Agent

        |
        V

StreamLit UI

-----------------------------------------------------------

## Requirement Agent

### Responsibility
Understand the bisiness requirement and convert it into a structured BI specification.

### Input
Natural Language business requirement

### Output
- Business Objective
- Dashboard title
- KPIs
- Measures
- Dimensions
- Filters
- Business questions
- Suggested star schema
- Fact tables
- Relationships
- Assumptions

The Requirement Agent must NOT generate:
- Mock data
- Charts
- Dashboard Visuals
- Reports

----------------------------------------------------------------

## Mock Data Agent

### Responsibility
Convert the structured requirement recieved from the Requirement Agent into a complete mock BI dataset that can be used by the Prototype Agent and the Reporter Agent. 

### Input
The input is not the users text anymore.
It recieves the RequirementContext from the Requirement Agent.

For Example:
{
    "dashboard_title": "....",
    “business_objective”: "....",
	“business_domain": "....",
	“target_users”: [....],
	“kpis”: [....],
	“measures”: [....],
	“dimensions”: [....],
	“filters”: [....],
	“business_questions” : [....],
	“fact_tables”: [....],
	“dimension_tables”: [....],
	“relationships”: [....],
	“assumptions”: [....],
	“success_criteria”: [....]

}

### Output
- Fact tables
- Dimension tables
- Sample records
- Realtionships
- Data dictionary

---------------------------------------------------------------------

## Clarification Agent

### Responsibility
Validate the BI requirement.

If confidence >= 90%
- Continue automatically.

Otherwise:
- Ask clarification questions.

------------------------------------------------------------------------

## Prototype Agent

### Responsibility
Design the dashboard layout.

Generate:
- KPI placement
- Visual placement
- Recommended chart type
- Dashboard sections
- Interaction suggestions

DO NOT generate reports.

-----------------------------------------------------------------------

## Reporter Agent

### Responsibility
Generate:
-Executive Summary
- Dashboard Documentation
- Power BI implementation notes
- Actuals charts using generated mock data

Generate chats using Plotly.

D NOT create fake placeholder charts. 

