# FOSS-CIT Event Management System

A complete web-based system for the FOSS-CIT college club to automate event organization, task management, file handling, and report generation.

## 🚀 Features
- **Dashboard**: Overview of all club events.
- **Event Creation**: Automated Google Drive folder creation (`Event_Name/` + subfolders).
- **Event Details**: Track venue, time, description, and detailed event flow (rounds).
- **Budget Module**: Items list with auto-calculation and bill upload to Google Drive.
- **Work Status**: Task assignment and tracking with real-time status updates and comments.
- **Resource Management**: Categorized file storage for posters, content, videos, and documents.
- **Report Generation**: Automatic PDF report synthesis with one click.

## 🏗️ Tech Stack
- **Backend**: Python (Flask)
- **Frontend**: HTML5, CSS3 (Vanilla), JavaScript (ES6+)
- **Database**: SQLite3
- **Storage**: Google Drive API

## 📁 Project Structure
- `backend/`: Flask application and API endpoints.
- `frontend/`: UI files (HTML, CSS, JS).
- `database/`: SQLite DB file and setup script.
- `drive_integration/`: Google Drive API handler and credentials.
- `utils/`: PDF generation and other utility scripts.
- `templates/`: Place for additional templates.

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
1. Place your `foss-cit-system-958d05ac0564.json` file inside the `drive_integration/` folder.
2. **Quota Fix (Crucial)**: Service accounts have 0GB quota. To upload files:
   - Create a folder in your **personal Google Drive**.
   - Share that folder with the service account email: `task5-132@foss-cit-system.iam.gserviceaccount.com` (as **Editor**).
   - Copy the Folder ID from the URL (the long string at the end).
   - Create a `.env` file in the root of the project:
     ```bash
     PARENT_DRIVE_FOLDER_ID=your_folder_id_here
     ```

### 5. Run the Application
**Start Backend:**
```bash
python backend/app.py
```
**Static Frontend:**
Open `frontend/index.html` in your browser. (Alternatively, use a Live Server or serve it via Python: `python -m http.server 8000` inside the `frontend` folder).

## 📊 Testing Features
1. Click **"New Event"** to create an event. Verify the folders are created in your Google Drive (if credentials are correct).
2. Use the **Tabs** to navigate between Details, Budget, Tasks, and Resources.
3. **Upload a file** (Bill or Poster) and check the link generated in the UI.
4. Click **"Generate Report"** to download the synthesized PDF.


