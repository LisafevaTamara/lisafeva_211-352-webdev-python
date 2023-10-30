import hashlib
import uuid
import os
from werkzeug.utils import secure_filename
from models import *
from app import db, app

class CoverSave:
    def __init__(self, file):
        self.file = file

    def save(self):
        self.cov = self.__find_by_md5_hash()
        if self.cov is not None:
            return self.cov
        file_name = secure_filename(self.file.filename)
        self.cov = Сovers(
            id = str(uuid.uuid4()),
            file_name = file_name,
            mime_type = self.file.mimetype,
            md5_hash = self.md5_hash)
        self.file.save(
            os.path.join(app.config['UPLOAD_FOLDER'],
                         self.cov.storage_filename))
        db.session.add(self.cov)
        db.session.commit()
        return self.cov

    def __find_by_md5_hash(self):
        self.md5_hash = hashlib.md5(self.file.read()).hexdigest()
        self.file.seek(0)
        return db.session.execute(db.select(Сovers).filter(Сovers.md5_hash == self.md5_hash)).scalar()
    
def cover_delete(storage_filename):
    os.remove(os.path.join(app.config['UPLOAD_FOLDER'], storage_filename))