import os
import sys
from PIL import Image
from PIL.ExifTags import TAGS
from datetime import datetime

def short(v, n=60):
    s = v if isinstance(v, str) else repr(v)
    return s if len(s) <= n else s[:n] + ".."

def get_meta(path):
    try:
       with Image.open(path) as image:
            print("Filename                 :", image.filename)
            print("Image Size               :", image.size)
            print("Image Height             :", image.height)
            print("Image Width              :", image.width)
            print("Image Format             :", image.format)
            print("Image Mode               :", image.mode)
            timestamp = os.path.getctime(path)
            print("File Date                :", datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S"))

            if hasattr(image, "is_animated"):
                print("Image is Animated        :", image.is_animated)
                print("Frames in Image          :", image.n_frames)

            exif_data = image.getexif()
            if exif_data:
                for tag_id, data in exif_data.items():
                    tag_name = TAGS.get(tag_id, tag_id)
                    print(f"{tag_name:25}: {short(data)}")
                for tag_id, data in exif_data.get_ifd(0x8769).items():
                    print(f"{TAGS.get(tag_id, tag_id):25}: {short(data)}")
            else:
                print("No EXIF metadata found.")
            for key, value in image.info.items():
                if key != "exif":
                    print(f"{key:25}: {short(value)}")
    except (OSError, Image.UnidentifiedImageError) as e:
        print(f"{path}: cannot read ({e})")

def main():
    if len(sys.argv) < 2:
        print("Not enough arguments")
        sys.exit(1)
    print("---------------------------------------------------------------------------------------------------")
    for i in range(len(sys.argv)):
        if i == 0:
            continue
        get_meta(sys.argv[i])
        print("---------------------------------------------------------------------------------------------------")

if __name__ == "__main__":
    main()
