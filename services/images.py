"""
Image layer: turns uploaded car photos into the `damages` dict used for pricing.

1. Load each photo: must be a real JPEG/PNG/WebP, fixed for phone rotation, shrunk to save tokens.
2. Number check (one vision call per photo, in parallel): the registration number must be clearly
   readable on the plate or on a piece of paper. Photos without one are discarded.
3. The car's number is taken from the number plate itself (a number on paper can't set it).
   Every other photo, plate or paper, must show that same number or it is discarded.
   If no photo shows the plate, no photo is accepted.
4. Damage detection (one vision call with all kept photos): returns part -> severity.
"""
import base64
import io
import re
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from PIL import Image, ImageOps, UnidentifiedImageError

from llm.images import check_number, detect_damages

MAX_IMAGES = 12
MAX_FILE_BYTES = 15 * 1024 * 1024
MAX_SIDE_PX = 1568  # larger photos cost more tokens without helping the model
ALLOWED_FORMATS = {"JPEG", "PNG", "WEBP"}
MIN_CONFIDENCE = 0.5  # damages the model is less sure about are reported but not priced

# Indian registration numbers: state + RTO + series + number (DL3CAB1234), and BH series (22BH1234AB)
REGISTRATION_PATTERNS = (
    re.compile(r"^[A-Z]{2}\d{1,2}[A-Z]{0,3}\d{1,4}$"),
    re.compile(r"^\d{2}BH\d{4}[A-Z]{1,2}$"),
)


def process_images(images: list) -> dict:
    """images: file paths, or (name, bytes) pairs for uploads."""
    if not images:
        raise ValueError("no images uploaded")
    if len(images) > MAX_IMAGES:
        raise ValueError(f"upload at most {MAX_IMAGES} images")

    rejected, loaded = [], []
    for item in images:
        name, data = item if isinstance(item, tuple) else (str(item), None)
        try:
            loaded.append((name, _load(data if data is not None else Path(item))))
        except ValueError as e:
            rejected.append({"image": name, "reason": str(e)})

    # Stage 1: every photo must show a readable registration number
    with ThreadPoolExecutor(max_workers=4) as pool:
        checks = list(pool.map(lambda item: check_number(item[1]), loaded))

    with_number = []
    for (path, data_url), check in zip(loaded, checks):
        number = normalise_number(check.registration_number)
        if not check.number_visible or check.shown_on == "none" or number is None:
            rejected.append({"image": path, "reason": f"no clearly visible registration number ({check.reason})"})
        else:
            with_number.append((path, data_url, number, check.shown_on))

    if not with_number:
        return {"registration_number": None, "accepted": [], "rejected": rejected, "damages": {}, "findings": []}

    # Stage 2: the car's number comes from the number plate; everything else must match it
    plate_numbers = Counter(n for _, _, n, shown_on in with_number if shown_on == "number_plate")
    if not plate_numbers:
        for path, _, number, _ in with_number:
            rejected.append({"image": path, "reason": f"number {number} is only on paper; "
                                                      "at least one photo must show the number plate"})
        return {"registration_number": None, "accepted": [], "rejected": rejected, "damages": {}, "findings": []}
    registration_number, _ = plate_numbers.most_common(1)[0]
    accepted = []
    for path, data_url, number, shown_on in with_number:
        if number == registration_number:
            accepted.append({"image": path, "data_url": data_url, "shown_on": shown_on})
        else:
            rejected.append({"image": path, "reason": f"shows {number}, but the number plate reads {registration_number}"})

    # Stage 3: damage detection on the accepted photos only
    report = detect_damages([a["data_url"] for a in accepted])
    damages, findings = {}, []
    for d in report.damages:
        priced = d.confidence >= MIN_CONFIDENCE
        findings.append({
            "part": d.part,
            "severity": d.severity,
            "description": d.description,
            "images": [accepted[i - 1]["image"] for i in d.image_numbers if 1 <= i <= len(accepted)],
            "confidence": d.confidence,
            "priced": priced,
        })
        if priced and d.severity > damages.get(d.part, ""):  # keep the worst severity per part
            damages[d.part] = d.severity

    return {
        "registration_number": registration_number,
        "accepted": [{"image": a["image"], "shown_on": a["shown_on"]} for a in accepted],
        "rejected": rejected,
        "damages": damages,
        "findings": findings,
        "unclear_areas": report.unclear_areas,
    }


def normalise_number(raw: str | None) -> str | None:
    """'dl 3c ab-1234' -> 'DL3CAB1234'. Returns None if it doesn't look like an Indian registration."""
    if not raw:
        return None
    number = re.sub(r"[^A-Z0-9]", "", raw.upper())
    return number if any(p.match(number) for p in REGISTRATION_PATTERNS) else None


def _load(source: Path | bytes) -> str:
    """Validate, rotate and shrink one photo (a path or raw bytes); returns a base64 JPEG data URL."""
    if isinstance(source, Path):
        if not source.is_file():
            raise ValueError("file not found")
        source = source.read_bytes()
    if len(source) > MAX_FILE_BYTES:
        raise ValueError(f"file larger than {MAX_FILE_BYTES // (1024 * 1024)} MB")
    try:
        with Image.open(io.BytesIO(source)) as image:
            if image.format not in ALLOWED_FORMATS:
                raise ValueError(f"unsupported format {image.format}; use JPEG, PNG or WebP")
            image = ImageOps.exif_transpose(image).convert("RGB")  # phone photos are often stored rotated
            image.thumbnail((MAX_SIDE_PX, MAX_SIDE_PX))
            buffer = io.BytesIO()
            image.save(buffer, format="JPEG", quality=85)  # re-encoding also drops EXIF (GPS etc.)
    except UnidentifiedImageError:
        raise ValueError("not a valid image file")
    return "data:image/jpeg;base64," + base64.b64encode(buffer.getvalue()).decode()
