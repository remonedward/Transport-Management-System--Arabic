import sys
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QTableWidget, QTableWidgetItem, QMessageBox,
                             QComboBox, QDialog, QFormLayout, QLineEdit, QLabel,
                             QAbstractItemView, QFileDialog, QListWidget)
from PyQt5.QtCore import Qt
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Employee, Route, RouteCost  # استيراد نماذج قاعدة البيانات
import pandas as pd  # لتصدير التقرير إلى Excel
import logging

# إعداد التسجيل لتتبع الأخطاء
logging.basicConfig(filename='app.log', level=logging.DEBUG, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

# دالة للحصول على المسار الصحيح سواء في وضع التنفيذ أو التطوير
def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(".")
    target_path = os.path.join(os.path.dirname(sys.executable), relative_path)
    if not os.path.exists(target_path) and hasattr(sys, '_MEIPASS'):
        import shutil
        shutil.copy(os.path.join(base_path, relative_path), target_path)
    return target_path

DATABASE_URL = f"sqlite:///{resource_path('transport_management.db')}"
# Database URL
#DATABASE_URL = "sqlite:///transport_management.db"
engine = create_engine(DATABASE_URL)
Base.metadata.bind = engine
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
session = SessionLocal()

class DataEntryDialog(QDialog):
    """
    نافذة حوار لإدخال بيانات جديدة إلى جدول محدد.
    """
    def __init__(self, table_name, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"إدخال بيانات إلى جدول {table_name}")
        self.table_name = table_name
        self.layout = QFormLayout(self)
        self.inputs = {}
        self.model = None

        if table_name == 'employees':
            self.model = Employee
            self.inputs['employee_name'] = QLineEdit()
            self.inputs['department'] = QLineEdit()
            self.inputs['station'] = QLineEdit()
            self.inputs['route_code'] = QLineEdit()
            self.layout.addRow("اسم الموظف:", self.inputs['employee_name'])
            self.layout.addRow("القسم:", self.inputs['department'])
            self.layout.addRow("المحطة:", self.inputs['station'])
            self.layout.addRow("رمز خط السير:", self.inputs['route_code'])
        elif table_name == 'routes':
            self.model = Route
            self.inputs['route_name'] = QLineEdit()
            self.inputs['route_code'] = QLineEdit()
            self.inputs['vehicle_type'] = QLineEdit()
            self.inputs['contractor_name'] = QLineEdit()
            self.inputs['supervisor_name'] = QLineEdit()
            self.inputs['route_stations'] = QLineEdit()
            self.layout.addRow("اسم خط السير:", self.inputs['route_name'])
            self.layout.addRow("رمز خط السير:", self.inputs['route_code'])
            self.layout.addRow("نوع المركبة:", self.inputs['vehicle_type'])
            self.layout.addRow("اسم المتعاقد:", self.inputs['contractor_name'])
            self.layout.addRow("اسم المشرف:", self.inputs['supervisor_name'])
            self.layout.addRow("محطات خط السير:", self.inputs['route_stations'])
        elif table_name == 'route_costs':
            self.model = RouteCost
            self.inputs['route_code'] = QLineEdit()
            self.inputs['vehicle_capacity'] = QLineEdit()
            self.inputs['cost_5_days'] = QLineEdit()
            self.inputs['cost_4_days'] = QLineEdit()
            self.inputs['cost_3_days'] = QLineEdit()
            self.layout.addRow("رمز خط السير:", self.inputs['route_code'])
            self.layout.addRow("سعة المركبة:", self.inputs['vehicle_capacity'])
            self.layout.addRow("تكلفة 5 أيام:", self.inputs['cost_5_days'])
            self.layout.addRow("تكلفة 4 أيام:", self.inputs['cost_4_days'])
            self.layout.addRow("تكلفة 3 أيام:", self.inputs['cost_3_days'])

        self.save_button = QPushButton("حفظ", self)
        self.cancel_button = QPushButton("إلغاء", self)
        self.layout.addRow(self.save_button, self.cancel_button)

        self.save_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)

    def get_data(self):
        """
        Returns:
            dict: قاموس يحتوي على البيانات التي تم إدخالها.
                  إذا تم الإلغاء، يتم إرجاع None.
        """
        if self.result() == QDialog.Accepted:
            data = {}
            for key, widget in self.inputs.items():
                data[key] = widget.text()
            return data
        else:
            return None



class EmployeeAttendanceDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("اختيار الموظفين المطلوب حضورهم")
        self.layout = QVBoxLayout(self)
        
        # تخزين قائمة الموظفين عند التهيئة
        self.all_employees = []
        try:
            logging.info("جاري تحميل قائمة الموظفين من قاعدة البيانات")
            employees = session.query(Employee).all()
            self.all_employees = [emp.employee_name for emp in employees 
                                if emp.employee_name is not None and isinstance(emp.employee_name, str)]
            logging.info(f"تم تحميل {len(self.all_employees)} موظف بنجاح")
        except Exception as e:
            logging.error(f"خطأ أثناء تحميل الموظفين: {str(e)}")
            QMessageBox.critical(self, "خطأ", f"خطأ في تحميل الموظفين: {str(e)}")

        # حقل البحث
        self.search_label = QLabel("ابحث عن موظف:")
        self.layout.addWidget(self.search_label)
        
        self.search_input = QLineEdit()
        self.search_input.textChanged.connect(self.filter_employees)
        self.layout.addWidget(self.search_input)
        
        # قائمة الموظفين المتاحين
        self.employee_list = QListWidget()
        self.employee_list.addItems(self.all_employees)
        self.employee_list.setSelectionMode(QAbstractItemView.SingleSelection)
        self.layout.addWidget(self.employee_list)
        
        # قائمة الموظفين المختارين
        self.selected_label = QLabel("الموظفون المختارون:")
        self.layout.addWidget(self.selected_label)
        
        self.selected_employees = QListWidget()
        self.layout.addWidget(self.selected_employees)
        
        # أزرار التحكم
        self.add_button = QPushButton("إضافة موظف")
        self.add_button.clicked.connect(self.add_employee)
        self.layout.addWidget(self.add_button)
        
        self.remove_button = QPushButton("إزالة موظف")
        self.remove_button.clicked.connect(self.remove_employee)
        self.layout.addWidget(self.remove_button)
        
        self.generate_button = QPushButton("إصدار التقرير")
        self.generate_button.clicked.connect(self.generate_report)
        self.layout.addWidget(self.generate_button)
        
        self.cancel_button = QPushButton("إلغاء")
        self.cancel_button.clicked.connect(self.reject)
        self.layout.addWidget(self.cancel_button)

    def filter_employees(self, text):
        """تصفية قائمة الموظفين بناءً على النص المدخل"""
        try:
            logging.info(f"جاري تصفية القائمة بناءً على النص: {text}")
            self.employee_list.clear()
            if not text.strip():
                self.employee_list.addItems(self.all_employees)
            else:
                filtered = [name for name in self.all_employees if text.lower() in name.lower()]
                self.employee_list.addItems(filtered)
            logging.info("تمت التصفية بنجاح")
        except Exception as e:
            logging.error(f"خطأ أثناء تصفية القائمة: {str(e)}")
            QMessageBox.critical(self, "خطأ", f"خطأ أثناء التصفية: {str(e)}")

    def add_employee(self):
        """إضافة الموظف المختار إلى القائمة"""
        try:
            selected_items = self.employee_list.selectedItems()
            if not selected_items:
                return
            employee_name = selected_items[0].text()
            logging.info(f"محاولة إضافة الموظف: {employee_name}")
            if employee_name not in [self.selected_employees.item(i).text() 
                                   for i in range(self.selected_employees.count())]:
                self.selected_employees.addItem(employee_name)
                logging.info(f"تمت إضافة الموظف: {employee_name}")
            self.search_input.clear()  # مسح حقل البحث بعد الإضافة
        except Exception as e:
            logging.error(f"خطأ أثناء إضافة الموظف: {str(e)}")
            QMessageBox.critical(self, "خطأ", f"خطأ أثناء إضافة الموظف: {str(e)}")

    def remove_employee(self):
        """إزالة موظف من القائمة"""
        try:
            current_row = self.selected_employees.currentRow()
            if current_row >= 0:
                removed_employee = self.selected_employees.item(current_row).text()
                self.selected_employees.takeItem(current_row)
                logging.info(f"تمت إزالة الموظف: {removed_employee}")
        except Exception as e:
            logging.error(f"خطأ أثناء إزالة الموظف: {str(e)}")
            QMessageBox.critical(self, "خطأ", f"خطأ أثناء إزالة الموظف: {str(e)}")

    def get_selected_employees(self):
        return [self.selected_employees.item(i).text() 
                for i in range(self.selected_employees.count())]

    def generate_report(self):
        selected_employees = self.get_selected_employees()
        if not selected_employees:
            QMessageBox.warning(self, "تحذير", "يرجى اختيار موظف واحد على الأقل")
            return

        # Generate report data
        report_data = {}
        total_cost = 0
        
        # قائمة لتتبع خطوط السير المستخدمة لتجنب التكرار
        used_routes = set()
        
        for emp_name in selected_employees:
            employee = session.query(Employee).filter(Employee.employee_name == emp_name).first()
            if employee:
                route = session.query(Route).filter(Route.route_code == employee.route_code).first()
                cost = session.query(RouteCost).filter(RouteCost.route_code == employee.route_code).first()
                
                if route and cost:
                    if route.route_code not in report_data:
                        report_data[route.route_code] = {
                            'vehicle_type': route.vehicle_type,
                            'stations': route.route_stations.split(','),
                            'station_counts': {},
                            'cost_5_days': float(cost.cost_5_days),
                            'vehicle_capacity': int(cost.vehicle_capacity)
                        }
                        # إضافة التكلفة مرة واحدة فقط لكل خط سير
                        if route.route_code not in used_routes:
                            total_cost += float(cost.cost_5_days)
                            used_routes.add(route.route_code)
                    
                    station = employee.station
                    report_data[route.route_code]['station_counts'][station] = \
                        report_data[route.route_code]['station_counts'].get(station, 0) + 1

        # Prepare data for Excel
        excel_data = []
        for route_code, data in report_data.items():
            for station in data['stations']:
                count = data['station_counts'].get(station, 0)
                excel_data.append({
                    'خط السير': route_code,
                    'نوع المركبة': data['vehicle_type'],
                    'المحطة': station,
                    'عدد الركاب': count,
                    'تكلفة السيارة (5 أيام)': data['cost_5_days']
                })
        excel_data.append({'خط السير': 'الإجمالي', 'تكلفة السيارة (5 أيام)': total_cost})

        # Convert to DataFrame
        df = pd.DataFrame(excel_data)

        # Show report summary
        report_text = "تقرير النقل اليومي\n================\n\n"
        for route_code, data in report_data.items():
            report_text += f"خط السير: {route_code}\nنوع المركبة: {data['vehicle_type']}\n"
            report_text += "المحطات وعدد الركاب:\n"
            for station in data['stations']:
                count = data['station_counts'].get(station, 0)
                report_text += f"  - {station}: {count} راكب\n"
            report_text += f"تكلفة السيارة (5 أيام): {data['cost_5_days']} جنيه\n----------------\n"
        report_text += f"الإجمالي الكلي للتكلفة اليومية: {total_cost:.2f} جنيه\n"
        QMessageBox.information(self, "التقرير", report_text)
        
        # Ask to save as Excel
        save = QMessageBox.question(self, "حفظ التقرير", 
                                  "هل تريد حفظ التقرير كملف Excel؟",
                                  QMessageBox.Yes | QMessageBox.No)
        
        if save == QMessageBox.Yes:
            file_name, _ = QFileDialog.getSaveFileName(self, "حفظ التقرير", "", "Excel Files (*.xlsx)")
            if file_name:
                df.to_excel(file_name, index=False, engine='openpyxl')
                QMessageBox.information(self, "نجاح", "تم حفظ التقرير بنجاح كملف Excel")
        
        self.accept()
    

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Transport Management >>ALASKA<< $$ By_R E M O $$ ")
        self.setGeometry(100, 100, 1200, 800)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        self.inspector = inspect(engine)
        self.table_names = self.inspector.get_table_names()
        self.model_mapping = {
            'employees': Employee,
            'routes': Route,
            'route_costs': RouteCost,
        }

        self.setup_ui()

    def setup_ui(self):
        table_selection_layout = QHBoxLayout()
        table_label = QLabel("اختر الجدول:")
        self.table_combo = QComboBox()
        self.table_combo.addItems(self.model_mapping.keys())
        self.table_combo.currentIndexChanged.connect(self.display_table_data)
        table_selection_layout.addWidget(table_label)
        table_selection_layout.addWidget(self.table_combo)
        self.layout.addLayout(table_selection_layout)

        self.data_table = QTableWidget()
        self.layout.addWidget(self.data_table)

        buttons_layout = QHBoxLayout()
        self.add_data_button = QPushButton("إضافة بيانات")
        self.add_data_button.clicked.connect(self.add_data)
        self.edit_data_button = QPushButton("تعديل البيانات")
        self.edit_data_button.clicked.connect(self.edit_data)
        self.report_button = QPushButton("إصدار تقرير الحضور")
        self.report_button.clicked.connect(self.generate_attendance_report)
        self.close_button = QPushButton("إغلاق")# زر الإغلاق الجديد
        self.close_button.clicked.connect(self.close_application)
        buttons_layout.addWidget(self.add_data_button)
        buttons_layout.addWidget(self.edit_data_button)
        buttons_layout.addWidget(self.report_button)
        buttons_layout.addWidget(self.close_button)  # إضافة الزر إلى التخطيط
        self.layout.addLayout(buttons_layout)

        self.display_table_data(0)
        
    def close_application(self):
        """دالة لإغلاق التطبيق مع إغلاق جلسة قاعدة البيانات"""
        try:
            session.close()  # إغلاق جلسة قاعدة البيانات
            QApplication.quit()  # إغلاق التطبيق بالكامل
        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"خطأ أثناء إغلاق التطبيق: {str(e)}")    

    def display_table_data(self, index):
        table_name = self.table_combo.currentText()
        if table_name in self.model_mapping:
            model = self.model_mapping[table_name]
            try:
                data = session.query(model).all()
                self.populate_table(data, model)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error loading data: {e}")
                session.rollback()
        else:
            QMessageBox.warning(self, "Warning", f"No SQLAlchemy model found for table: {table_name}")

    def populate_table(self, data, model):
        self.data_table.clear()
        self.data_table.setRowCount(0)
        self.data_table.setColumnCount(0)

        if not data:
            return

        columns = [column.key for column in model.__table__.columns]
        self.data_table.setColumnCount(len(columns))
        self.data_table.setHorizontalHeaderLabels(columns)

        for row_index, record in enumerate(data):
            self.data_table.insertRow(row_index)
            for col_index, column_name in enumerate(columns):
                value = getattr(record, column_name)
                self.data_table.setItem(row_index, col_index, QTableWidgetItem(str(value)))
        self.data_table.setEditTriggers(QAbstractItemView.NoEditTriggers)

    def add_data(self):
        table_name = self.table_combo.currentText()
        dialog = DataEntryDialog(table_name, self)
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.get_data()
            if data:
                try:
                    if table_name == 'employees':
                        new_employee = Employee(
                            employee_name=data['employee_name'],
                            department=data['department'],
                            station=data['station'],
                            route_code=data['route_code'],
                        )
                        session.add(new_employee)
                    elif table_name == 'routes':
                        new_route = Route(
                            route_name=data['route_name'],
                            route_code=data['route_code'],
                            vehicle_type=data['vehicle_type'],
                            contractor_name=data['contractor_name'],
                            supervisor_name=data['supervisor_name'],
                            route_stations=data['route_stations'],
                        )
                        session.add(new_route)
                    elif table_name == 'route_costs':
                        new_route_cost = RouteCost(
                            route_code=data['route_code'],
                            vehicle_capacity=data['vehicle_capacity'],
                            cost_5_days=data['cost_5_days'],
                            cost_4_days=data['cost_4_days'],
                            cost_3_days=data['cost_3_days'],
                        )
                        session.add(new_route_cost)

                    session.commit()
                    QMessageBox.information(self, "Success", "Data added successfully.")
                    self.display_table_data(self.table_combo.currentIndex())
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Error adding data: {e}")
                    session.rollback()
        dialog.deleteLater()

    def edit_data(self):
        table_name = self.table_combo.currentText()
        selected_row = self.data_table.currentRow()
        if selected_row == -1:
            QMessageBox.warning(self, "Warning", "Please select a row to edit.")
            return

        model = self.model_mapping[table_name]
        primary_key_column = model.__table__.primary_key.columns.values()[0].name
        primary_key_value = self.data_table.item(selected_row, 0).text()

        record_to_edit = session.query(model).filter(getattr(model, primary_key_column) == primary_key_value).first()

        if not record_to_edit:
            QMessageBox.warning(self, "Warning", "Record to edit not found.")
            return

        dialog = DataEntryDialog(table_name, self)
        for key, widget in dialog.inputs.items():
            set_value = getattr(record_to_edit, key)
            if set_value:
                widget.setText(str(set_value))

        if dialog.exec_() == QDialog.Accepted:
            edited_data = dialog.get_data()
            if edited_data:
                try:
                    for key, value in edited_data.items():
                        setattr(record_to_edit, key, value)
                    session.commit()
                    QMessageBox.information(self, "Success", "Data edited successfully.")
                    self.display_table_data(self.table_combo.currentIndex())
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Error editing data: {e}")
                    session.rollback()
        dialog.deleteLater()

    def generate_attendance_report(self):
        dialog = EmployeeAttendanceDialog(self)
        dialog.exec_()
        dialog.deleteLater()

    def closeEvent(self, event):
        session.close()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())
