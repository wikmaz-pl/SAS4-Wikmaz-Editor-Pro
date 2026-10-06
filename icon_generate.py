import os
import subprocess
import sys

print("=========================================")
print("   WIKMAZ ICON GENERATOR")
print("=========================================")

print("\n[1/2] Sprawdzanie biblioteki graficznej (Pillow)...")
try:
    from PIL import Image, ImageDraw
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "Pillow"])
    from PIL import Image, ImageDraw

def create_wikmaz_icon():
    print("[2/2] Rysowanie wektorowe i renderowanie pliku .ico...")
    
    # Płótno 256x256 z pełną przezroczystością (RGBA)
    size = (256, 256)
    img = Image.new('RGBA', size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Kolory
    dark_grey = (35, 35, 35, 255)
    toxic_green = (57, 255, 20, 255)

    # 1. Tło - Ciemne koło
    draw.ellipse((10, 10, 246, 246), fill=dark_grey)

    # 2. Obramowanie - Toksyczna zieleń
    draw.ellipse((10, 10, 246, 246), outline=toxic_green, width=12)

    # 3. Logo - Agresywne "W" (Wikmaz)
    # Koordynaty punktów: lewa góra -> lewy dół -> środek -> prawy dół -> prawa góra
    w_points = [
        (65, 80),   
        (95, 180),  
        (128, 120), 
        (161, 180), 
        (191, 80)   
    ]
    draw.line(w_points, fill=toxic_green, width=20, joint="curve")

    # Zapis do pliku .ico (generator z automatu robi wersje dla paska zadań, pulpitu itp.)
    img.save("icon.ico", format="ICO", sizes=[(256, 256), (128, 128), (64, 64), (32, 32)])
    
    print("\n=========================================")
    print("SUKCES! Wygenerowano plik 'icon.ico'.")
    print("Leży w Twoim folderze gotowy do użycia.")
    print("Możesz teraz odpalić polecenie: python zbuduj_exe.py")
    print("=========================================")

if __name__ == "__main__":
    create_wikmaz_icon()
    input("\nWciśnij Enter, aby zakończyć...")