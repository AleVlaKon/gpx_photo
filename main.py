import os
import sys
from datetime import datetime, timedelta
from xml.etree import ElementTree as ET
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS

def get_exif_datetime(image_path):
    """Извлекает дату и время из EXIF-данных фотографии"""
    try:
        img = Image.open(image_path)
        exif = img._getexif()
        if exif is None:
            return None
            
        for tag, value in exif.items():
            if TAGS.get(tag) == 'DateTimeOriginal':
                return datetime.strptime(value, '%Y:%m:%d %H:%M:%S')
    except Exception as e:
        print(f"Ошибка при чтении EXIF: {e}")
    return None

def parse_gpx(gpx_file):
    """Парсит GPX-файл и возвращает список точек с временем, широтой и долготой"""
    points = []
    try:
        tree = ET.parse(gpx_file)
        root = tree.getroot()
        
        # Namespace может отличаться в разных GPX-файлах
        ns = {'gpx': 'http://www.topografix.com/GPX/1/1'}
        
        for trkpt in root.findall('.//gpx:trkpt', ns):
            lat = float(trkpt.attrib['lat'])
            lon = float(trkpt.attrib['lon'])
            time_str = trkpt.find('gpx:time', ns).text
            # Удаляем Z в конце, если есть (UTC время)
            time_str = time_str.replace('Z', '') if 'Z' in time_str else time_str
            time = datetime.fromisoformat(time_str)
            points.append({'time': time, 'lat': lat, 'lon': lon})
    except Exception as e:
        print(f"Ошибка при парсинге GPX: {e}")
    return points

def find_nearest_point(photo_time, gpx_points):
    """Находит ближайшую по времени точку в GPX-треке"""
    if not gpx_points:
        return None
    
    # Ищем точку с минимальной разницей во времени
    nearest = min(gpx_points, key=lambda x: abs(x['time'] - photo_time))
    return nearest

def write_gps_to_image(image_path, lat, lon):
    """Записывает GPS-координаты в EXIF фотографии"""
    try:
        img = Image.open(image_path)
        exif = img.info.get('exif', {})
        
        # Конвертируем EXIF в словарь, если это не словарь
        if isinstance(exif, bytes):
            exif_dict = {}
        else:
            exif_dict = exif
            
        # Преобразуем координаты в формат EXIF
        lat_ref = 'N' if lat >= 0 else 'S'
        lon_ref = 'E' if lon >= 0 else 'W'
        lat = abs(lat)
        lon = abs(lon)
        
        # Координаты в градусах, минутах, секундах
        lat_deg = int(lat)
        lat_min = int((lat - lat_deg) * 60)
        lat_sec = (lat - lat_deg - lat_min/60) * 3600
        
        lon_deg = int(lon)
        lon_min = int((lon - lon_deg) * 60)
        lon_sec = (lon - lon_deg - lon_min/60) * 3600
        
        # Создаем EXIF GPS теги
        gps_ifd = {
            GPSTAGS.GPSLatitudeRef: lat_ref,
            GPSTAGS.GPSLatitude: [(lat_deg, 1), (lat_min, 1), (int(lat_sec*100), 100)],
            GPSTAGS.GPSLongitudeRef: lon_ref,
            GPSTAGS.GPSLongitude: [(lon_deg, 1), (lon_min, 1), (int(lon_sec*100), 100)],
        }
        
        # Обновляем EXIF данные
        exif_dict[0x8825] = gps_ifd  # 0x8825 - GPSInfo tag
        
        # Сохраняем изображение с новыми EXIF данными
        img.save(image_path, exif=exif_dict)
        print(f"GPS координаты записаны в {image_path}")
    except Exception as e:
        print(f"Ошибка при записи GPS в EXIF: {e}")

def main():
    if len(sys.argv) < 3:
        print("Использование: python geotag_photos.py <путь_к_gpx> <путь_к_фото>")
        return
    
    gpx_file = sys.argv[1]
    photo_path = sys.argv[2]
    
    # Проверяем, является ли photo_path файлом или директорией
    if os.path.isfile(photo_path):
        photos = [photo_path]
    elif os.path.isdir(photo_path):
        photos = [os.path.join(photo_path, f) for f in os.listdir(photo_path) 
                 if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
    else:
        print("Указанный путь к фото не существует")
        return
    
    # Парсим GPX
    gpx_points = parse_gpx(gpx_file)
    if not gpx_points:
        print("Не удалось прочитать точки из GPX-файла")
        return
    
    # Обрабатываем каждое фото
    for photo in photos:
        photo_time = get_exif_datetime(photo)
        if not photo_time:
            print(f"Не удалось получить дату и время из {photo}")
            continue
        
        nearest_point = find_nearest_point(photo_time, gpx_points)
        if nearest_point:
            print(f"Фото: {photo}, Время: {photo_time}")
            print(f"Ближайшая точка: {nearest_point['time']}, Lat: {nearest_point['lat']}, Lon: {nearest_point['lon']}")
            write_gps_to_image(photo, nearest_point['lat'], nearest_point['lon'])
        else:
            print(f"Не найдена подходящая точка в GPX для {photo}")

if __name__ == "__main__":
    main()