import hashlib
from pathlib import Path


class DocumentHashService:

    @staticmethod
    def calculate_file_hash(
        file_path: str | Path,
    ) -> str:

        hash_obj = hashlib.sha256()

        with open(file_path,"rb") as file:

            while chunk := file.read(4096):       # Read 4096 bytes at a time
                hash_obj.update(chunk)

        return hash_obj.hexdigest()