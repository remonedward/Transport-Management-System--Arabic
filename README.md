[عربي](README_ar.md)

# Transport Management System

A desktop application built with **PyQt5** and **SQLAlchemy** for managing employee transportation logistics, including attendance tracking, route management, and cost analysis. The application integrates with a SQLite database to store and retrieve data, and supports importing data from Excel files for efficient data management.

## Table of Contents
- [Project Overview](#project-overview)
- [Features](#features)
- [Technologies Used](#technologies-used)
- [Setup Instructions](#setup-instructions)
- [Database Schema](#database-schema)
- [Usage](#usage)
- [Sample Data](#sample-data)
- [Contributing](#contributing)
- [License](#license)

## Project Overview
The **Transport Management System** is designed to streamline employee transportation logistics for a company. It allows users to:
- Manage employee, route, and cost data through a user-friendly GUI.
- Generate daily transportation reports based on employee attendance.
- Import data from Excel files into a SQLite database.
- Perform cost analysis by department and export reports to Excel.

This project demonstrates skills in:
- **Desktop Application Development**: Using PyQt5 for a responsive GUI.
- **Database Integration**: Using SQLAlchemy for ORM-based database operations.
- **Data Processing**: Handling Excel data with pandas and openpyxl.
- **Error Handling and Logging**: Robust error management and logging for debugging.

## Features
- **Data Management**: Add, edit, and view employee, route, and cost data in a tabular interface.
- **Attendance Tracking**: Select employees to generate daily transportation reports, including route details, passenger counts, and costs.
- **Data Import**: Import employee, route, and cost data from Excel files into the SQLite database.
- **Cost Analysis**: Analyze transportation costs by department for a specified date range.
- **Excel Export**: Export generated reports to Excel for further analysis.
- **Search Functionality**: Filter employees by name for quick selection in the attendance dialog.
- **Responsive GUI**: Built with PyQt5 for a modern and intuitive user experience.

## Technologies Used
- **Python 3.x**: Core programming language.
- **PyQt5**: For building the graphical user interface.
- **SQLAlchemy**: For database ORM and management.
- **pandas**: For Excel data processing and report generation.
- **openpyxl**: For reading and writing Excel files.
- **SQLite**: Lightweight database for storing employee, route, and cost data.
- **Logging**: For tracking application events and errors.

## Setup Instructions
### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Installation
1. **Clone the Repository**:
   ```bash
   git clone https://github.com/your-username/transport-management-system.git
   cd transport-management-system
   ```

2. **Install Dependencies**:
   Install the required Python packages listed in `requirements.txt`:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set Up the Database**:
   Run the `database_setup.py` script to create the SQLite database and tables:
   ```bash
   python database_setup.py
   ```

4. **Import Sample Data**:
   Use the provided `sample_data.xlsx` file to populate the database with dummy data:
   ```bash
   python data_import.py
   ```
   Alternatively, replace `sample_data.xlsx` with your own Excel file matching the required schema (see [Sample Data](#sample-data)).

5. **Run the Application**:
   Launch the main application:
   ```bash
   python main_app2.py
   ```

## Database Schema
The application uses a SQLite database (`transport_management.db`) with the following tables:

- **employees**:
  - `employee_id` (Integer, Primary Key)
  - `employee_name` (String)
  - `department` (String)
  - `station` (String)
  - `route_code` (String, Foreign Key to `routes`)
  - `notes` (String)

- **routes**:
  - `route_code` (String, Primary Key)
  - `route_name` (String)
  - `vehicle_type` (String)
  - `contractor_name` (String)
  - `supervisor_name` (String)
  - `route_stations` (String, comma-separated)

- **route_costs**:
  - `route_code` (String, Primary Key, Foreign Key to `routes`)
  - `vehicle_capacity` (Integer)
  - `cost_5_days` (Float)
  - `cost_4_days` (Float)
  - `cost_3_days` (Float)

## Usage
1. **Launch the Application**:
   Run `main_app2.py` to open the main window.

2. **View and Manage Data**:
   - Use the dropdown menu to select a table (`employees`, `routes`, or `route_costs`).
   - View data in the table view.
   - Click **Add Data** to insert new records or **Edit Data** to modify existing ones.

3. **Generate Attendance Reports**:
   - Click **Generate Attendance Report** to open the attendance dialog.
   - Search for employees by name, add them to the selected list, and generate a report.
   - View the report summary and optionally save it as an Excel file.

4. **Import Data**:
   - Run `data_import.py` with an Excel file to populate the database.
   - Ensure the Excel file has three sheets (`Sheet1`, `Sheet2`, `Sheet3`) with columns matching the database schema.

## Sample Data
The repository includes a `sample_data.xlsx` file with dummy data to demonstrate the application’s functionality. The file contains:
- **Sheet1**: Employee data (columns: `employee_name`, `department`, `station`, `route_name`, `route_code`, `notes`)
- **Sheet2**: Route data (columns: `route_code`, `route_name`, `vehicle_type`, `contractor_name`, `supervisor_name`, `route_stations`)
- **Sheet3**: Route cost data (columns: `route_code`, `vehicle_capacity`, `cost_5_days`, `cost_4_days`, `cost_3_days`)

To use your own data, create an Excel file with the same structure and update `data_import.py` to reference your file.

## Contributing
Contributions are welcome! Please follow these steps:
1. Fork the repository.
2. Create a new branch (`git checkout -b feature/your-feature`).
3. Make your changes and commit (`git commit -m "Add your feature"`).
4. Push to the branch (`git push origin feature/your-feature`).
5. Create a pull request.

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.