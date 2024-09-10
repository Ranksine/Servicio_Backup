import pyodbc
import os
from dotenv import load_dotenv

load_dotenv()

def conex_db():
    # Establecer la conexión a la base de datos
    try:
        db_server = os.getenv('DB_SERVER')
        db_name = os.getenv('DB_NAME')
        db_user = os.getenv('DB_USER')
        db_password = os.getenv('DB_PASSWORD')
        backup_path = os.getenv('BACKUP_PATH')
        
        connectionString = (
            f"DRIVER={{ODBC Driver 17 for SQL Server}};"
            f"SERVER={db_server};"
            f"DATABASE={db_name};"
            f"UID={db_user};"
            f"PWD={db_password};"
        )
        conex = pyodbc.connect(connectionString)
        return conex
    except pyodbc.Error as e:
        print('Error al establecer la conexión: ', e)
        return None
    
    
    
if __name__ == "__main__":
    conn = conex_db()
    if conn:
        cursor = conn.cursor()
        # Ejecutar una consulta SQL (ejemplo)
        cursor.execute("SELECT TOP(5)* FROM EMPRESAS_FED")
        rows = cursor.fetchall()
        for row in rows:
            print(row)

        # Cerrar la conexión
        conn.close()
        