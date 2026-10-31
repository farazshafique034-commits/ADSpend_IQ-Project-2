# AdSpend IQ — Digital Advertising Budget Optimizer

## Big Data Analytics | Project 2

**Student:** Faraz Shafique  
**Student ID:** F2023376197  
**Section:** A4  
**Subject:** Big Data Analytics

## Overview

AdSpend IQ is an interactive marketing intelligence
dashboard built with Python, Streamlit, and Plotly.

The project analyzes digital advertising campaigns
across Facebook, Instagram, Google, TikTok,
and YouTube.

It also connects with Project 1 — SHEIN Reviews
Sentiment Analysis — to provide additional
customer-feedback insights.

## Features

- Interactive executive dashboard
- Campaign performance analytics
- Audience and demographic insights
- CTR, CPC, CPA, CVR, and ROAS calculations
- Big Data processing benchmark dashboard
- Marketing budget optimization engine
- Adjustable budget and allocation constraints
- SHEIN sentiment analysis integration
- Positive, negative, neutral, and mixed sentiments
- Marketing recommendations
- CSV, JSON, HTML, and ZIP reporting

## Technology Stack

- Python
- Streamlit
- Pandas
- NumPy
- Plotly
- SciPy
- Google Colab for Big Data experiments

## Installation

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m streamlit run app.py
```

Open http://localhost:8501

## Project 1 Connection

Project 1 analyzes SHEIN-related YouTube comments.

Project 2 can import the sentiment analysis CSV
to provide customer-feedback recommendations
alongside advertising performance analysis.

Project 1 repository:

https://github.com/farazshafique034-commits/SHEIN-REVIEWS-SENTIMENT-ANALYSIS

## Data

The demonstration advertising dataset is synthetic.

Budget recommendations use simulated historical
performance and assumed diminishing returns.

They are not guaranteed real-world forecasts.

## Testing

```powershell
python -m unittest discover -s tests -p "test_*.py" -v
```

## Author

Faraz Shafique  
F2023376197  
Big Data Analytics — Section A4
