@echo on
REM Cambiar al directorio donde está ubicado el entorno virtual
cd /d C:\Users\HAZEL\Desktop\Python\Servicio_Backup_SEISSP\

REM Activar el entorno virtual
call myvenv\Scripts\activate.bat

REM Ejecutar tu script Python
python C:\Users\HAZEL\Desktop\Python\Servicio_Backup_SEISSP\Hacer_Backup.py >> LogErrors.log 2>&1


