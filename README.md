# 🎧 Vireo Audio Support Analytics

> **Deterministic customer-support analytics for CSAT, agent performance, coaching prioritization, and product-quality investigation.**

<div align="center">

**CSAT Analysis • Agent Performance • Case-Mix Adjustment • Product Investigation • Deterministic Classification**

</div>

---

## 🛠️ Tech Stack

<div align="center">

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=flat-square&logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-FF4B4B?style=flat-square&logo=streamlit&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-Data%20Analysis-150458?style=flat-square&logo=pandas&logoColor=white)
![NumPy](https://img.shields.io/badge/NumPy-Numerical%20Analysis-013243?style=flat-square&logo=numpy&logoColor=white)
![Scikit Learn](https://img.shields.io/badge/Scikit--Learn-OLS%20%26%20Statistics-F7931E?style=flat-square&logo=scikit-learn&logoColor=white)
![Pytest](https://img.shields.io/badge/Pytest-Testing-0A9EDC?style=flat-square&logo=pytest&logoColor=white)
![Python](https://img.shields.io/badge/LLM%20Runtime-None-6B7280?style=flat-square)
![Cost](https://img.shields.io/badge/Runtime%20AI%20Cost-Rs%200-2E7D32?style=flat-square)

</div>

---

# 📌 Overview

**Vireo Audio Support Analytics** is a deterministic **Streamlit analytics dashboard** built to investigate a decline in customer satisfaction after the festive season.

The dashboard combines:

- 📊 CSAT analysis
- ⏱️ Handle-time analysis
- 👤 Agent-level performance
- 🔎 Raw bottom-ten analysis
- 🎯 Case-mix-adjusted coaching priority
- 🎧 Product and issue investigation
- 🏷️ Defective-lot analysis
- 💰 Replacement-cost estimation
- 🧪 Deterministic issue classification
- ✅ Independent validation and automated testing

The application requires **no API key** and makes **no per-run LLM/API calls**.

---

# 💼 Business Problem

CSAT declined after the festive season.

The client requested a **bottom-ten agent view** to help inform allocation of a **₹4 lakh Q3 training budget**.

However, raw CSAT is affected by the types of cases agents receive.

For example:

- Tier 2 warranty cases
- Hardware triage
- Product-specific issues
- Defective-lot cases

can affect customer satisfaction independently of individual agent performance.

The dashboard therefore provides both:

```text
Raw Agent Performance
        +
Case-Mix-Adjusted Coaching Priority
        +
Product / Lot Investigation
```

This separates the simple ranking the client requested from a more defensible analytical view.

---

# 💰 Business Outcome

A major finding is a defective **Pulse 2 lot** associated with excess replacements and a substantial replacement-cost impact.

The business-case calculation estimates:

```text
Excess replacements ≈ 515
Q1 2026 replacement cost ≈ ₹9.4 lakh
Cost per replacement = ₹1,820
```

The calculation is implemented in:

```text
vireo/metrics.py::business_case
```

and surfaced on the dashboard's **first tab**.

The stated outcome target is:

```text
Reduce lot-linked excess replacements
from approximately 515 per quarter
toward approximately zero per quarter
```

---

# 🏗️ Architecture

```text
                    CSV Data Sources
                           │
                           ▼
              ┌────────────────────────┐
              │      vireo/data.py     │
              │                        │
              │ • Clean                │
              │ • Join                 │
              │ • Flag                 │
              └───────────┬────────────┘
                          │
             ┌────────────┼────────────┐
             │                         │
             ▼                         ▼
   ┌──────────────────┐      ┌──────────────────┐
   │ vireo/metrics.py │      │ vireo/themes.py  │
   │                  │      │                  │
   │ • Agent table    │      │ Regex taxonomy   │
   │ • Adjustment     │      │ Issue themes     │
   │ • Business case  │      │                  │
   └────────┬─────────┘      └────────┬─────────┘
            │                         │
            └────────────┬────────────┘
                         ▼
                 ┌───────────────┐
                 │    app.py     │
                 │   Streamlit   │
                 │   6 Tabs      │
                 └───────┬───────┘
                         │
                         ▼
                 Analytics Dashboard


        Independent Validation
                 │
       ┌─────────┴─────────┐
       ▼                   ▼
validation/            tests/
run_validation.py
       │
       ▼
results.json
```

---

# 🔄 Data Pipeline

The dashboard follows a deterministic processing pipeline.

```text
tickets.csv
agents.csv
orders.csv
customers.csv
products.csv
       │
       ▼
Data Cleaning
       │
       ▼
Data Joins
       │
       ▼
Issue Classification
       │
       ▼
Agent Metrics
       │
       ▼
Case-Mix Adjustment
       │
       ▼
Business Case
       │
       ▼
Streamlit Dashboard
```

---

# 🧹 Data Cleaning & Methodology

All major cleaning decisions are counted and exposed in the dashboard's:

```text
Data quality & method
```

tab.

## Timestamp Handling

Legacy `resolved_at` values are treated as UTC and shifted by:

```text
+5:30 → IST
```

This follows the policy specified in section 9 of the analysis methodology.

---

## ⏱️ Handle Time

Handle time is defined as:

```text
First Response → Resolution
```

rather than using an alternative duration definition.

---

## ⭐ CSAT

Blank CSAT values are:

```text
Excluded
```

They are **not converted to zero**.

---

## 👤 Agent Matching

Agents are joined using:

```text
agent_id
```

rather than agent name.

This is important because there are two agents named **Kavya Pandey**.

---

## 🏷️ Lot Matching

Lot information is joined using:

```text
order_id
```

When `order_id` is unavailable, the fallback is:

```text
customer + SKU
```

but only when exactly one matching order exists.

---

# 📊 Dashboard

The Streamlit application contains **six tabs** designed around the analytical workflow.

The dashboard covers:

```text
Executive Summary
       │
       ▼
Agent Performance
       │
       ▼
Bottom 10
       │
       ▼
Coaching Priority
       │
       ▼
Product / Lot Investigation
       │
       ▼
Data Quality & Method
```

---

# 📈 Executive Summary

The first dashboard tab provides the high-level business picture.

A key element is the **Pulse 2 lot finding**, including the estimated replacement impact.

The business-case calculation is generated from:

```text
vireo/metrics.py::business_case
```

---

# 👤 Agent Performance

The agent performance view provides:

- CSAT
- Handle time
- Team-level filtering
- Agent-level metrics
- Adjusted performance measures

The view allows analysts to investigate performance without relying exclusively on a raw ranking.

---

# 🔟 Bottom 10

The **Bottom 10** tab represents the client's requested raw ranking.

This is intentionally kept separate from the adjusted coaching view.

```text
Raw Bottom 10
      │
      ▼
Direct CSAT Ranking
      │
      ▼
Potentially influenced by
case mix
```

The dashboard allows this raw result to be compared with the more defensible coaching-priority analysis.

---

# 🎯 Coaching Priority

The coaching view adjusts agent performance for recorded case characteristics.

The central metric is:

```text
Adjusted Gap
=
Mean(Actual CSAT − Expected CSAT)
```

Expected CSAT is estimated using:

- Category
- Priority
- Channel
- Product family
- Defective-lot flag
- Team

---

# 📐 Case-Mix Adjustment

The expected CSAT model is based on OLS.

Conceptually:

```text
Recorded Case Characteristics
             │
             ▼
       Expected CSAT
             │
             ▼
      Actual CSAT
             │
             ▼
       Actual - Expected
             │
             ▼
        Agent Gap
```

This attempts to distinguish differences in observed CSAT from differences attributable to the recorded characteristics of the cases handled.

---

# 📉 Empirical Bayes Shrinkage

Small samples can produce unstable agent-level estimates.

The coaching view therefore applies **empirical Bayes shrinkage** to reduce the influence of small-sample extremes.

```text
Small Sample
     │
     ▼
Noisy Estimate
     │
     ▼
Empirical Bayes
Shrinkage
     │
     ▼
More Conservative
Agent Estimate
```

---

# 🚩 Review Recommendation Rule

An agent is marked **"Review recommended"** only when all three conditions are satisfied:

```text
Adjusted Gap ≥ 0.15
        AND
90% interval fully below zero
        AND
40+ survey responses
```

This intentionally avoids treating every low raw-CSAT agent as a coaching priority.

---

# 🔍 Why Transfers & Replacements Are Excluded

Transfers and replacement flags are intentionally excluded from the case-mix adjustment because they can be influenced by the agent.

The model instead controls for recorded case characteristics that are less directly agent-influenced:

```text
Category
Priority
Channel
Product Family
Defective-Lot Flag
Team
```

---

# 🏭 Product & Lot Investigation

The dashboard investigates whether the CSAT decline is partly associated with a product or manufacturing issue.

The analysis identified a **Pulse 2 lot** that drives much of the observed CSAT decline and is associated with excess replacements.

```text
Pulse 2 Lot
    │
    ▼
Affected Tickets
    │
    ▼
Replacement Activity
    │
    ▼
Excess Replacement Estimate
    │
    ▼
Business Cost
```

---

# 💰 Replacement Business Case

The replacement-cost calculation uses:

```text
Excess Replacements × Replacement Cost
```

For the Q1 2026 estimate:

```text
≈ 515 excess replacements
× ₹1,820 per replacement
──────────────────────────
≈ ₹9.4 lakh
```

The implementation is located in:

```text
vireo/metrics.py::business_case
```

---

# 🧮 Q1 2026 Calculation

The Q1 2026 excess figure is derived by splitting the all-time excess according to ticket share.

The **October–December lot window** was discovered from the data rather than supplied externally.

This distinction is documented because the calculation is an analytical derivation rather than a directly provided business input.

---

# 🧠 Deterministic Issue Classification

The dashboard does **not** use an LLM at runtime.

Issue themes are generated using a regex-based taxonomy:

```text
Ticket Text
    │
    ▼
Regex Rules
    │
    ▼
Issue Theme
```

The taxonomy was created after reviewing the ticket data.

This approach was selected because:

- Finance requested no per-ticket model calls
- The classification task could be handled with rules
- Deterministic output is easier to reproduce
- Runtime API costs remain zero

---

# 📊 Classifier Validation

The issue taxonomy achieved:

```text
86.7%
```

accuracy on a fresh hand-labelled holdout of:

```text
60 tickets
```

The validation is separate from the runtime dashboard.

---

# ⚠️ Known Classification Errors

The analysis identified several known failure modes.

### Firmware / Charging

The phrase:

```text
"kept it in the case"
```

can be interpreted as a charging fault in firmware-related tickets.

### Compatibility

Questions such as:

```text
"will the watch app run"
```

can be misclassified.

### Typos

For example:

```text
"debted"
```

can cause classification errors.

### Wrong-Colour Cancellation

Wrong-colour cancellation requests can be assigned to an incorrect theme.

### Watch Hardware

Watch hardware issues such as straps are grouped under:

```text
Display / Touch
```

This is a known taxonomy limitation.

---

# 🤖 AI Usage

The application itself uses:

```text
No LLM
No API calls
No runtime AI dependency
```

The classification system is deterministic.

Claude was used during development for:

- Analysis development
- Code development
- Supporting the implementation workflow

Further details are documented in:

```text
submission-form.md
```

---

# 💰 Runtime AI Cost

There are **no paid API calls during dashboard execution**.

Therefore:

```text
Runtime AI Cost
= ₹0 per run
```

At the stated volume:

```text
650 tickets/week
× 4.33 weeks/month
≈ 2,815 tickets/month
```

The local processing benchmark described in the project processes:

```text
11,750 tickets
in under 1 second
```

Therefore the stated monthly runtime AI cost remains:

```text
₹0
```

---

# 🔬 Validation

The project includes two validation paths.

## Independent Validation

```bash
python -m validation.run_validation
```

This writes:

```text
validation/results.json
```

---

## Automated Tests

```bash
python -m pytest -q tests
```

The tests cover:

- Accuracy
- Independent recomputation
- Edge cases
- Analytical calculations

---

# 🧪 Validation Architecture

```text
                    Source Data
                        │
                        ▼
                 Dashboard Pipeline
                        │
              ┌─────────┴─────────┐
              │                   │
              ▼                   ▼
        Streamlit Output    Independent Validation
                                  │
                                  ▼
                           results.json
                                  │
                                  ▼
                              Pytest
```

The independent recomputation provides a separate check against the dashboard calculations.

---

# 📁 Project Structure

```text
vireo-audio-support-analytics/
│
├── app.py
│
├── vireo/
│   ├── data.py              # Cleaning, joins, and flags
│   ├── metrics.py           # Agent metrics, adjustment, business case
│   └── themes.py            # Regex issue taxonomy
│
├── data/
│   ├── tickets.csv
│   ├── agents.csv
│   ├── orders.csv
│   ├── customers.csv
│   └── products.csv
│
├── validation/
│   └── run_validation.py
│
├── tests/
│   └── ...
│
├── validation/
│   └── results.json
│
├── requirements.txt
├── .env.example
├── submission-form.md
└── README.md
```

> The five CSV files contain customer names and are therefore git-ignored. The project distribution includes them in the supplied ZIP.

---

# 🚀 Getting Started

## Prerequisites

- Python **3.10+**
- Python 3.12 used during development
- Streamlit
- Project dependencies from `requirements.txt`

---

## 1. Create Virtual Environment

### Linux / macOS

```bash
python -m venv .venv
source .venv/bin/activate
```

### Windows

```bash
python -m venv .venv
.venv\Scripts\activate
```

---

## 2. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 3. Add Dataset

Place the five CSV files inside:

```text
data/
├── tickets.csv
├── agents.csv
├── orders.csv
├── customers.csv
└── products.csv
```

The data directory is git-ignored because the customer data contains names.

---

## 4. Start Dashboard

```bash
streamlit run app.py
```

The Streamlit application will open in the browser.

---

# ⚙️ Configuration

No environment variables are required for normal operation.

An optional variable is available:

```env
VIREO_DATA_DIR=data
```

The default data directory is:

```text
data
```

See:

```text
.env.example
```

for the configuration example.

---

# 🔄 Example Analyst Workflow

A typical analysis flow is:

```text
1. Executive Summary
        │
        ▼
Read Pulse 2 lot finding
        │
        ▼
2. Agent Performance
        │
        ▼
Filter by team
        │
        ▼
Sort by adjusted gap
        │
        ▼
3. Bottom 10
        │
        ▼
Compare raw ranking
vs coaching priority
        │
        ▼
4. Review flagged agents
        │
        ▼
Inspect individual tickets
before allocating training budget
```

---

# ⚠️ Known Limitations

## CSAT Response Rate

The CSAT response rate is:

```text
44%
```

There is no available mechanism in the analysis to test for non-response bias.

---

## Case Difficulty

Case difficulty is controlled only through recorded fields.

A customer-tone proxy based on angry wording was tested but showed no difference.

However, the proxy is crude, and the triage rota may still receive harder tickets than the recorded variables capture.

---

## Lot Linkage

Approximately:

```text
8%
```

of tickets cannot be tied to a lot.

Additionally:

```text
933 tickets
```

have several orders for the same customer and SKU.

Therefore, the replacement-cost estimate should be interpreted as a **lower bound**.

---

## Pre-Order-Dated Tickets

There are:

```text
255 tickets
```

dated before their associated order date.

These records are not corrected in the current analysis.

---

## Tier 2 Handle Time

Tier 2 cases are multi-touch.

Therefore, handle time measured in days is not directly comparable with Tier 1.

---

## Agent Roster

The current agent roster contains one row per agent.

Therefore, changes such as:

- Shift
- Site
- Assignment location

are not modeled.

---

# 🚫 Deliberately Excluded

The following analyses were intentionally excluded from the current scope:

- LLM classification
- Repeat-contact 30-day costing
- SLA breach credit analysis
- Shift/site effects
- Refund reason-code audit
- Authentication

SLA breach rate is computed per agent but is **not costed**.

---

# 🧠 Methodology Summary

```text
                    Raw Data
                       │
                       ▼
               Data Quality Rules
                       │
                       ▼
                  Data Joins
                       │
                       ▼
              Issue Classification
                       │
                       ▼
               Agent Performance
                       │
             ┌─────────┴─────────┐
             │                   │
             ▼                   ▼
         Raw CSAT          Expected CSAT
                                 │
                                 ▼
                           Adjusted Gap
                                 │
                                 ▼
                       Coaching Priority
                                 │
                                 ▼
                       Ticket-Level Review
```

Alongside the agent analysis:

```text
Product / Lot Data
       │
       ▼
Defective Lot Detection
       │
       ▼
Replacement Analysis
       │
       ▼
Excess Replacement Estimate
       │
       ▼
Business Cost
```

---

# 🎯 Key Analytical Outputs

| Output | Purpose |
|---|---|
| CSAT by Agent | Measure observed customer satisfaction |
| Handle Time | Understand resolution duration |
| Raw Bottom 10 | Provide the client's requested ranking |
| Adjusted Gap | Account for recorded case mix |
| Coaching Priority | Identify agents meeting review criteria |
| Issue Themes | Categorize support problems |
| Defective Lot Analysis | Investigate product-driven CSAT impact |
| Excess Replacements | Estimate operational impact |
| Business Case | Translate replacement volume into cost |
| Data Quality | Make cleaning assumptions visible |

---

# 📌 Engineering Highlights

### Deterministic Analytics

The same input data produces reproducible outputs without external model calls.

### Case-Mix Adjustment

Agent performance is evaluated against expected CSAT derived from recorded case characteristics.

### Empirical Bayes Shrinkage

Small samples are prevented from dominating the coaching-priority analysis.

### Product Investigation

Agent analytics are combined with product, order, and lot information to identify operational drivers.

### Independent Validation

Core calculations are independently recomputed rather than relying exclusively on dashboard output.

### Zero Runtime AI Cost

The deployed analysis does not require an LLM or external API.

### Transparent Methodology

Cleaning rules, exclusions, limitations, and business-case calculations are surfaced instead of hidden inside the dashboard.

---

# 📊 Business Impact Summary

```text
CSAT Decline
     │
     ├─────────────────────────────┐
     │                             │
     ▼                             ▼
Agent Performance             Product Issue
     │                             │
     ▼                             ▼
Case-Mix Adjustment          Pulse 2 Lot Finding
     │                             │
     ▼                             ▼
Coaching Priority           Excess Replacements
                                   │
                                   ▼
                              ~₹9.4 lakh
                              Q1 2026 impact
```

The analysis therefore avoids treating the CSAT decline as solely an agent-performance problem and also investigates the product-related replacement driver.

---

# 👨‍💻 Author

<div align="center">

### Devansh Negi

**Backend / AI Engineer**

Python • Data Analytics • FastAPI • Machine Learning • AI Systems

[![GitHub](https://img.shields.io/badge/GitHub-devanshnegi88-181717?style=flat-square&logo=github&logoColor=white)](https://github.com/devanshnegi88)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-Devansh%20Negi-0A66C2?style=flat-square&logo=linkedin&logoColor=white)](https://linkedin.com/in/devansh-negi005)

</div>

---

<div align="center">

## 🎧 Vireo Audio Support Analytics

**Deterministic analytics for understanding CSAT, coaching priorities, and product-driven support costs.**

</div>