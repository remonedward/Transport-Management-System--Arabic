import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Employee, Route, RouteCost

# تحديد قاعدة البيانات
DATABASE_URL = "sqlite:///transport_management.db"
engine = create_engine(DATABASE_URL)
Base.metadata.bind = engine
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def import_data_from_excel(excel_file_path):
    try:
        db = SessionLocal()
        excel_file = pd.ExcelFile(excel_file_path)

        # استيراد بيانات الموظفين
        df_employees = excel_file.parse('Sheet1')
        for index, row in df_employees.iterrows():
            employee = Employee(
                employee_name=row['employee_name'],
                department=row['department'],
                station=row['station'],
                route_code=row['route_code'],
                notes=row['notes']
            )
            db.add(employee)

        # استيراد بيانات خطوط السير
        df_routes = excel_file.parse('Sheet2')
        for index, row in df_routes.iterrows():
            route = Route(
                route_code=row['route_code'],
                route_name=row['route_name'],
                vehicle_type=row['vehicle_type'],
                contractor_name=row['contractor_name'],
                supervisor_name=row['supervisor_name'],
                route_stations=row['route_stations']
            )
            db.add(route)

        # استيراد بيانات تكلفة خطوط السير
        df_costs = excel_file.parse('Sheet3')
        for index, row in df_costs.iterrows():
            cost = RouteCost(
                route_code=row['route_code'],
                vehicle_capacity=row['vehicle_capacity'],
                cost_5_days=row['cost_5_days'],
                cost_4_days=row['cost_4_days'],
                cost_3_days=row['cost_3_days']
            )
            db.add(cost)

        db.commit()
        print("Data has been imported from Excel to the database successfully.")

    except Exception as e:
        db.rollback()
        print(f"An error occurred while importing data.: {e}")

    finally:
        db.close()

if __name__ == "__main__":
    excel_file = '2025.xlsx'  # استبدل باسم ملف Excel الخاص بك
    import_data_from_excel(excel_file)