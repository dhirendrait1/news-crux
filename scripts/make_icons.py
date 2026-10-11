from PIL import Image, ImageDraw, ImageFont
import os

os.makedirs("icons", exist_ok=True)

def generate_icon(size, path):
    # Create AMOLED dark background with rounded aesthetic
    img = Image.new("RGBA", (size, size), (5, 5, 8, 255))
    draw = ImageDraw.Draw(img)
    
    # Outer cyan border
    margin = int(size * 0.05)
    border_radius = int(size * 0.22)
    draw.rounded_rectangle(
        [margin, margin, size - margin, size - margin],
        radius=border_radius,
        outline=(0, 210, 255, 120),
        width=int(size * 0.02)
    )
    
    # Inner glowing core
    pad = int(size * 0.18)
    core_radius = int(size * 0.15)
    draw.rounded_rectangle(
        [pad, pad, size - pad, size - pad],
        radius=core_radius,
        fill=(0, 180, 240, 255)
    )
    
    # Center text NC
    font_size = int(size * 0.28)
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_size)
    except:
        font = ImageFont.load_default()
        
    draw.text((size / 2, size / 2), "NC", fill=(0, 0, 0, 255), anchor="mm", font=font)
    img.save(path, "PNG")
    print(f"Saved {path}")

generate_icon(192, "icons/icon-192.png")
generate_icon(512, "icons/icon-512.png")
