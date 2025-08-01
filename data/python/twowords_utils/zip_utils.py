import os
import zipfile

class ZipUtils:
    @staticmethod
    def create_words_zip(words_txt_path, output_zip_path):
        os.makedirs(os.path.dirname(output_zip_path), exist_ok=True)
        with zipfile.ZipFile(output_zip_path, "w", compression=zipfile.ZIP_DEFLATED) as z:
            z.write(words_txt_path, arcname="words.txt")
