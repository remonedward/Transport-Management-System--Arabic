from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship, declarative_base

# تحديد قاعدة البيانات (يمكنك تغييرها إلى PostgreSQL أو MySQL وغيرها)
DATABASE_URL = "sqlite:///transport_management.db"

# إنشاء محرك قاعدة البيانات
engine = create_engine(DATABASE_URL)

# إنشاء قاعدة أساسية للكائنات
Base = declarative_base()

# تعريف جدول الموظفين
class Employee(Base):
    __tablename__ = "employees"

    employee_id = Column(Integer, primary_key=True, index=True)
    employee_name = Column(String, nullable=False)
    department = Column(String)
    station = Column(String)
    route_code = Column(String, ForeignKey("routes.route_code"))
    notes = Column(String)  # إضافة عمود الملاحظات

    route = relationship("Route", back_populates="employees")

# تعريف جدول خطوط السير
class Route(Base):
    __tablename__ = "routes"

    route_code = Column(String, primary_key=True, index=True)
    route_name = Column(String)
    vehicle_type = Column(String)
    contractor_name = Column(String)
    supervisor_name = Column(String)
    route_stations = Column(String)

    employees = relationship("Employee", back_populates="route")
    cost = relationship("RouteCost", back_populates="route", uselist=False)

# تعريف جدول تكلفة خطوط السير
class RouteCost(Base):
    __tablename__ = "route_costs"

    route_code = Column(String, ForeignKey("routes.route_code"), primary_key=True)
    vehicle_capacity = Column(Integer)
    cost_5_days = Column(Float)
    cost_4_days = Column(Float)
    cost_3_days = Column(Float)

    route = relationship("Route", back_populates="cost")

# إنشاء الجداول في قاعدة البيانات
def create_tables():
    Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    create_tables()
    print("The database and tables were created successfully.")