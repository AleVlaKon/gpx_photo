from exif import Image as ExifImage

# with open('photo_gps_2.jpg', 'rb') as img_file:
#     img = ExifImage(img_file)
#     print(img.gps_latitude)
#     print(img.gps_longitude)
#     print(img.gps_latitude_ref)
#     print(img.gps_longitude_ref)
#     img.gps_latitude = (55, 51, 37.0)
#     img.gps_latitude_ref = "N"
#     img.gps_longitude = (37, 39, 3.0)
#     img.gps_longitude_ref = "E"
# with open('photo_gps_2.jpg', 'wb') as img_file:    
#     img_file.write(img.get_file())


# with open('photo_gps.jpg', 'rb') as img_file:
#     img = ExifImage(img_file)
#     all_exif = img.get_all()
#     for key, value in all_exif.items():
#         print(f"{key}: {value}")


# with open('photo_gps_2.jpg', 'rb') as img_file:
#     img = ExifImage(img_file)
#     all_exif = img.get_all()
#     for key, value in all_exif.items():
#         print(f"{key}: {value}")


with open('photo_gps.jpg', 'rb') as f1, open('photo_gps_2.jpg', 'rb') as f2:
    img_1 = ExifImage(f1)
    img_2 = ExifImage(f2)
    all_exif_1 = img_1.get_all()
    all_exif_2 = img_2.get_all()
    for key in all_exif_1.keys():
        if isinstance(key, str) and key.startswith('gps_'):
            print(f'{key}: {all_exif_1[key]} -> {all_exif_2[key]}')
