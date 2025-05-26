from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Employee, Route, RouteCost

# Database URL
DATABASE_URL = "sqlite:///transport_management.db"
engine = create_engine(DATABASE_URL)
Base.metadata.bind = engine
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_employee_by_name(db: SessionLocal, employee_name: str):
    return db.query(Employee).filter(Employee.employee_name == employee_name).first()

def generate_transport_report(db: SessionLocal, date_str: str, employee_names: list):
    report_data = []
    total_cost = 0
    department_counts = {}

    for name in employee_names:
        employee = get_employee_by_name(db, name)
        if employee:
            report_data.append({
                'Employee Name': employee.employee_name,
                'Department': employee.department,
                'Station': employee.station,
                'Route Name': employee.route.route_name,
                'Vehicle Type': employee.route.vehicle_type,
                'Contractor Name': employee.route.contractor_name,
                'Supervisor Name': employee.route.supervisor_name,
                'Route Stations': employee.route.route_stations,
                'Vehicle Capacity': employee.route.cost.vehicle_capacity,
                'Cost (5 Days)': employee.route.cost.cost_5_days
            })
            total_cost += employee.route.cost.cost_5_days
            department = employee.department
            department_counts[department] = department_counts.get(department, 0) + 1
        else:
            print(f"Employee not found: {name}")

    required_vehicles = {}
    for item in report_data:
        route_name = item['Route Name']
        if route_name not in required_vehicles:
            required_vehicles[route_name] = {
                'Route Name': item['Route Name'],
                'Vehicle Type': item['Vehicle Type'],
                'Contractor Name': item['Contractor Name'],
                'Supervisor Name': item['Supervisor Name'],
                'Route Stations': item['Route Stations'],
                'Passengers': [item['Employee Name']],
                'Vehicle Capacity': item['Vehicle Capacity'],
                'Cost': item['Cost (5 Days)']
            }
        else:
            required_vehicles[route_name]['Passengers'].append(item['Employee Name'])

    print(f"\nTransport Report for Date: {date_str}")

    print("\nAttendance Count by Department:")
    for department, count in department_counts.items():
        print(f"Department: {department}, Attendance Count: {count}")

    print(f"\nRequired Vehicles and Costs:")
    for route_name, details in required_vehicles.items():
        print(f"  Route Name: {details['Route Name']}")
        print(f"    Vehicle Type: {details['Vehicle Type']}")
        print(f"    Contractor Name: {details['Contractor Name']}")
        print(f"    Supervisor Name: {details['Supervisor Name']}")
        print(f"    Route Stations: {details['Route Stations']}")
        print(f"    Passengers: {', '.join(details['Passengers'])}")
        print(f"    Vehicle Capacity: {details['Vehicle Capacity']}")
        print(f"    Cost: {details['Cost']:.2f}")

    print(f"\nTotal Expected Cost for Required Vehicles: {total_cost:.2f}\n")

def analyze_cost_by_department(db: SessionLocal, start_date: str, end_date: str, department_filter: str = None):
    query = db.query(Employee.department, func.count(Employee.employee_id), func.sum(RouteCost.cost_5_days)).\
        join(Route, Employee.route_code == Route.route_code).\
        join(RouteCost, Route.route_code == RouteCost.route_code)

    if department_filter:
        query = query.filter(Employee.department == department_filter)

    results = query.group_by(Employee.department).all()

    #print("\nTransport Cost Analysis by Department:")
    #for department, employee_count, total_cost in results:
        #print(f"Department: {department}, Number of Employees: {employee_count}, Total Cost (Estimated): {total_cost:.2f}")

if __name__ == "__main__":
    db = next(get_db())
    attendance_date = "2025-04-07"
    employees_attending = ["ريمون ادوارد عزيز", "سعدان فخرى اديب ", "صفوت بخيت بخيت"] # Replace with actual employee names
    generate_transport_report(db, attendance_date, employees_attending)
    analyze_cost_by_department(db, "2025-04-01", "2025-04-30", department_filter="الموارد البشرية") # Replace with actual department
    analyze_cost_by_department(db, "2025-04-01", "2025-04-30")