import os 
import time
import shutil
import logging
import datetime
from venv import logger
from dotenv import load_dotenv
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

load_dotenv()

# ------------------- VARIABLES GLOBALES -------------------

source_folder = os.getenv('SOURCE_FOLDER')
carpeta_destino = os.getenv('FINAL_PATH')
log_file = os.getenv('LOGFILE_NAME')

archivos_existentes = 0 
hora_alta_ini = datetime.time(8, 0)
hora_alta_fin = datetime.time(17, 0)


def esta_bloqueado(filepath):
    """Este metodo comprueba que el archivo no este siendo utilizado por ningun proceso
        
    Args:
        filepath (String): Ruta del archivo a verificar.
        
    Returns: 
        Boolean
    """
    try:
        with open(filepath, 'r+') as f:
            logger.info(f"El archivo se encuentra disponible")
            return False
    except IOError: # El entrar en la excepcion queire decir que la función open no pudo acceder al archivo, lo que implica que esta bloqueado por otro proceso.
        logger.info(f"El archivo esta siendo utilizado por otro proceso")
        return True
 

def revisar_existencia_archivos(carpeta_origen, carpeta_destino):
    """ Este método monitorea constantemente la creación del respaldo en la carpeta de origen, cuando se crea, procede a moverlo a la carpeta destino
        
    Args:
        carpeta_origen (String): Carpeta donde se encuentra el archivo original.
        carpeta_destino (String): Carta hacia donde se movera el archivo.
    """
    global hora_alta_ini, hora_alta_fin
    ahorita = datetime.datetime.now()
    hora_actual = ahorita.time()
    
    # tiempo_espera = 5 if (hora_alta_ini <= hora_actual <= hora_alta_fin) else 3  #  Tiempo de espera para pruebas.
    tiempo_espera = 7200 if (hora_alta_ini <= hora_actual <= hora_alta_fin) else 3600.
    
    while True:
        for filename in os.listdir(carpeta_origen): # Recorrer todos los archivos de la carpeta origen.
            if filename.endswith('.bak'): # Busqueda de archivos .bak
                file_path=os.path.join(carpeta_origen, filename) # Creación de la ruta completa del archivo .bak.
                logger.info(f'Se encontró el archivo {filename}.')
                if not esta_bloqueado(file_path):
                    mover_archivo(file_path, carpeta_destino) # Si todo fue correcto, procede a mover el archivo encontrado.
            else:
                logger.info(f'Esperando por la existencia del archivo de respaldo...')
        time.sleep(tiempo_espera) # En segundos. # Delay antes de repetir el ciclo (infinito).
  
  
def buscar_archivo_destino(carpeta_destino, nombre_archivo):
    """Este método busca por archivos que tengan el mismo nombre que el archivo de respaldo en la carpeta origen. En caso de que existan archivos con el mismo nombre, incrementa el contador segun la cantidad de estos archivos
        
    Args:
        carpeta_origen (String): Carpeta donde se encuentra el archivo original.
        carpeta_destino (String): Carta hacia donde se movera el archivo.
    """
    print('-- Entrando a buscar archivos con el mismo nombre')
    global archivos_existentes
    for filename in os.listdir(carpeta_destino):
        nombre = filename[0:len(filename)-4]
        
        # Limpiar el nombre de archivos que ya fueron procesados pero tienen el mismo nombre.
        if nombre[len(nombre)-2 : len(nombre)-1] == '_':
            clean_nombre = nombre[:len(nombre)-2]
        else:
            clean_nombre = nombre
            
        # Incrementar contador.
        if clean_nombre == nombre_archivo:
            archivos_existentes += 1
            print(f'Archivos existentes: {archivos_existentes}')
  
def mover_archivo(source, destino):
    """Mover el backup de la carpeta compartida a su ubicacion final en el disco duro. 
    
    Args:
        source (String): Nombre el archivo en la carpeta origen.
        destino (String): Ruta a donde se movera el archivo.
    
    """
    
    try:
        print(f'Nombre del archivo a mover: {source}')
        logger.info(f'Iniciando el proceso de transferencia de {source}')
        
        # En el caso idoneo se mueve el archivo, solo existe un archivo con este nombre, el flujo es directo.
        shutil.move(source, destino)
        
        # Puede que no sea necesario limpiar la variable en este punto, pero mas vale.
        global archivos_existentes
        archivos_existentes = 0
        
        logger.info(f"Se completo la transferencia de {source} hacia: {destino}.")
        print(f'Se completo la transferencia de {source} hacia: {destino}.')
        eliminar_respaldo_viejo(destino)
    except shutil.Error as e: # Atrapar cualquier error de la libreria shutil.
        if "already exists" in str(e): # Cuando ya existe un archivo con el mismo nombre en carpeta destino, se debe renombrar el archivo a mover.
            logger.error(f'Ya existe un archivo con el nombre {source}, se renombrará para poder hacer la transferencia.')
            print(f'{e}, hora de cambiar el nombre')
            
            buscar_archivo_destino(destino, source[3:len(source)-4]) # Generar la cantidad de archivos con el mismo nomrbe.
            nuevo_nombre = cambiar_nombre_archivo(source) # Renombrar el archivo con el formato <nombre_original>_<numero_consecutivo>.bak
            nuevo_destino = os.path.join(destino, nuevo_nombre) # Recontruir la ruta destino
            
            shutil.move(source, nuevo_destino) # Reintentar mover archivo
            archivos_existentes = 0 # Limpiar variable global para el siguiente archivo.
            print(f'Se completo la transferencia de {source} hacia: {destino} despues del error.')
            eliminar_respaldo_viejo(destino)
            return
        else: # Atrapar cualquier otra excepcion de la librería shutil
            logger.error(f'Ocurrió un error al intentar mover el archivo {source}: {e}... Reintentando')
            print(f'Ocurrió un error al intentar mover el archivo {source}: {e}... Reintentando')
            return
        
         
def eliminar_respaldo_viejo(directorio):
    """Método para eliminar el archivo de respaldo más antiguo cuando existan mas de cinco (5) archivos de respaldo en la carpeta destino.

    Args:
        directorio (String): Carpeta en donde se encuentran los archivos de respaldo.
    """
    archivos_list = os.listdir(directorio)
    
    archivos_list.sort(key=lambda f: os.stat(os.path.join(directorio,f)).st_mtime)
    
    if len(archivos_list) >= 5 :
        most_old_archivo = os.path.join(directorio, archivos_list[0])
        print(f'El archivo mas antiguo es: {most_old_archivo}')
        os.remove(most_old_archivo)
        print('Ya se elimino el archivo mi valedor')
        
       
            
def cambiar_nombre_archivo(source):
    """Método para renombrar el archivo destino cuando ya existe un archivo con el mismo nombre, se renombra bajo el formato: [nombre_original] + '_' + [numero_consecutivo] + '.bak'.

    Args:
        source (String): Nombre el archivo en la carpeta origen.
        
    Returns: 
        String
    """
    print('--- Entrando a cambiar el nombre')
    global archivos_existentes
    if archivos_existentes > 0:
        if source[len(source)-6:len(source)-5] == '_' :
            nuevo_name = source[0:len(source)-6] + '_' + str(archivos_existentes) + '.bak'
        else:
            nuevo_name = source[0:len(source)-4] + '_' + str(archivos_existentes) + '.bak'
    else: 
        nuevo_name = source
    
    print(f'Nuevo nombresini: {nuevo_name}')
    return nuevo_name
        
class FileEventHandler(FileSystemEventHandler):
    logger.info(f'Entrando al FileEventHandler...')
    def on_created(self, event):
        if event.is_directory:
            return None
        
        if event.src_path.endswith('.bak'):
            if not esta_bloqueado(event.src_path):
                mover_archivo(event.src_path, carpeta_destino)
     

logging.basicConfig(filename=log_file, level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
logger = logging.getLogger(__name__)                

event_handler = FileEventHandler()
observer = Observer()
observer.schedule(event_handler, source_folder, recursive=False)

observer.start()

try:
    revisar_existencia_archivos(source_folder, carpeta_destino)
except KeyboardInterrupt:
    observer.stop()
observer.join()