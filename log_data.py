from PyQt5.QtWidgets import QDialog, QMessageBox
from PyQt5.uic import loadUi
from PyQt5.QtCore import QDateTime, QTimer
import pyodbc

class Log_data():
    def __init__(self,main_window):
        self.shifting_position = None
        self.weld_shift_position = None
        self.weld_miss_position = None
        self.weld_weak_position = None
        self.weld_burn_position = None
        self.cycletime = None
        self.recipe = None
        self.battery_id2 = None
        self.status = None
        self.inspectby = None
        self.positions = None
        self.battery_id = None
        self.shift_num = None
        self.main_window = main_window  # store reference

        self.defect = None
        self.topbottom = None
        # Database connection
        # self.connection_str = (
        #     "DRIVER={ODBC Driver 17 for SQL Server};"
        #     "SERVER=MYPC;"  # Server name
        #     "DATABASE=Rework_Entry_database;"  # Database name (no brackets)
        #     "Trusted_Connection=yes;"
        # )
        self.connection_str = (
            "DRIVER={ODBC Driver 17 for SQL Server};"
            "SERVER=192.168.200.24,1433;"  # Update with your SQL Server name
            "DATABASE=ZONE02_REPORTS;"
            "UID=dbuserz02 ;"
            "PWD=CTPL@123123;"
        )
        # Database connection string
        # conn_str = (
        #     "DRIVER={ODBC Driver 17 for SQL Server};"
        #     "SERVER=192.168.200.24,1433;"  # Update with your SQL Server name
        #     "DATABASE=ZONE01_REPORTS;"
        #     "UID=dbuser;"
        #     "PWD=CTPL@123123;"
        # )

        self.main_window.accept_btn_4.clicked.connect(self.accept)
        self.main_window.rework_btn_4.clicked.connect(self.sendtorework)

        # Top/Bottom
        self.main_window.topbottom_input_5.addItems([" ", "Top", "Bottom", "Top & Bottom"])  # Set initial items#
        self.main_window.topbottom_input_5.currentIndexChanged.connect(self.topbottom_inputs_change)
        # Defect
        # self.main_window.defect_input_4.addItems([" ", "Weld Weak", "Shifting", "Weld Shift", "Weld Burn", "Weld Miss/No Weld"])  # Set initial items#
        # self.main_window.defect_input_4.currentIndexChanged.connect(self.defect_inputs_change)

    def topbottom_inputs_change(self, index):
        self.topbottom = self.main_window.topbottom_input_5.itemText(index)
    def defect_inputs_change(self, index):
        self.defect = self.main_window.defect_input_4.itemText(index)

    def connect_db(self):
        try:
            conn = pyodbc.connect(self.connection_str)
            return conn
        except Exception as e:
            print(f"Database connection error: {e}")
            return None

    def accept(self):
        if self.main_window.is_logged_in:
            # Use current datetime for Created_At and Modified_At
            current_datetime = QDateTime.currentDateTime().toString("yyyy-MM-dd hh:mm:ss")

            try:
                self.shift_num = chr(int(self.main_window.shift))
                self.battery_id = self.main_window.battery_id1
                self.battery_id2 = self.main_window.battery_id2
                self.weld_burn_position = self.main_window.position_input_7.text()
                self.weld_weak_position = self.main_window.position_input_2.text()
                self.weld_miss_position = self.main_window.position_input_3.text()
                self.weld_shift_position = self.main_window.position_input_6.text()
                self.shifting_position = self.main_window.position_input_5.text()

                self.inspectby = self.main_window.loggedinuser
                self.status = 1
                self.recipe = self.main_window.recipe_no
                self.cycletime = self.main_window.cycletime

                if self.battery_id:
                    conn = self.connect_db()
                    if conn:
                        cursor = conn.cursor()
                        # If the row does not exist, insert a new one
                        query = """INSERT INTO [dbo].[Visual_Inspection_Station]
                                   ([DateTime], [Shift], [ModuleBarcodeData], [Top_Bottom], [weld_burn_position], [weld_weak_position],[weld_miss_position] ,[weld_shift_position],[shifting_position], [Operator], [Status], [Recipe], [CycleTime])
                                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""
                        values = (
                            current_datetime, self.shift_num, self.battery_id, self.topbottom, self.weld_burn_position,
                            self.weld_weak_position,self.weld_miss_position, self.weld_shift_position, self.shifting_position,
                            self.inspectby, self.status,self.recipe, self.cycletime)
                        cursor.execute(query, values)
                        QMessageBox.information(self.main_window, "Success", "Data inserted successfully!")
                        conn.commit()
                        cursor.close()
                        conn.close()
                        self.main_window.sendstatusforvisualinspection(1)
                    else:
                        print("Failed to connect to the database.")
                if self.battery_id2:
                    conn = self.connect_db()
                    if conn:
                        cursor = conn.cursor()
                        # If the row does not exist, insert a new one
                        # If the row does not exist, insert a new one
                        query = """INSERT INTO [dbo].[Visual_Inspection_Station]
                                                           ([DateTime], [Shift], [ModuleBarcodeData], [Top_Bottom], [weld_burn_position], [weld_weak_position],[weld_miss_position] ,[weld_shift_position],[shifting_position], [Operator], [Status], [Recipe], [CycleTime])
                                                           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""
                        values = (
                            current_datetime, self.shift_num, self.battery_id2, self.topbottom, self.weld_burn_position,
                            self.weld_weak_position, self.weld_miss_position, self.weld_shift_position,
                            self.shifting_position,
                            self.inspectby, self.status, self.recipe, self.cycletime)
                        cursor.execute(query, values)
                        QMessageBox.information(self.main_window, "Success", "Data inserted successfully!")
                        conn.commit()
                        cursor.close()
                        conn.close()
                        self.main_window.sendstatusforvisualinspection(1)
                    else:
                        print("Failed to connect to the database.")
                self.updatevalues()
            except Exception as e:
                print(f"failed to connect to the database: {e}")
                QMessageBox.critical(self.main_window, "Error", f"Error inserting or updating data: {e}")
        else:
            QMessageBox.critical(self.main_window, "Log in Error", f"Please Log in Before accepting")


    def sendtorework(self):
        if self.main_window.is_logged_in:

            # Use current datetime for Created_At and Modified_At
            current_datetime = QDateTime.currentDateTime().toString("yyyy-MM-dd hh:mm:ss")
            try:
                self.shift_num = chr(int(self.main_window.shift))
                self.battery_id = self.main_window.battery_id1
                self.battery_id2 = self.main_window.battery_id2
                self.weld_burn_position = self.main_window.position_input_7.text()
                self.weld_weak_position = self.main_window.position_input_2.text()
                self.weld_miss_position = self.main_window.position_input_3.text()
                self.weld_shift_position = self.main_window.position_input_6.text()
                self.shifting_position = self.main_window.position_input_5.text()
                self.inspectby = self.main_window.loggedinuser
                self.status = 2
                self.recipe = self.main_window.recipe_no
                self.cycletime = self.main_window.cycletime
                if self.battery_id:
                    conn = self.connect_db()
                    if conn:
                        cursor = conn.cursor()
                        # If the row does not exist, insert a new one

                        # If the row does not exist, insert a new one
                        query = """INSERT INTO [dbo].[Visual_Inspection_Station]
                                                           ([DateTime], [Shift], [ModuleBarcodeData], [Top_Bottom], [weld_burn_position], [weld_weak_position],[weld_miss_position] ,[weld_shift_position],[shifting_position], [Operator], [Status], [Recipe], [CycleTime])
                                                           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""
                        values = (
                            current_datetime, self.shift_num, self.battery_id, self.topbottom, self.weld_burn_position,
                            self.weld_weak_position, self.weld_miss_position, self.weld_shift_position,
                            self.shifting_position,
                            self.inspectby, self.status, self.recipe, self.cycletime)
                        cursor.execute(query, values)
                        QMessageBox.information(self.main_window, "Success", "Data inserted successfully!")
                        conn.commit()
                        cursor.close()
                        conn.close()
                        self.main_window.sendstatusforvisualinspection(2)
                    else:
                        print("Failed to connect to the database.")
                if self.battery_id2:
                    conn = self.connect_db()
                    if conn:
                        cursor = conn.cursor()
                        # If the row does not exist, insert a new one
                        # If the row does not exist, insert a new one
                        query = """INSERT INTO [dbo].[Visual_Inspection_Station]
                                                           ([DateTime], [Shift], [ModuleBarcodeData], [Top_Bottom], [weld_burn_position], [weld_weak_position],[weld_miss_position] ,[weld_shift_position],[shifting_position], [Operator], [Status], [Recipe], [CycleTime])
                                                           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""
                        values = (
                            current_datetime, self.shift_num, self.battery_id2, self.topbottom, self.weld_burn_position,
                            self.weld_weak_position, self.weld_miss_position, self.weld_shift_position,
                            self.shifting_position,
                            self.inspectby, self.status, self.recipe, self.cycletime)

                        cursor.execute(query, values)
                        QMessageBox.information(self.main_window, "Success", "Data inserted successfully!")
                        conn.commit()
                        cursor.close()
                        conn.close()
                        self.main_window.sendstatusforvisualinspection(2)
                    else:
                        print("Failed to connect to the database.")
                self.updatevalues()
            except Exception as e:
                print(f"failed to connect to the database: {e}")
                QMessageBox.critical(self.main_window, "Error", f"Error inserting or updating data: {e}")
        else:
            QMessageBox.critical(self.main_window, "Log in Error", f"Please Log in Before accepting")


    def updatevalues(self):
        # update the values of  self.main_window.position_input_2.text(), self.topbottom and  self.defect
        self.main_window.position_input_2.setText("")
        self.main_window.position_input_3.setText("")
        self.main_window.position_input_6.setText("")
        self.main_window.position_input_5.setText("")
        self.main_window.position_input_7.setText("")
        self.main_window.topbottom_input_5.setCurrentIndex(0)