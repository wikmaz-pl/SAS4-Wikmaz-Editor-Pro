# 🧟‍♂️ SAS:ZA4 Wikmaz Ultimate Profile Editor Pro

[![Release](https://img.shields.io/badge/Release-V2.0-blue.svg)]()
[![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey.svg)]()
[![Python](https://img.shields.io/badge/Python-3.x-yellow.svg)]()

[🇺🇸 Read in English](#english) | [🇵🇱 Czytaj po polsku](#polski)

---

<a name="english"></a>
## 🇺🇸 English Version

Welcome to the **Ultimate SAS: Zombie Assault 4 Profile Editor**. This tool allows you to safely and fully modify your save files, bypassing Steam's double-buffering protection and Ninja Kiwi's cache sync mechanisms.

### ✨ Features
* **1-Click Auto-Find:** Automatically scans your Windows Registry and Steam Userdata to locate your hidden SAS4 profile directory.
* **Sync-3 Protection Bypass:** The game uses 3 files (`Profile.save`, `OldProfile.save`, `TempProfile.save`) to prevent tampering. This tool automatically modifies and injects all 3 simultaneously.
* **Cache Wipe (Anti-Sync):** Automatically deletes the game's server cache to force the Ninja Kiwi servers to accept your modified local save as the absolute truth.
* **Smart Randomization (Anti-Cheat Bypass):** Instead of setting everything to suspicious "9999999", the editor can generate safe, random, and massive numbers for Ammo, Grenades, and Turrets, making your account look 100% legitimate.
* **Integrated Backup System:** Safely backup and restore your files directly from the app interface.
* **Bilingual UI:** Instantly switch between English and Polish.

### 🚀 How to Use (For Beginners)

Even a 10-year-old can do it! Follow these simple steps:

1. **Download & Run:** Download `SAS4_Wikmaz_Editor_Pro.exe` from the Releases tab and open it. No installation needed!
2. **Find Save Location:** Click **"🔍 Auto-Find"** at the top. The program will automatically locate your Steam save files.
3. **Open Profile:** Click the **"1. Open & Decode"** button. Your characters will appear in the tabs below.
4. **Edit:** 
   * Change your money, unlock free skill resets, or click the **"🎲 Randomize Ammo & Grenades"** button to safely get millions of bullets!
5. **Save & Inject:** Click **"3. Save & Inject (Sync-3)"**. The tool will encode your files and clear the cache.
6. **CRITICAL STEP:** **TURN OFF YOUR INTERNET** (Wi-Fi/Cable). Launch SAS4. Enter a single-player game, die, and return to the menu. 
7. **Done!** Turn your internet back on. The server will now permanently accept your new riches.

### 💻 How to run from Source (For Developers)
If you prefer running the raw Python script:
1. Clone the repository to your disk.
2. Ensure you have the `kucingoren` folder in the same directory as the script.
3. Run the script: `python sas4_gui_editor.py` 
*(Note: Requires NO external pip packages. Standard Python 3.x is enough!)*

**To build your own EXE file:**
Run `python zbuduj_exe.py`. The builder script will automatically install `pyinstaller` and compile the `.exe` file into the `dist` folder.

---

<a name="polski"></a>
## 🇵🇱 Wersja Polska

Witaj w **SAS: Zombie Assault 4 Ultimate Profile Editor**. To potężne, w pełni zautomatyzowane narzędzie, które pozwala na modyfikowanie zapisów gry, omijając przy tym zabezpieczenia Steam (double-buffering) oraz mechanizmy synchronizacji w chmurze Ninja Kiwi.

### ✨ Główne Funkcje
* **Auto-Wyszukiwanie:** Program sam przeszukuje rejestr systemu Windows oraz strukturę Steama, aby bezbłędnie namierzyć Twój unikalny folder zapisu gry.
* **Ominięcie ochrony Sync-3:** Gra używa trzech plików (`Profile.save`, `OldProfile.save`, `TempProfile.save`), aby cofać oszustwa. Nasz edytor w locie modyfikuje i nadpisuje wszystkie trzy pliki na raz!
* **Niszczyciel Cache'u:** Po zapisaniu zmian, program automatycznie usuwa tokeny pamięci podręcznej gry. Dzięki temu zmusza serwery do zaakceptowania Twojego lokalnego zapisu.
* **Inteligentna Losowość (Bypass Anty-Cheata):** Zamiast wpisywać ryzykowne "999999", użyj wbudowanych w program przycisków losowania z ikoną kostki (🎲). Wygenerują one bezpieczne, różnorodne i gigantyczne liczby dla każdej amunicji z osobna – serwer potraktuje to jak naturalny zapis!
* **System Kopii Zapasowych:** Zrób bezpieczny backup i przywracaj pliki jednym kliknięciem.
* **Dwujęzyczny interfejs (PL/EN):** Przełączanie w czasie rzeczywistym.

### 🚀 Jak używać (Dla początkujących)

To proste jak budowa cepa! Poradzisz sobie w minutę:

1. **Pobierz i Uruchom:** Pobierz plik `SAS4_Wikmaz_Editor_Pro.exe` z zakładki "Releases" na GitHubie i po prostu go włącz (nie wymaga żadnej instalacji).
2. **Znajdź Zapis:** Kliknij **"🔍 Auto-Wyszukiwanie"** na górze okna. Program sam znajdzie, gdzie ukryte są pliki gry.
3. **Otwórz Profil:** Kliknij przycisk **"1. Otwórz i Dekoduj"**. Twoje postacie pojawią się w zakładkach poniżej.
4. **Edytuj:** 
   * Ustaw gotówkę, aktywuj darmowy reset umiejętności lub kliknij **"🎲 Losuj Amunicję i Granaty"**, aby bezpiecznie dostać grube miliony pocisków dla każdej broni!
5. **Zapisz i Wstrzyknij:** Kliknij **"3. Zapisz i Wstrzyknij (Sync-3)"**. Narzędzie zakoduje pliki w formacie DGDATA i zatrze ślady w cache'u.
6. **KROK KRYTYCZNY:** **WYŁĄCZ INTERNET** (Wi-Fi/Kabel). Uruchom grę SAS4. Wejdź na mapę w trybie Solo, daj się od razu zabić i wróć do menu (to wymusi zapis wewnątrz gry).
7. **Gotowe!** Włącz internet. Serwer bez problemu przełknie Twój nowy majątek.

### 💻 Jak uruchomić przez Pythona (Dla programistów)
Jeśli wolisz odpalić czysty kod źródłowy z konsoli:
1. Pobierz pliki z repozytorium na dysk.
2. Upewnij się, że obok skryptu znajduje się folder silnika `kucingoren`.
3. Uruchom poleceniem: `python sas4_gui_editor.py` 
*(Uwaga: Skrypt korzysta z natywnych bibliotek. Czysty Python 3.x wystarczy, nie trzeba niczego instalować przez pip!)*

**Jak zbudować własny plik EXE:**
Uruchom polecenie `python zbuduj_exe.py`. Automat sam doinstaluje pakiet `pyinstaller` i wypluje gotowy plik wykonywalny do folderu `dist`.

---

### 📬 Kontakt i Wsparcie / Contact & Support
Projekt jest rozwijany przez markę **Wikmaz**. Jeśli program Ci pomógł, odwiedź moje linki i wesprzyj twórczość! / *If this tool helped you, consider supporting me!*

* 🌐 **WWW:** [wikmaz.pl](https://wikmaz.pl)
* 📺 **YouTube:** [Wikmazpl](https://www.youtube.com/@Wikmazpl)
* 💻 **GitHub:** [wikmaz-pl](https://github.com/wikmaz-pl)
* ✉️ **E-mail:** admin@softhause.wikmaz.pl
* ☕ **Wsparcie / Support (Ko-fi):** [ko-fi.com/wikmaz](https://ko-fi.com/wikmaz)
* 💖 **Wsparcie / Support (Suppi):** [suppi.pl/wikmaz](https://suppi.pl/wikmaz)

---
*Disclaimer: This tool is for educational purposes and offline fun. Use at your own risk. / Narzędzie stworzone w celach edukacyjnych i do gry offline. Używasz na własną odpowiedzialność.*