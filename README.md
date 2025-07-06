# 🌿 SmartField Supervisor Dashboard

The **SmartField Dashboard** is a Django-based web platform designed for agricultural researchers to manage and visualize trait-based field data collected from trials. It supports dynamic trait tracking, field mapping, GPS visualization, time-based reminders, and **BrAPI v2** API integration for interoperability with bioinformatics systems.

---

## 🚀 Features

- ✅ Upload CSV files for both **trait data** and **trait schedule**
- 🧬 Visualize trait completion using an interactive **color-coded heatmap**
- 📊 Access **trait status tables** with export options (CSV, Excel, PDF, Print)
- 🖊️ Edit trait values inline via **AJAX-enabled UI**
- 📈 Snapshot and track **trait history** per plant
- 🌍 View **GPS-mapped field plots** and coordinate visualizations
- ⏳ Trait reminders based on **planting dates** and **expected timelines**
- 🧠 Auto status detection:
  - ✔️ Complete
  - ⏳ Due soon
  - ❌ Overdue
  - 🕓 Too early
- 📤 Export detailed **trait summary reports**
- 🔐 Secure **user authentication** and user status management
- 🔎 Searchable, sortable, and paginated tables using **DataTables**
- 🌐 Full support for **BrAPI v2** including:
  - `calls`, `trials`, `studies`, `observationunits`, `observations`
  - `observationvariables`, `programs`, `germplasm`, `locations`, `commoncropnames`
  - `studies/{studyDbId}/observationunits`, `germplasm/{germplasmDbId}`, etc.

---

## 📦 Installation

Clone the repository:

```bash
git clone https://github.com/henrymwaka/SmartFieldDashboard.git
cd SmartFieldDashboard
