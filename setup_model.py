"""
Скрипт для автоматической распаковки модели CatBoost.
Проверяет наличие несжатого файла модели и распаковывает его при необходимости.
"""

import os
import gzip
import shutil

MODEL_COMPRESSED = "dc_characters_best.cbm.gz"
MODEL_UNCOMPRESSED = "dc_characters_best.cbm"

def setup_model():
    """Распаковывает модель, если она еще не распакована."""
    
    # Проверяем, существует ли уже распакованная модель
    if os.path.exists(MODEL_UNCOMPRESSED):
        print(f"✅ Модель {MODEL_UNCOMPRESSED} уже распакована.")
        return
    
    # Проверяем, существует ли сжатая модель
    if not os.path.exists(MODEL_COMPRESSED):
        print(f"❌ Ошибка: Файл {MODEL_COMPRESSED} не найден!")
        print("Убедитесь, что вы клонировали репозиторий полностью.")
        return
    
    print(f"📦 Распаковка модели {MODEL_COMPRESSED}...")
    
    try:
        # Распаковываем модель
        with gzip.open(MODEL_COMPRESSED, 'rb') as f_in:
            with open(MODEL_UNCOMPRESSED, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
        
        print(f"✅ Модель успешно распакована в {MODEL_UNCOMPRESSED}")
        
        # Показываем размеры файлов
        compressed_size = os.path.getsize(MODEL_COMPRESSED) / (1024 * 1024)
        uncompressed_size = os.path.getsize(MODEL_UNCOMPRESSED) / (1024 * 1024)
        
        print(f"📊 Размер сжатого файла: {compressed_size:.1f} MB")
        print(f"📊 Размер распакованного файла: {uncompressed_size:.1f} MB")
        
    except Exception as e:
        print(f"❌ Ошибка при распаковке: {e}")

if __name__ == "__main__":
    setup_model() 