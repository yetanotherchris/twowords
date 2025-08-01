import os
import zipfile

class ZipUtils:
    @staticmethod
    def create_words_zip(words_txt_path, output_zip_path):
        """Create words.zip file containing the words.txt file as expanded_words.txt."""
        os.makedirs(os.path.dirname(output_zip_path), exist_ok=True)
        with zipfile.ZipFile(output_zip_path, "w", compression=zipfile.ZIP_DEFLATED) as z:
            # Save as expanded_words.txt inside the zip (matches old behavior)
            z.write(words_txt_path, arcname="expanded_words.txt")
        print(f"Created {output_zip_path} containing expanded_words.txt")
