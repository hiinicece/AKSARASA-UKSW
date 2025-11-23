import json
from pathlib import Path
import qrcode
from qrcode.constants import ERROR_CORRECT_H
from PIL import Image

CODES_FILE = Path(__file__).parent / "museum_codes.json"
OUTPUT_DIR = Path(__file__).parent / "qr_codes"
QR_SIZE = 600          
LOGO_PERCENT = 0.22    

def load_codes():
    return json.loads(CODES_FILE.read_text(encoding="utf-8"))

def make_qr(code: str) -> Image.Image:
    qr = qrcode.QRCode(
        version=None,
        error_correction=ERROR_CORRECT_H,  
        box_size=10,
        border=4,
    )
    qr.add_data(code)
    qr.make(fit=True)
    img = qr.make_image(fill_color="#1a1a1a", back_color="white").convert("RGB")
    return img

def add_logo(qr_img: Image.Image) -> Image.Image:
    if not LOGO_PATH.exists():
        return qr_img
    logo = Image.open(LOGO_PATH).convert("RGBA")
    target_w = int(qr_img.width * LOGO_PERCENT)
    ratio = logo.height / logo.width
    logo = logo.resize((target_w, int(target_w * ratio)), Image.LANCZOS)

    x = (qr_img.width - logo.width) // 2
    y = (qr_img.height - logo.height) // 2

    qr_img = qr_img.copy()
    qr_img.paste(logo, (x, y), logo)
    return qr_img

def save_qr(img: Image.Image, code: str):
    OUTPUT_DIR.mkdir(exist_ok=True)
    img = img.resize((QR_SIZE, QR_SIZE), Image.NEAREST)
    out_path = OUTPUT_DIR / f"{code}.png"
    img.save(out_path)
    print(f"Saved {out_path}")

def main():
    codes = load_codes()
    for code in codes:
        base = make_qr(code)
        final = add_logo(base)
        save_qr(final, code)
    print("Done.")

if __name__ == "__main__":
    main()