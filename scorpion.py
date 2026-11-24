import struct
import os
import zlib
import time
import sys
from PIL import Image
from PIL.ExifTags import TAGS
from datetime import datetime

def get_meta(path):
    image = Image.open(path)

    # Access and print basic image metadata
    print("Filename                 :", image.filename)
    print("Image Size               :", image.size)
    print("Image Height             :", image.height)
    print("Image Width              :", image.width)
    print("Image Format             :", image.format)
    print("Image Mode               :", image.mode)
    timestamp = os.path.getctime(path)
    print("File Creation Date       :", datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S"))

    # Check if the image is animated (for GIF images)
    if hasattr(image, "is_animated"):
        print("Image is Animated        :", image.is_animated)
        print("Frames in Image          :", image.n_frames)

    exif_data = image.getexif()
    if exif_data:
        for tag_id, data in exif_data.items():
            tag_name = TAGS.get(tag_id, tag_id)
            print(f"{tag_name:25}: {data}")
    else:
        print("No EXIF metadata found.")
    for key, value in image.info.items():
        if key != "exif":
            print(f"{key:25}: {value}")


def main():
    for i in range(len(sys.argv)):
        if i == 0:
            continue
        get_meta(sys.argv[i])

if __name__ == "__main__":
    main()

"""""
Previous attemp at thi project because i though that pil was forbidden and i was goiing byte by byte followint the specific format of the image extention.

METADATA_CHUNKS = {b'tEXt', b'zTXt', b'iTXt', b'eXIf', b'tIME', b'pHYs', b'iCCP'}

def parsepng(data: bytes) -> list:
    pos = 0
    metadata_list = []

    while pos < len(data):
        chunk_len, chunk_type = struct.unpack('>I4s', data[pos:pos+8])
        chunk_data = data[pos+8 : pos+8+chunk_len]

        if chunk_type in METADATA_CHUNKS:
            print(f"Found {chunk_type.decode()} at byte {pos + 33}, payload starts at {pos + 33 + 8}")
            item = {"chunk": chunk_type.decode('ascii')}

            if chunk_type == b'tEXt':
                keyword, text = chunk_data.split(b'\x00', 1)
                item.update({
                    "keyword": keyword.decode('latin-1'),
                    "text": text.decode('latin-1')
                })

            elif chunk_type == b'zTXt':
                keyword, rest = chunk_data.split(b'\x00', 1)
                comp_method = rest[0]
                text = zlib.decompress(rest[1:]).decode('latin-1')
                item.update({
                    "keyword": keyword.decode('latin-1'),
                    "compression_method": comp_method,
                    "text": text
                })

            elif chunk_type == b'iTXt':
                keyword, rest = chunk_data.split(b'\x00', 1)
                comp_flag = rest[0]
                comp_method = rest[1]
                lang_tag, trans_kw, raw_text = rest[2:].split(b'\x00', 2)
                
                if comp_flag == 1:
                    text = zlib.decompress(raw_text).decode('utf-8')
                else:
                    text = raw_text.decode('utf-8')
                    
                item.update({
                    "keyword": keyword.decode('latin-1'),
                    "compressed": bool(comp_flag),
                    "language": lang_tag.decode('ascii'),
                    "translated_keyword": trans_kw.decode('utf-8'),
                    "text": text
                })

            elif chunk_type == b'tIME':
                year, month, day, hour, minute, second = struct.unpack('>HBBBBB', chunk_data)
                item.update({
                    "datetime_utc": f"{year:04d}-{month:02d}-{day:02d} {hour:02d}:{minute:02d}:{second:02d}"
                })

            elif chunk_type == b'pHYs':
                ppu_x, ppu_y, unit = struct.unpack('>IIB', chunk_data)
                item.update({
                    "pixels_per_unit_x": ppu_x,
                    "pixels_per_unit_y": ppu_y,
                    "unit": "meters" if unit == 1 else "unknown (aspect ratio only)"
                })
                if unit == 1:
                    item["dpi_x"] = round(ppu_x * 0.0254)
                    item["dpi_y"] = round(ppu_y * 0.0254)

            elif chunk_type == b'iCCP':
                profile_name, rest = chunk_data.split(b'\x00', 1)
                comp_method = rest[0]
                icc_profile_bytes = zlib.decompress(rest[1:])
                item.update({
                    "profile_name": profile_name.decode('latin-1'),
                    "compression_method": comp_method,
                    "icc_data_size_bytes": len(icc_profile_bytes)
                })

            elif chunk_type == b'eXIf':
                endian = "Little-endian (Intel)" if chunk_data[:2] == b'II' else "Big-endian (Motorola)"
                item.update({
                    "format": f"TIFF/Exif ({endian})",
                    "raw_size_bytes": len(chunk_data),
                    "preview_hex": chunk_data[:16].hex()
                })

            metadata_list.append(item)
        if chunk_type == b'IEND':
            break
        pos += 12 + chunk_len
    return metadata_list

def get_file_metadata(filename):
    with open(filename, mode='rb') as file:
        data = file.read()

    if len(data) >= 3 and data[:3] == b"\xff\xd8\xff":
    elif len(data) >= 8 and data[:8] == b"\x89\x50\x4e\x47\x0d\x0a\x1a\x0a":
        parsepng(data[33:])
    elif len(data) >= 6 and (data[:6] == b"\x47\x49\x46\x38\x37\x61" or data[:8] == b"\x47\x49\x46\x38\x39\x61"):
    elif len(data) >= 2 and data[:2] == b"\x42\x4d":
    

if __name__ == '__main__':

"""
