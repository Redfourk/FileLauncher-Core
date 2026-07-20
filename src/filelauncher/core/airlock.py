import os
import uuid
import logging
from models.database import ManifestDB

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

class AirlockPipeline:
    def __init__(self, staging_dir="staging", storage_dir="storage"):
        self.staging_dir = staging_dir
        self.storage_dir = storage_dir
        self.db = ManifestDB()

        os.makedirs(self.staging_dir, exist_ok=True)
        os.makedirs(self.storage_dir, exist_ok=True)
    def process_incoming_file(self, filename: str, file_data: bytes) -> dict:
        logging.info(f"Airlock activated for incoming file: {filename}")

        safe_filename = f"{uuid.uuid4().hex[:8]}_{filename}"
        staged_path = os.path.join(self.staging_dir, safe_filename)

        with open(staged_path, "wb") as f:
            f.write(file_data)
        logging.debug(f"File staged at: {staged_path}")

        is_valid, reason = self._validate_file(staged_path)
        if not is_valid:
            os.remove(staged_path)
            logging.warning(f"File {filename} failed validation: {reason}")
            return {"status": "failure", "reason": reason}

        final_path = os.path.join(self.storage_dir, safe_filename)
        os.rename(staged_path, final_path)
        self.db.add_file(safe_filename, filename)
        logging.info(f"File {filename} successfully promoted to permanent storage.")

        return {"status": "success", "file_id": safe_filename}

    def _validate_file(self, filepath: str) -> (bool, str):
        """ Example validation rules. """
        if os.path.getsize(filepath) > (5 * 1024 * 1024):
            return False, "File too large (>5MB)"
        if not filepath.lower().endswith(('.txt', '.png', '.jpg', '.zip', '.json')):
            return False, "Unauthorized file extension"
        return True, "Success"