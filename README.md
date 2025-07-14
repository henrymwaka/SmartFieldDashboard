# 🌿 SmartField Supervisor Dashboard

The **SmartFieldDashboard** is a modular Django-based web platform built for agricultural researchers and field supervisors to manage, monitor, and visualize phenotypic trait data across trials.

It is tightly integrated with the **SmartField ODK-X mobile app** and enables real-time data tracking, field plot mapping, trait status evaluation, and BrAPI v2 interoperability for bioinformatics workflows.

---

## 🚀 Core Features

- ✅ Upload **trait data** and **trait schedule** CSV files
- 🧬 Visualize trait completion via an interactive **color-coded heatmap**
- 📊 View searchable, paginated **trait status tables** with export options (CSV, Excel, PDF)
- 🖊️ Edit trait values **inline** or in bulk with **AJAX-enabled UI**
- 📈 View per-plant **trait history timeline** with modal previews
- ⏳ Auto-generate trait reminders based on **actual planting dates**
- 📤 Generate **summary reports** (PDF, CSV) per snapshot
- 🌍 Visualize **GPS-tagged plots** on a field map
- 🔎 Built-in **status detection** logic for traits:
  - ✔️ Complete
  - ⏳ Due soon
  - ❌ Overdue
  - 🕓 Too early
- 🔐 Role-based user authentication and secure login
- 🧠 BrAPI v2 API support for programmatic data access

---

## 🧬 BrAPI v2 Integration

SmartFieldDashboard offers full compliance with the [BrAPI v2](https://brapi.org/) standard for external integration. Supported endpoints include:

- `calls`, `trials`, `studies`, `observationunits`, `observations`
- `observationvariables`, `programs`, `germplasm`, `locations`, `people`, `methods`
- `studies/{studyDbId}/observationunits`, `germplasm/{germplasmDbId}`, etc.

API documentation:
- [Swagger UI](http://127.0.0.1:8000/swagger/)
- [ReDoc](http://127.0.0.1:8000/redoc/)

---

## 📦 Installation & Setup

```bash
# 1. Clone the repository
git clone https://github.com/henrymwaka/SmartFieldDashboard.git
cd SmartFieldDashboard

# 2. Create a virtual environment
python -m venv env
source env/bin/activate  # On Windows: env\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run migrations
python manage.py migrate

# 5. Start the development server
python manage.py runserver
```

Ensure your PostgreSQL database is configured correctly in `settings.py`.

---

## 🧱 Project Structure

```bash
SmartFieldDashboard/
├── dashboard/
│   ├── urls/                # Modular URLs: traits, GPS, users, etc.
│   ├── templates/dashboard/ # HTML pages
│   ├── static/              # CSS, JS, and assets
│   ├── views/               # Modular views for traits, exports, GPS
│   ├── models.py            # Core models: FieldPlot, TraitData, etc.
│   ├── serializers.py       # BrAPI serializers
│   ├── brapi_views.py       # BrAPI v2 API endpoints
├── media/                   # Uploaded files
├── manage.py
├── requirements.txt
└── README.md
```

---

## 🧪 In Progress

- 🔁 Integration with SmartField ODK-X mobile app for real-time sync
- ⚙️ Auto-generate JSON trait forms from CSV files for mobile deployment
- 🧭 Field GPS view enhancements and map overlays
- 📅 Trait timeline and forecast view per crop
- 🛡️ Admin control panel and full deployment hardening

---

## 📜 Changelog

### [modular-urls-v1] – 2025-07-13

#### Added
- Modular route structure under `dashboard/urls/`
  - `traits`, `planting`, `gps`, `exports`, `users`, `mail`
- Namespaced `include()` paths for better maintainability

#### Removed
- Legacy flat `urls.py` setup

#### Fixed
- All `NoReverseMatch` errors due to template and route mismatches

---

## 🧭 Roadmap

| Milestone                      | Status       |
|-------------------------------|--------------|
| Modular views and routing     | ✅ Complete   |
| BrAPI v2 compliance           | ✅ Complete   |
| AJAX trait editing            | ✅ Complete   |
| GPS mapping and coordinates   | ✅ Done       |
| CSV upload/export             | ✅ Done       |
| ODK-X sync integration        | 🔄 In Progress |
| JSON form auto-generation     | 🔄 In Progress |
| Field pilot deployment        | ⏳ Pending    |
| Railway/VPS deployment        | ⏳ Pending    |

---

## 👨‍🔬 Developed By

**Henry Mwaka**  
PhD in Bioscience Engineering | NARO Uganda  
📧 henry.mwaka@naro.go.ug  
🔗 [GitHub Profile](https://github.com/henrymwaka)

---

## 📘 License

This project is licensed under the **Apache License 2.0** – you're free to use, modify, and distribute with attribution.
