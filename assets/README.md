# Placeholder for icon file
# This directory should contain:
# - icon.ico (Windows icon)
# - icon.icns (macOS icon, optional)
# 
# You can generate these from a PNG image using online tools or:
# - Windows: Use an online PNG to ICO converter
# - macOS: Use `sips` command or online PNG to ICNS converter
#
# Example PNG to ICO (using ImageMagick):
#   convert icon.png -define icon:auto-resize=256,128,64,48,32,16 icon.ico
#
# Example PNG to ICNS (macOS):
#   mkdir icon.iconset
#   sips -z 16 16 icon.png --out icon.iconset/icon_16x16.png
#   sips -z 32 32 icon.png --out icon.iconset/icon_16x16@2x.png
#   # ... (repeat for other sizes)
#   iconutil -c icns icon.iconset
