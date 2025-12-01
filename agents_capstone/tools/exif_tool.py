"""
EXIF Extraction Tool: Photography-focused metadata extraction.

Purpose:
- Extract camera settings from JPEG files (ISO, aperture, shutter speed, focal length)
- Provide VisionAgent with technical data for analysis
- Normalize EXIF values for consistent processing

Technology: PIL/Pillow library for image metadata reading
Note: Runs completely offline - no external API calls needed

Design Choice: Extract only photography-relevant fields to reduce noise
and focus coaching on actionable settings (exposure triangle, lens info).
"""

from PIL import Image, ExifTags

# Subset of EXIF fields relevant for photography coaching
# Full EXIF contains 100+ fields - we focus on the most important for learning
EXIF_FIELDS = ["Model", "FNumber", "ISOSpeedRatings", "FocalLength", "ExposureTime"]

def extract_exif(image_path: str) -> dict:
    """
    Extract a small, coach-relevant subset of EXIF metadata.
    Safe to run offline on JPEGs.
    
    Extraction Strategy:
    1. Open image with PIL
    2. Access raw EXIF data (tag IDs -> values)
    3. Map numeric tags to human-readable field names
    4. Normalize rational numbers (e.g., 28/1 -> 28.0 for focal length)
    5. Handle errors gracefully (corrupted EXIF, non-JPEG files)
    
    Args:
        image_path: Path to JPEG file
        
    Returns:
        Dict with Model, FNumber, ISOSpeedRatings, FocalLength, ExposureTime
        Returns None for missing fields, includes 'error' key if extraction fails
    """
    # Initialize result dict with all fields set to None (safe defaults)
    result: dict = {k: None for k in EXIF_FIELDS}
    try:
        # Step 1: Open image and extract raw EXIF data
        img = Image.open(image_path)
        exif_raw = img._getexif() or {}  # Returns None if no EXIF data
        
        # Step 2: Build reverse mapping from tag names to numeric IDs
        # EXIF stores data with numeric tags (e.g., 271 = Model)
        name_map = {v: k for k, v in ExifTags.TAGS.items()}

        # Step 3: Extract each field we care about
        for field in EXIF_FIELDS:
            tag_id = name_map.get(field)
            if tag_id in exif_raw:
                value = exif_raw[tag_id]
                
                # Step 4: Normalize rational numbers to floats
                # EXIF stores some values as fractions: (numerator, denominator)
                # Example: FNumber = (28, 10) -> f/2.8
                # Example: FocalLength = (50, 1) -> 50mm
                if field in ("FNumber", "FocalLength") and isinstance(value, tuple) and len(value) == 2:
                    value = round(value[0] / value[1], 2)
                result[field] = value
    except Exception as e:
        # Graceful error handling - return partial data with error flag
        # This prevents UI crashes when processing corrupted/non-JPEG files
        result["error"] = str(e)
    return result
