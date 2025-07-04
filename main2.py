import gpxpy
import os
from datetime import datetime, timedelta
from exif import Image as ExifImage

def parse_gpx(gpx_file):
    with open(gpx_file, 'r') as f:
        gpx = gpxpy.parse(f)
    points = []
    for track in gpx.tracks:
        for segment in track.segments:
            for point in segment.points:
                points.append({
                    'time': point.time.replace(tzinfo=None),
                    'lat': point.latitude,
                    'lon': point.longitude
                })
    return points

def get_photo_time(photo_path):
    with open(photo_path, 'rb') as img_file:
        img = ExifImage(img_file)
        if not img.has_exif:
            raise Exception(f"No EXIF data in {photo_path}")
        dt_str = img.datetime_original
        return datetime.strptime(dt_str, '%Y:%m:%d %H:%M:%S')

def find_nearest_gpx_point(photo_time, gpx_points):
    return min(gpx_points, key=lambda p: abs(p['time'] - photo_time))

def set_gps_to_photo(photo_path, lat, lon):
    def dec_to_dms(dec):
        d = int(dec)
        m = int((abs(dec) - abs(d)) * 60)
        s = (abs(dec) - abs(d) - m/60) * 3600
        return (abs(d), m, s)
    with open(photo_path, 'rb') as img_file:
        img = ExifImage(img_file)
    img.gps_latitude = dec_to_dms(lat)
    img.gps_latitude_ref = 'N' if lat >= 0 else 'S'
    img.gps_longitude = dec_to_dms(lon)
    img.gps_longitude_ref = 'E' if lon >= 0 else 'W'
    with open(photo_path, 'wb') as img_file:
        img_file.write(img.get_file())

# Основной цикл
gpx_points = parse_gpx('gpx_track.gpx')
photos_dir = 'Photo'
for filename in os.listdir(photos_dir):
    if filename.lower().endswith('.jpg'):
        photo_path = os.path.join(photos_dir, filename)
        photo_time = get_photo_time(photo_path)
        nearest = find_nearest_gpx_point(photo_time, gpx_points)
        set_gps_to_photo(photo_path, nearest['lat'], nearest['lon'])
        print(f"{filename}: {nearest['lat']}, {nearest['lon']}")