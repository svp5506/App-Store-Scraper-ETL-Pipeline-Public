# Automated App Stats Scraper 📊

This project scrapes app ratings, review statistics, and rankings from the iOS App Store and Google Play Store for a list of telecom-related apps. The collected data is stored in a PostgreSQL database and can be viewed via a Flask web interface or accessed through an API.

<p align="center">
  <a href="https://www.python.org/"><img src="https://img.shields.io/badge/Python-3.x-blue.svg?logo=python&logoColor=white" alt="Python Version"></a>
  <a href="https://flask.palletsprojects.com/"><img src="https://img.shields.io/badge/Flask-2.x-black.svg?logo=flask&logoColor=white" alt="Powered by Flask"></a>
  <a href="https://www.postgresql.org/"><img src="https://img.shields.io/badge/Database-PostgreSQL-blue.svg?logo=postgresql&logoColor=white" alt="Database: PostgreSQL"></a>
  <a href="https://www.heroku.com/"><img src="https://img.shields.io/badge/Heroku-Deployed-430098.svg?logo=heroku&logoColor=white" alt="Deployed on Heroku"></a>
  <a href="LICENSE_PLACEHOLDER.md"><img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License: MIT"></a>
</p>

---

## ⚙️ How the ETL Process Works

This project uses an automated ETL (Extract, Transform, Load) process to keep your app performance data up-to-date:

-   **Extract:** 📲 The system automatically collects (scrapes) app ratings, reviews, and rankings from both the iOS App Store and Google Play Store for each app in your defined list.
-   **Transform:** 🔄 The collected data is cleaned and standardized. This includes:
    -   Converting ratings and review counts to consistent numerical formats.
    -   Merging iOS and Android data for each app.
    -   Calculating combined ratings, total reviews, and generating overall app rankings.
-   **Load:** 💾 The processed data is saved into a secure PostgreSQL database. This enables easy reporting, dashboard creation, and historical data tracking.

**In summary:** You'll always have access to up-to-date, accurate, and comparable app performance data from both major app stores, ready for business analysis and informed decision-making.

---

## ✨ Features

-   Scrapes ratings, reviews, and rankings for both iOS and Android apps.
-   Stores daily statistics in a PostgreSQL database.
-   Provides a web dashboard to view and compare app statistics.
  
---

## 📁 Project Structure

├── scraper.py         # Main script for scraping and inserting data <br>
├── app.py             # Flask web server and API <br>
├── appURLs.py         # Dictionary of app names and their store URLs <br>
├── dataDetailed.json  # Latest scraped data (updated by scraper) <br>
├── templates/ <br>
│  └── index.html     # Web dashboard template <br>
├── requirements.txt   # Python dependencies <br>
└── Procfile           # For Heroku deployment with Gunicorn


---

## 🚀 Setup

1.  **Clone the repository:**
    ```bash
    git clone <your-repository-url>
    cd <repository-directory>
    ```

2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Set up PostgreSQL:**
    -   Ensure you have a PostgreSQL database created.
    -   Set the DATABASE_URL environment variable to your database connection string (e.g., postgresql://user:password@host:port/database). This is typically used for deployment (e.g., Heroku) and is the primary recommended method.
    -   For local development or alternative setups where environment variables are not used, you may need to add or update your database URL directly within the app.py and scraper.py files where the database connection is initialized.

4.  **Run the scraper:**
    ```bash
    python scraper.py
    ```
    This will scrape the latest stats and insert them into the database. It will also update `dataDetailed.json`.

5.  **Run the web server:**
    ```bash
    python app.py
    ```
    Or, for a production-like environment using Gunicorn:
    ```bash
    gunicorn app:app
    ```

6.  **View the dashboard:**
    Open your web browser and navigate to [http://localhost:5000](http://localhost:5000).

---

## 🛠️ Customization

-   **To add, remove, or modify apps:** Edit the `app_urls` dictionary in the `appURLs.py` file.
    ```python
    # Example from appURLs.py
    app_urls = {
        "App Name 1": {
            "ios": "[https://apps.apple.com/us/app/app-name-1/id123456789](https://apps.apple.com/us/app/app-name-1/id123456789)",
            "android": "[https://play.google.com/store/apps/details?id=com.example.app1](https://play.google.com/store/apps/details?id=com.example.app1)"
        },
        # ... more apps
    }
    ```
-   **To customize the web dashboard's appearance:** Modify the HTML and CSS within `templates/index.html`.

---

## 📊 Data View

You can also view the latest app stats directly in a tabular format via this [Heroku DataClip](https://data.heroku.com/dataclips/ctivnnjqlkpalkxnltdlboovepmn).
