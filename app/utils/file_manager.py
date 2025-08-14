import uuid
from werkzeug.utils import secure_filename
import pandas as pd
import os

UPLOAD_FOLDER = "uploads"

class FileManager:
    UPLOAD_SESSION_KEY = 'uploaded_files'

    @staticmethod
    def init_session(session):
        if FileManager.UPLOAD_SESSION_KEY not in session:
            session[FileManager.UPLOAD_SESSION_KEY] = []

    @staticmethod
    def add_file(session, file):
        if not os.path.exists(UPLOAD_FOLDER):
            os.makedirs(UPLOAD_FOLDER)

        file_id = str(uuid.uuid4())
        filename = secure_filename(file.filename)
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)

        analisis = FileManager.process_file(filepath)

        file_info = {
            'id': file_id,
            'name': filename,
            'path': filepath,
            'analisis': analisis  # guardamos el análisis
        }

        files = session[FileManager.UPLOAD_SESSION_KEY]
        files.append(file_info)
        session[FileManager.UPLOAD_SESSION_KEY] = files

        return analisis


    @staticmethod
    def process_file(filepath):
        if filepath.endswith(".csv"):
            df = pd.read_csv(filepath)
        elif filepath.endswith((".xls", ".xlsx")):
            df = pd.read_excel(filepath)
        else:
            return {"error": "Formato no soportado"}

        df.columns = [c.strip() for c in df.columns]
        df = df.drop_duplicates()
        df = df.dropna(how="all")

        tipos = df.dtypes.astype(str).to_dict()
        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()

        analisis = {
            "shape": df.shape,
            "columnas": list(df.columns),
            "tipos": tipos,
            "nulos": df.isnull().sum().to_dict(),
            "estadisticas": df.describe(include="all").fillna("").to_dict(),
            "numeric_columns": numeric_cols
        }
        
        return analisis


    @staticmethod
    def get_files(session):
        return session.get(FileManager.UPLOAD_SESSION_KEY, [])

    @staticmethod
    def delete_file(session, file_id):
        files = session.get(FileManager.UPLOAD_SESSION_KEY, [])
        for f in files:
            if f['id'] == file_id:
                if os.path.exists(f['path']):
                    os.remove(f['path'])  # Eliminar del disco también
        session[FileManager.UPLOAD_SESSION_KEY] = [f for f in files if f['id'] != file_id]
