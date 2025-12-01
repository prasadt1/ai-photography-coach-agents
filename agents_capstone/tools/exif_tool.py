from PIL import Image, ExifTags

EXIF_FIELDS = ["Model", "FNumber", "ISOSpeedRatings", "FocalLength", "ExposureTime"]

def extract_exif(image_path: str) -> dict:
    """
    Extract a small, coach‑relevant subset of EXIF metadata.
    Safe to run offline on JPEGs.
    """
    result: dict = {k: None for k in EXIF_FIELDS}
    try:
        img = Image.open(image_path)
        exif_raw = img._getexif() or {}
        name_map = {v: k for k, v in ExifTags.TAGS.items()}

        for field in EXIF_FIELDS:
            tag_id = name_map.get(field)
            if tag_id in exif_raw:
                value = exif_raw[tag_id]
                # Normalize some common fields
                if field in ("FNumber", "FocalLength") and isinstance(value, tuple) and len(value) == 2:
                    value = round(value[0] / value[1], 2)
                result[field] = value
    except Exception as e:
        result["error"] = str(e)
    return result
