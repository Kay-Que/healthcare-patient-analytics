# 🏥 Healthcare Patient Analytics Dashboard

A modern, interactive **Healthcare Patient Analytics Dashboard** built with Python and Streamlit to analyze patient demographics, medical conditions, hospital activity, billing, medications, and treatment-related data.

The dashboard transforms healthcare records into clear visual insights that can help users understand patient trends, medical patterns, and financial performance.

---

## 📊 Dashboard Features

### 📈 Dashboard

* Total patient count
* Average patient age
* Average billing amount
* Number of medical conditions
* Patient activity overview
* Demographic analysis
* Medical condition analysis
* Test result analysis
* Billing analysis
* Patient records table

### 👥 Patients

* Search and explore patient records
* Sort patients by:

  * Name
  * Age
  * Billing amount
  * Medical condition
  * Admission date
* Pagination for large datasets
* Individual patient detail lookup

### 🩺 Medical Analysis

* Medical condition distribution
* Gender analysis
* Age-group analysis
* Test result analysis
* Medication analysis
* Doctor analysis
* Medical KPIs

### 💰 Billing Analysis

* Total billing
* Average billing
* Highest patient bill
* Lowest patient bill
* Billing by medical condition
* Billing by admission type
* Billing distribution
* Financial insights

### 📄 Reports

* Filter-based report summary
* Patient statistics
* Financial summary
* Medical insights
* Patient record preview
* CSV export
* Excel export

---

## 🛠️ Technologies Used

| Technology | Purpose                               |
| ---------- | ------------------------------------- |
| Python     | Data processing and application logic |
| Streamlit  | Interactive dashboard                 |
| Pandas     | Data analysis and manipulation        |
| Plotly     | Interactive charts                    |
| OpenPyXL   | Excel file processing                 |

---

## 📁 Project Structure

```text
healthcare-patient-analytics/
│
├── app/
│   └── app.py
│
├── data/
│   ├── raw/
│   └── cleaned/
│       └── cleaned_healthcare_dataset.xlsx
│
├── README.md
├── requirements.txt
├── .gitignore
└── LICENSE
```

---

## ⚙️ Installation

### 1. Clone the repository

```bash
git clone https://github.com/Kay-Que/healthcare-patient-analytics
```

### 2. Open the project

```bash
cd healthcare-patient-analytics
```

### 3. Create a virtual environment

```bash
python -m venv venv
```

### 4. Activate the environment

**Windows:**

```bash
venv\Scripts\activate
```

### 5. Install dependencies

```bash
pip install -r requirements.txt
```

### 6. Run the application

```bash
streamlit run app/app.py
```

The dashboard will open in your browser.

---

## 🔍 Key Analytics

The dashboard provides insights into:

* Patient demographics
* Medical conditions
* Admission patterns
* Test results
* Medication usage
* Doctor activity
* Patient billing
* Financial distribution
* Patient-level information

Users can apply filters to analyze specific subsets of the healthcare dataset.

---

## 📊 Data

The project uses a cleaned healthcare patient dataset containing information such as:

* Patient ID
* Patient name
* Age
* Gender
* Medical condition
* Admission type
* Billing amount
* Test results
* Medication
* Admission date
* Discharge date
* Hospital and insurance information where available

> **Note:** This project is intended for analytics, educational, and portfolio purposes. It should not be used for clinical decision-making.

---

## 🎯 Project Objective

The goal of this project is to demonstrate how healthcare data can be transformed into an interactive analytics solution using Python.

The dashboard focuses on making healthcare data easier to explore through **KPIs, interactive charts, filters, patient tables, and downloadable reports**.

---

## 🚀 Future Improvements

Potential future enhancements include:

* Predictive patient-risk analysis
* Hospital performance comparison
* Advanced statistical analysis
* Automated PDF reports
* Machine learning-based predictions
* Cloud deployment
* Role-based dashboard access

---

## 👩‍💻 Author

**Kashaf**

BS Information Technology
Data Analytics & Dashboard Development

---

## ⭐ Project Highlights

* Modern Streamlit dashboard
* Interactive data visualization
* Healthcare-focused analytics
* Responsive UI
* Patient-level analysis
* Financial analysis
* Filter-based reporting
* CSV and Excel export
* Portfolio-ready project
