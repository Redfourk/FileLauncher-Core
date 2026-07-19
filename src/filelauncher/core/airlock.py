import os
import uuid
import logging

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

class AirlockPipeline:
    def __init__(self, staging_dir="staging", storage_dir="storage"):
        self.staging_dir = staging_dir
        self.storage_dir = storage_dir

        os.makedirs(self.staging_dir, exist_ok=True)
        os.makedirs(self.storage_dir, exist_ok=True)
    def process_incoming_file(self, filename: str, file_data: bytes) -> dict:
        logging.info(f"Airlock activated for incoming file: {filename}")

        safe_filename = f"{uuid.uuid4().hex[:8]}_{filename}"
        staged_path = os.path.join(self.staging_dir, safe_filename)

        with open(staged_path, "wb") as f:
            f.write(file_data)
        logging.debug(f"File staged at: {staged_path}")

        if not self._validate_file(staged_path):
            os.remove(staged_path)
            logging.warning(f"File {filename} failed validation and was destroyed.")
            return {"status": "rejected", "reason": "Validation failed"}

        final_path = os.path.join(self.storage_dir, safe_filename)
        os.rename(staged_path, final_path)
        logging.info(f"File {filename} successfully promoted to permanent storage.")

        return {"status": "success", "file_id": safe_filename}

    def _validate_file(self, filepath: str) -> bool:
        """ Example validation rules. """
        max_size = 5 * 1024 * 1024
        if os.path.getsize(filepath) > max_size:
            logging.error("Validation Error: File Exceeds 5MB limit.")
            return False
        if not filepath.lower().endswith(('.txt', '.png', '.jpg', '.zip', '.json')):
            logging.error("Validation Error: Unauthorized file type.")
            return False

        return True