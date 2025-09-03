from PyQt5.QtWidgets import QDialog, QMessageBox
from PyQt5.uic import loadUi
from PyQt5.QtCore import QDateTime, QTimer
import pyodbc

connection_str = (
            "DRIVER={ODBC Driver 17 for SQL Server};"
            "SERVER=192.168.200.24,1433;"  # Update with your SQL Server name
            "DATABASE=ZONE02_REPORTS;"
            "UID=dbuserz02;"
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


def connect_db():
    try:
        conn = pyodbc.connect(connection_str)
        return conn
    except Exception as e:
        print(f"Database connection error: {e}")
        return None
print(connect_db())