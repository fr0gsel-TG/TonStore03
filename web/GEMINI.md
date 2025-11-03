# GEMINI Project: iPhone Catalog Web App

## Project Overview

This project is a Python-based web application that displays a catalog of iPhones. It consists of two main parts:

1.  **Web Scraper:** A set of Python scripts (`parsing.py`, `fast_pars.py`) that use `BeautifulSoup` and `requests` to parse iPhone product information from an HTML file (`site-html.txt`). The scraped data is then stored in a PostgreSQL database.
2.  **Flask Web Application:** A `Flask` application (`app.py`) that serves the iPhone catalog data from the PostgreSQL database. It provides a web interface to browse and search for iPhones, view product details, and filter by category.

The project uses a PostgreSQL database, which is set up and managed through `web_db_setup.py` and `parsing.py`. The frontend is built with HTML templates located in the `templates/` directory.

## Building and Running

Here are the steps to get the application running:

### 1. Install Dependencies

This project uses Python. Install the required libraries using `pip`:

```bash
pip install -r requirements.txt
```

### 2. Set up the Database and Scrape Data

Before running the web application, you need to create the database and populate it with data from the HTML file.

First, run the parsing script to scrape the data and create the initial database:

```bash
python parsing.py
```

Then, run the database setup script to prepare the database for the web application:

```bash
python web_db_setup.py
```

### 3. Run the Web Application

Once the database is set up, you can run the Flask web application:

```bash
python app.py
```

The application will be available at `http://localhost:5000`.

## Development Conventions

*   **Backend:** The backend is built with Python and the Flask framework.
*   **Database:** The application uses a PostgreSQL database to store product information.
*   **Web Scraping:** Data is collected using `BeautifulSoup` for parsing HTML.
*   **Frontend:** The frontend is rendered using Flask's templating engine with HTML files from the `templates/` directory.
*   **Dependencies:** Project dependencies are managed in the `requirements.txt` file.
