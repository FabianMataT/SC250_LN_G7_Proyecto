import uuid
from werkzeug.utils import secure_filename

class FileManager:
    UPLOAD_SESSION_KEY = 'uploaded_files'

    @staticmethod
    def init_session(session):
        if FileManager.UPLOAD_SESSION_KEY not in session:
            session[FileManager.UPLOAD_SESSION_KEY] = []

    @staticmethod
    def add_file(session, file):
        file_id = str(uuid.uuid4())
        file_info = {
            'id': file_id,
            'name': secure_filename(file.filename),
        }
        files = session[FileManager.UPLOAD_SESSION_KEY]
        files.append(file_info)
        session[FileManager.UPLOAD_SESSION_KEY] = files

    @staticmethod
    def get_files(session):
        return session.get(FileManager.UPLOAD_SESSION_KEY, [])

    @staticmethod
    def delete_file(session, file_id):
        files = session.get(FileManager.UPLOAD_SESSION_KEY, [])
        session[FileManager.UPLOAD_SESSION_KEY] = [f for f in files if f['id'] != file_id]
