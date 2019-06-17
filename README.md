## Catalog Flask App
This repository is a part of "items catalog". This repository is a REST API written in python (Flask)

## Getting Started
Open a bash, powershell or cmd terminal.
### Prerequisites
- Python 3
- PIP
- SQLITE3

### Create a virtual environment
#### `python3 -m venv env`

### Activate virtual environment
#### on Windows: `env\Scripts\activate.bat`
#### on Linux: `source env/bin/activate`

### Install dependencies
#### `pip install -r .\requirements.txt`

### Run database migrations
#### `flask db upgrade`

### Populate database
#### 1) `flask shell`
#### 2) on the interactive python shell run the following command `exec(open("populatedb.py").read())`

### `flask run`
Runs the app in the development mode.<br>
Open [http://localhost:5000](http://localhost:5000) to view it in the browser.