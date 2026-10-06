import os
import subprocess
import sys

def build():
    print("=========================================")
    print("   SAS4 WIKMAZ EDITOR - EXE BUILDER")
    print("=========================================")
    
    # 1. Sprawdzenie PyInstallera
    print("\n[1/3] Sprawdzanie biblioteki PyInstaller...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
    
    # 2. Przygotowanie polecenia
    print("\n[2/3] Konfiguracja i sprawdzanie ikony...")
    cmd = [
        "pyinstaller",
        "--noconfirm",
        "--onefile",
        "--windowed",  # Ukrywa czarną konsolę
        "--name", "SAS4_Wikmaz_Editor_Pro",
        "--add-data", "kucingoren;kucingoren" # Silnik gry
    ]
    
    # --- NOWOŚĆ: Obsługa ikony ---
    icon_filename = "icon.ico"
    if os.path.exists(icon_filename):
        print(f"[*] Znaleziono plik '{icon_filename}'! Zostanie wgrany do pliku EXE.")
        cmd.extend(["--icon", icon_filename])
    else:
        print("[!] Nie znaleziono pliku 'icon.ico'. Program będzie miał domyślną ikonę Windows.")
        print("    (Wskazówka: Wrzuć plik icon.ico do tego folderu przed kompilacją, aby użyć własnej).")
    
    cmd.append("sas4_gui_editor.py")
    
    # 3. Kompilacja
    print("\n[3/3] Rozpoczynam pakowanie (to może potrwać kilkanaście sekund)...")
    try:
        subprocess.check_call(cmd)
        print("\n=========================================")
        print("[SUKCES] Kompilacja zakończona!")
        print("Gotowy plik EXE znajdziesz w folderze 'dist'.")
        print("=========================================")
    except Exception as e:
        print(f"\n[BŁĄD KOMPILACJI]: {e}")

if __name__ == "__main__":
    build()
    input("\nWciśnij Enter, aby zakończyć...")