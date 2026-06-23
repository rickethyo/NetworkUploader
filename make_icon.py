from PIL import Image, ImageChops
from pathlib import Path

source_image = Path(r"C:\Users\ricke\Downloads\ChatGPT Image May 28, 2026, 09_25_39 PM.png")
output_icon = Path(r"C:\Users\ricke\OneDrive\Desktop\PyUploader\assets\network_uploader.ico")

output_icon.parent.mkdir(parents=True, exist_ok=True)

image = Image.open(source_image).convert("RGBA")

# Crop away white/empty border
background = Image.new("RGBA", image.size, image.getpixel((0, 0)))
difference = ImageChops.difference(image, background)
bbox = difference.getbbox()

if bbox:
    image = image.crop(bbox)

# Create a square canvas with controlled padding
icon_size = 1024
padding = 20

image.thumbnail((icon_size - padding * 2, icon_size - padding * 2), Image.LANCZOS)

canvas = Image.new("RGBA", (icon_size, icon_size), (0, 0, 0, 0))

x = (icon_size - image.width) // 2
y = (icon_size - image.height) // 2

canvas.paste(image, (x, y), image)

canvas.save(
    output_icon,
    format="ICO",
    sizes=[
        (16, 16),
        (24, 24),
        (32, 32),
        (48, 48),
        (64, 64),
        (128, 128),
        (256, 256)
    ]
)

print("Icon created:", output_icon)