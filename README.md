# FOSS-CIT Event Management System

A web-based system for the FOSS club to automate event organization, task tracking, file handling, and report generation.

---

## Features
- Dashboard overview of all events
- Event creation with auto Google Drive folders
- Event details: venue, time, description, rounds
- Budget module: item list, auto total, bill upload
- Task assignment & real-time status tracking
- Resource management: posters, content, videos, docs
- One-click PDF report generation

---

## Tech Stack
- Backend: Python (Flask)
- Frontend: HTML5, CSS3, JavaScript (ES6+)
- Database: SQLite3
- Storage: Google Drive API

---

## 📂 Structure
- `backend/` → Flask app & APIs  
- `frontend/` → UI files  
- `database/` → SQLite DB + setup  
- `drive_integration/` → Google Drive handler  
- `utils/` → PDF & helpers  
- `templates/` → Extra templates  

---

## 🛠️ Setup Instructions

### 1. Prerequisites
- Python 3.8+
- Google Cloud Service Account `credentials.json`

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Setup Database
```bash
python database/db_setup.py
```

### 4. Setup Google Drive API
1. Place your service account JSON file inside the `drive_integration/` folder.  
2. **Quota Fix (Important):** Service accounts start with 0GB storage quota. To enable uploads:  
   - Create a folder in your personal Google Drive.  
   - Share that folder with your service account email (give **Editor** access).  
   - Copy the Folder ID from the folder’s URL.  
   - Add it to a `.env` file in the project root:  
     ```bash
     PARENT_DRIVE_FOLDER_ID=your_folder_id_here
     ```

### 5. Run the Application
**Start Backend:**
```bash
python backend/app.py
```



