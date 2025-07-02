# 🌿 SmartField Supervisor Dashboard

The **SmartField Dashboard** is a Django-based web platform for managing and visualizing trait-based field data collected from agricultural research plots. It provides real-time insights into trait completion, plant statuses, GPS mapping, historical tracking, and trait-specific visualizations.

---

## 🚀 Features

- ✅ Upload CSV files containing field data and trait schedule
- 🧬 Visualize trait completion across all plants using a color-coded **heatmap**
- 📊 View a trait status table with export options (CSV, Excel, PDF, Print)
- 🖊️ Edit trait data inline via AJAX
- 📈 Snapshot and view trait history per plant
- 🌍 Visualize GPS-tagged plots on a field map
- ⏳ Time-based reminder logic (based on planting date and expected schedule)
- 🧠 Automatically assign status symbols:
  - ✔️ = Complete
  - ⏳ = Due soon
  - ❌ = Overdue
  - 🕓 = Too early
- 📤 Export CSV summary reports
- 🔐 Secure user login/logout system
- 🔍 Search, sort, and paginate trait data using DataTables

---

## 📦 Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-username/SmartFieldDashboard.git
   cd SmartFieldDashboard
   
   SmartFieldDashboard/
├── dashboard/
│   ├── templates/
│   │   └── dashboard/
│   │       ├── index.html
│   │       ├── trait_status_table.html
│   │       ├── trait_heatmap.html
│   ├── views.py
│   ├── urls.py
│   └── models.py
├── static/
├── media/
├── smartfield_dashboard/
│   └── urls.py
├── README.md
└── requirements.txt



