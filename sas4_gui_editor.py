import sys
import os
import json
import shutil
import winreg
import webbrowser
import random
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog

# --- Próba importu silnika DGDATA ---
try:
    from kucingoren.gameio.dgdata import iter_decode_fromfile, encode_readwrite_helper
except ImportError as e:
    print(f"[BŁĄD IMPORTU / IMPORT ERROR]: {e}\nUpewnij się, że folder 'kucingoren' leży obok skryptu.")
    sys.exit(1)

# --- Stałe dla walidacji i losowania (Bezpieczne limity) ---
MAX_MONEY = 999_999_999
MAX_SKILL_POINTS = 500
MAX_KEYS_CORES = 10_000

# --- Słownik Tłumaczeń ---
TRANSLATIONS = {
    'pl': {
        'title': 'SAS:ZA4 Wikmaz Ultimate Profile Editor',
        'path_frame': 'Lokalizacja plików zapisu (Steam)',
        'btn_auto_find': '🔍 Auto-Wyszukiwanie',
        'btn_manual_find': '📂 Wybierz ręcznie',
        'btn_about': '⭐ O autorze / Kontakt (Wikmaz)',
        'backup_frame': 'Kopie Zapasowe (Backups)',
        'btn_backup': 'Zrób Kopię (Backup)',
        'btn_restore': 'Przywróć Zaznaczone',
        'btn_refresh': 'Odśwież Listę',
        'btn_open': '1. Otwórz i Dekoduj (Pobierz z gry)',
        'btn_validate': '2. Walidacja danych',
        'btn_save': '3. Zapisz i Wstrzyknij (Sync-3 + Wipe Cache)',
        'log_frame': 'Konsola zdarzeń',
        'msg_welcome': 'Witaj w edytorze Wikmaz! System gotowy do pracy.',
        'lbl_money': 'Gotówka (Money):',
        'lbl_skills': 'Wolne Punkty Umiejętności:',
        'lbl_keys': 'Czarne Klucze (Black Keys):',
        'lbl_cores': 'Elitarne Rdzenie (Elite Cores):',
        'lbl_free_reset': 'Darmowy Reset Umiejętności',
        'lbl_turrets_sec': '--- WIEŻYCZKI WSPARCIA ---',
        'lbl_ammo_sec': '--- AMUNICJA I GRANATY ---',
        'btn_max': '⚡ Ustaw na MAX',
        'btn_rnd_basic': '🎲 Losuj Bezpieczną Kasę',
        'btn_rnd_turrets': '🎲 Losuj Unikalne Ilości',
        'btn_rnd_ammo': '🎲 Losuj Amunicję i Granaty',
        'btn_max_ammo': '⚡ Ustaw Amunicję na MAX',
        'msg_no_path': 'BŁĄD: Wybierz lokalizację plików zapisu!',
        'msg_no_file': 'BŁĄD: Wskazany folder nie zawiera Profile.save!',
        'lang_switch': '🇬🇧 Switch to English'
    },
    'en': {
        'title': 'SAS:ZA4 Wikmaz Ultimate Profile Editor',
        'path_frame': 'Save Files Location (Steam)',
        'btn_auto_find': '🔍 Auto-Find',
        'btn_manual_find': '📂 Manual Select',
        'btn_about': '⭐ About / Contact (Wikmaz)',
        'backup_frame': 'Backups',
        'btn_backup': 'Create Backup',
        'btn_restore': 'Restore Selected',
        'btn_refresh': 'Refresh List',
        'btn_open': '1. Open & Decode (Fetch from game)',
        'btn_validate': '2. Validate Data',
        'btn_save': '3. Save & Inject (Sync-3 files)',
        'log_frame': 'Event Console',
        'msg_welcome': 'Welcome to Wikmaz Editor! System ready.',
        'lbl_money': 'Money:',
        'lbl_skills': 'Available Skill Points:',
        'lbl_keys': 'Black Keys:',
        'lbl_cores': 'Elite Cores:',
        'lbl_free_reset': 'Free Skill Reset',
        'lbl_turrets_sec': '--- TURRETS ---',
        'lbl_ammo_sec': '--- AMMO & GRENADES ---',
        'btn_max': '⚡ Set to MAX',
        'btn_rnd_basic': '🎲 Randomize Safe Money',
        'btn_rnd_turrets': '🎲 Randomize Amounts',
        'btn_rnd_ammo': '🎲 Randomize Ammo & Grenades',
        'btn_max_ammo': '⚡ Set Ammo to MAX',
        'msg_no_path': 'ERROR: Select save files location!',
        'msg_no_file': 'ERROR: Selected folder does not contain Profile.save!',
        'lang_switch': '🇵🇱 Zmień na Polski'
    }
}


class ScrollableFrame(ttk.Frame):
    def __init__(self, container, *args, **kwargs):
        super().__init__(container, *args, **kwargs)
        self.canvas = tk.Canvas(self, borderwidth=0, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.inner_frame = ttk.Frame(self.canvas)

        self.inner_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        self.canvas.create_window((0, 0), window=self.inner_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")


class SAS4EditorApp:
    def __init__(self, root):
        self.root = root
        self.lang = 'pl'
        self.root.geometry("950x750")
        
        self.current_data = None
        self.profile_vars = {} 
        self.backup_dir = "backups"
        
        if not os.path.exists(self.backup_dir):
            os.makedirs(self.backup_dir)

        self.setup_ui()
        self.update_texts()
        self.refresh_backup_list()
        self.log(self.t('msg_welcome'))
        self.auto_find_steam_path()

    def t(self, key):
        return TRANSLATIONS[self.lang].get(key, key)

    def setup_ui(self):
        # --- GÓRNY PASEK MENU ---
        top_bar = ttk.Frame(self.root)
        top_bar.pack(fill=tk.X, padx=5, pady=2)
        
        self.btn_lang = ttk.Button(top_bar, command=self.toggle_language)
        self.btn_lang.pack(side=tk.RIGHT, padx=5)
        
        self.btn_about = ttk.Button(top_bar, command=self.show_about)
        self.btn_about.pack(side=tk.RIGHT, padx=5)

        # --- PANEL GÓRNY (Wybór ścieżki) ---
        self.path_frame = ttk.LabelFrame(self.root)
        self.path_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.target_dir_var = tk.StringVar()
        ttk.Entry(self.path_frame, textvariable=self.target_dir_var, state='readonly').pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5, pady=5)
        self.btn_auto_find = ttk.Button(self.path_frame, command=self.auto_find_steam_path)
        self.btn_auto_find.pack(side=tk.LEFT, padx=5, pady=5)
        self.btn_manual_find = ttk.Button(self.path_frame, command=self.manual_select_path)
        self.btn_manual_find.pack(side=tk.LEFT, padx=5, pady=5)

        # --- GŁÓWNY PODZIAŁ ---
        paned = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.left_frame = ttk.Frame(paned, width=220)
        right_frame = ttk.Frame(paned)
        paned.add(self.left_frame, weight=1)
        paned.add(right_frame, weight=4)

        # --- PANEL LEWY (Backupy) ---
        self.lbl_backup = ttk.Label(self.left_frame, font=("Arial", 10, "bold"))
        self.lbl_backup.pack(pady=5)
        
        self.backup_listbox = tk.Listbox(self.left_frame)
        self.backup_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.btn_backup = ttk.Button(self.left_frame, command=self.create_backup)
        self.btn_backup.pack(fill=tk.X, padx=5, pady=2)
        self.btn_restore = ttk.Button(self.left_frame, command=self.restore_backup)
        self.btn_restore.pack(fill=tk.X, padx=5, pady=2)
        self.btn_refresh = ttk.Button(self.left_frame, command=self.refresh_backup_list)
        self.btn_refresh.pack(fill=tk.X, padx=5, pady=2)

        # --- PANEL PRAWY (Akcje i Edycja) ---
        action_frame = ttk.Frame(right_frame)
        action_frame.pack(fill=tk.X, pady=5)
        
        self.btn_open = ttk.Button(action_frame, command=self.decode_file)
        self.btn_open.pack(side=tk.LEFT, padx=5)
        self.btn_validate = ttk.Button(action_frame, command=self.validate_data)
        self.btn_validate.pack(side=tk.LEFT, padx=5)
        self.btn_save = ttk.Button(action_frame, command=self.encode_file)
        self.btn_save.pack(side=tk.LEFT, padx=5)

        self.notebook = ttk.Notebook(right_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # --- KONSOLA ---
        self.log_frame = ttk.LabelFrame(self.root)
        self.log_frame.pack(fill=tk.X, padx=5, pady=5)
        self.log_text = scrolledtext.ScrolledText(self.log_frame, height=8, state=tk.DISABLED)
        self.log_text.pack(fill=tk.X, padx=5, pady=5)

    def update_texts(self):
        self.root.title(self.t('title'))
        self.btn_lang.config(text=self.t('lang_switch'))
        self.btn_about.config(text=self.t('btn_about'))
        self.path_frame.config(text=self.t('path_frame'))
        self.btn_auto_find.config(text=self.t('btn_auto_find'))
        self.btn_manual_find.config(text=self.t('btn_manual_find'))
        self.lbl_backup.config(text=self.t('backup_frame'))
        self.btn_backup.config(text=self.t('btn_backup'))
        self.btn_restore.config(text=self.t('btn_restore'))
        self.btn_refresh.config(text=self.t('btn_refresh'))
        self.btn_open.config(text=self.t('btn_open'))
        self.btn_validate.config(text=self.t('btn_validate'))
        self.btn_save.config(text=self.t('btn_save'))
        self.log_frame.config(text=self.t('log_frame'))
        
        if self.current_data:
            self.apply_ui_to_data()
            self.build_profile_tabs()

    def toggle_language(self):
        self.lang = 'en' if self.lang == 'pl' else 'pl'
        self.update_texts()
        self.log(f"Zmieniono język / Language changed to: {self.lang.upper()}")

    def show_about(self):
        top = tk.Toplevel(self.root)
        top.title(self.t('btn_about'))
        top.geometry("400x300")
        top.resizable(False, False)
        
        ttk.Label(top, text="SAS:ZA4 Wikmaz Ultimate Profile Editor", font=("Arial", 14, "bold")).pack(pady=10)
        ttk.Label(top, text="Created by: Wikmaz", font=("Arial", 10)).pack()
        ttk.Label(top, text="Contact: admin@softhause.wikmaz.pl", font=("Arial", 10)).pack(pady=5)
        
        ttk.Separator(top, orient='horizontal').pack(fill=tk.X, padx=20, pady=10)
        
        def open_url(url):
            webbrowser.open(url)

        links = [
            ("🌐 WWW:", "https://wikmaz.pl"),
            ("📺 YouTube:", "https://www.youtube.com/@Wikmazpl"),
            ("💻 GitHub:", "https://github.com/wikmaz-pl"),
            ("☕ Ko-fi Support:", "https://ko-fi.com/wikmaz"),
            ("💖 Suppi Support:", "https://suppi.pl/wikmaz")
        ]

        for text, url in links:
            frame = ttk.Frame(top)
            frame.pack(fill=tk.X, padx=40, pady=2)
            ttk.Label(frame, text=text, width=15).pack(side=tk.LEFT)
            link_lbl = tk.Label(frame, text=url, fg="blue", cursor="hand2")
            link_lbl.pack(side=tk.LEFT)
            link_lbl.bind("<Button-1>", lambda e, u=url: open_url(u))

    def log(self, message):
        self.log_text.config(state=tk.NORMAL)
        time_str = datetime.now().strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{time_str}] {message}\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)

    # ================= ZARZĄDZANIE ŚCIEŻKĄ =================
    def auto_find_steam_path(self):
        self.log("Szukam ścieżki Steama / Searching Steam path...")
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Valve\Steam") as key:
                steam_path = winreg.QueryValueEx(key, "SteamPath")[0]
                steam_path = os.path.normpath(steam_path)
        except Exception:
            steam_path = r"C:\Program Files (x86)\Steam"

        userdata_dir = os.path.join(steam_path, "userdata")
        if not os.path.exists(userdata_dir):
            self.log(f"BŁĄD: Nie znaleziono folderu / No userdata folder in {userdata_dir}.")
            return

        found_paths = []
        
        # Zbieramy wszystkie poprawne ścieżki (jeśli jest kilka kont lub hashów)
        for user_id in os.listdir(userdata_dir):
            docs_path = os.path.join(userdata_dir, user_id, "678800", "local", "Data", "Docs")
            if os.path.isdir(docs_path):
                for hash_folder in os.listdir(docs_path):
                    full_hash_path = os.path.join(docs_path, hash_folder)
                    if os.path.isdir(full_hash_path) and os.path.exists(os.path.join(full_hash_path, "Profile.save")):
                        found_paths.append(full_hash_path)

        if not found_paths:
            self.log("Nie znaleziono zapisów z automatu. / Auto-find failed. Use Manual Select.")
            return

        if len(found_paths) == 1:
            self.target_dir_var.set(found_paths[0])
            self.log(f"Auto-znaleziono / Auto-found path:\n{found_paths[0]}")
        else:
            self.log(f"Znaleziono kilka profili ({len(found_paths)}). Oczekuję na wybór... / Multiple profiles found.")
            self.choose_from_multiple_paths(found_paths)

    def choose_from_multiple_paths(self, paths):
        top = tk.Toplevel(self.root)
        top.title("Wybierz Profil / Select Profile")
        top.geometry("700x300")
        
        ttk.Label(top, text="Znaleziono kilka kont SAS4! Wybierz właściwe z listy:\nMultiple SAS4 accounts found! Select the correct one:", font=("Arial", 10, "bold")).pack(pady=10)
        
        listbox = tk.Listbox(top, width=100)
        listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        for p in paths:
            parts = p.split(os.sep)
            # parts[-6] = steam_id, parts[-1] = hash Ninja Kiwi
            try:
                steam_id = parts[-6]
                nk_hash = parts[-1]
                display_str = f"Steam ID: {steam_id} | NK Hash: {nk_hash}  ->  (...{p[-45:]})"
            except:
                display_str = p
            listbox.insert(tk.END, display_str)
            
        def on_select():
            sel = listbox.curselection()
            if sel:
                chosen = paths[sel[0]]
                self.target_dir_var.set(chosen)
                self.log(f"Wybrano profil z listy / Selected from list:\n{chosen}")
                top.destroy()
                
        ttk.Button(top, text="Wybierz zaznaczone / Select highlighted", command=on_select).pack(pady=10)

    def manual_select_path(self):
        selected = filedialog.askdirectory(title="Wskaż folder zapisu / Select folder with Profile.save")
        if selected:
            if os.path.exists(os.path.join(selected, "Profile.save")):
                self.target_dir_var.set(selected)
                self.log(f"Wybrano ręcznie / Manual path set:\n{selected}")
            else:
                messagebox.showerror("Błąd / Error", self.t('msg_no_file'))

    # ================= BACKUPY =================
    def refresh_backup_list(self):
        self.backup_listbox.delete(0, tk.END)
        for f in sorted(os.listdir(self.backup_dir), reverse=True):
            if f.endswith(".save"):
                self.backup_listbox.insert(tk.END, f)

    def create_backup(self):
        target_dir = self.target_dir_var.get()
        if not target_dir:
            self.log(self.t('msg_no_path'))
            return
            
        source_file = os.path.join(target_dir, "Profile.save")
        if not os.path.exists(source_file):
            self.log(self.t('msg_no_file'))
            return
            
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        bckp_name = f"Profile_{timestamp}.save"
        shutil.copy2(source_file, os.path.join(self.backup_dir, bckp_name))
        self.log(f"Zrobiono backup / Backup created: {bckp_name}")
        self.refresh_backup_list()

    def restore_backup(self):
        selection = self.backup_listbox.curselection()
        if not selection:
            return
            
        target_dir = self.target_dir_var.get()
        if not target_dir:
            messagebox.showerror("Błąd / Error", self.t('msg_no_path'))
            return

        bckp_name = self.backup_listbox.get(selection[0])
        backup_path = os.path.join(self.backup_dir, bckp_name)
        
        try:
            shutil.copy2(backup_path, os.path.join(target_dir, "Profile.save"))
            shutil.copy2(backup_path, os.path.join(target_dir, "OldProfile.save"))
            shutil.copy2(backup_path, os.path.join(target_dir, "TempProfile.save"))
            self.log(f"Przywrócono i zsynchronizowano / Restored & Synced: {bckp_name}")
            messagebox.showinfo("Sukces / Success", "Backup restored to all 3 files.")
        except Exception as e:
            self.log(f"BŁĄD PRZYWRACANIA / RESTORE ERROR: {e}")

    # ================= LOGIKA GRY I INTERFEJS =================
    def decode_file(self):
        target_dir = self.target_dir_var.get()
        if not target_dir:
            messagebox.showerror("Błąd / Error", self.t('msg_no_path'))
            return
            
        source_file = os.path.join(target_dir, "Profile.save")
        if not os.path.exists(source_file):
            self.log(self.t('msg_no_file'))
            return
        
        self.log(f"Dekodowanie z / Decoding from: {source_file}")
        try:
            with open(source_file, "rb") as fin, open("Profile.json", "wb") as fout:
                for chunk in iter_decode_fromfile(fin):
                    fout.write(chunk)
            
            with open("Profile.json", "r", encoding="utf-8") as f:
                self.current_data = json.load(f)
                
            self.log("Sukces. Budowanie interfejsu... / Decoded successfully. Building UI...")
            self.build_profile_tabs()
        except Exception as e:
            self.log(f"BŁĄD DEKODOWANIA / DECODE ERROR: {e}")

    def build_profile_tabs(self):
        for tab in self.notebook.tabs():
            self.notebook.forget(tab)
        self.profile_vars.clear()

        inventory = self.current_data.get("Inventory", {})
        for prof_key, prof_data in inventory.items():
            if not prof_data.get("Loaded", False):
                continue
                
            name = prof_data.get("Name", "Unknown")
            lvl = prof_data.get("Skills", {}).get("PlayerLevel", 0)
            tab_title = f"{name} (Lvl {lvl})"
            
            scroll_frame = ScrollableFrame(self.notebook)
            self.notebook.add(scroll_frame, text=tab_title)
            frame = scroll_frame.inner_frame
            
            free_reset_actual_val = bool(prof_data.get("FreeSkillsReset", False))
            
            vars_dict = {
                "Money": tk.StringVar(value=str(prof_data.get("Money", 0))),
                "SkillPoints": tk.StringVar(value=str(prof_data.get("Skills", {}).get("AvailableSkillPoints", 0))),
                "BlackKeys": tk.StringVar(value=str(prof_data.get("Skills", {}).get("AvailableBlackKeys", 0))),
                "EliteCores": tk.StringVar(value=str(prof_data.get("Skills", {}).get("AvailableEliteAugmentCores", 0))),
                "FreeReset": tk.BooleanVar(),
                "Turrets": {},
                "Ammo": {}
            }
            self.profile_vars[prof_key] = vars_dict
            
            row = 0
            
            # --- SEKCJA PODSTAWOWA ---
            ttk.Label(frame, text="--- PODSTAWOWE / BASIC ---", font=("Arial", 10, "bold")).grid(row=row, column=0, columnspan=2, pady=(10,5))
            row += 1
            
            basic_btn_frame = ttk.Frame(frame)
            basic_btn_frame.grid(row=row, column=0, columnspan=2, pady=5)
            ttk.Button(basic_btn_frame, text=self.t('btn_rnd_basic'), command=lambda p=prof_key: self.rnd_basic(p)).pack(side=tk.LEFT, padx=5)
            row += 1
            
            ttk.Label(frame, text=self.t('lbl_money')).grid(row=row, column=0, padx=10, pady=2, sticky=tk.W)
            ttk.Entry(frame, textvariable=vars_dict["Money"]).grid(row=row, column=1, padx=10, pady=2)
            row += 1
            
            ttk.Label(frame, text=self.t('lbl_skills')).grid(row=row, column=0, padx=10, pady=2, sticky=tk.W)
            ttk.Entry(frame, textvariable=vars_dict["SkillPoints"]).grid(row=row, column=1, padx=10, pady=2)
            row += 1
            
            ttk.Label(frame, text=self.t('lbl_keys')).grid(row=row, column=0, padx=10, pady=2, sticky=tk.W)
            ttk.Entry(frame, textvariable=vars_dict["BlackKeys"]).grid(row=row, column=1, padx=10, pady=2)
            row += 1

            ttk.Label(frame, text=self.t('lbl_cores')).grid(row=row, column=0, padx=10, pady=2, sticky=tk.W)
            ttk.Entry(frame, textvariable=vars_dict["EliteCores"]).grid(row=row, column=1, padx=10, pady=2)
            row += 1
            
            chk = ttk.Checkbutton(frame, text=self.t('lbl_free_reset'), variable=vars_dict["FreeReset"], onvalue=True, offvalue=False)
            chk.grid(row=row, column=0, columnspan=2, padx=10, pady=2, sticky=tk.W)
            vars_dict["FreeReset"].set(free_reset_actual_val)
            row += 1
            
            # --- SEKCJA WIEŻYCZEK ---
            turrets = prof_data.get("Turrets", [])
            if turrets:
                ttk.Separator(frame, orient='horizontal').grid(row=row, column=0, columnspan=2, sticky='ew', pady=10)
                row += 1
                ttk.Label(frame, text=self.t('lbl_turrets_sec'), font=("Arial", 10, "bold")).grid(row=row, column=0, columnspan=2, pady=(5,5))
                row += 1
                
                tur_btn_frame = ttk.Frame(frame)
                tur_btn_frame.grid(row=row, column=0, columnspan=2, pady=5)
                ttk.Button(tur_btn_frame, text=self.t('btn_rnd_turrets'), command=lambda p=prof_key: self.rnd_turrets(p)).pack(side=tk.LEFT, padx=5)
                ttk.Button(tur_btn_frame, text=self.t('btn_max'), command=lambda p=prof_key: self.max_turrets(p)).pack(side=tk.LEFT, padx=5)
                row += 1
                
                for i, t in enumerate(turrets):
                    tid = t.get("TurretId", "?")
                    tcnt = t.get("TurretCount", 0)
                    lbl_txt = f"Wieżyczka [ID: {tid}]:" if self.lang == 'pl' else f"Turret [ID: {tid}]:"
                    ttk.Label(frame, text=lbl_txt).grid(row=row, column=0, padx=10, pady=2, sticky=tk.W)
                    t_var = tk.StringVar(value=str(tcnt))
                    ttk.Entry(frame, textvariable=t_var).grid(row=row, column=1, padx=10, pady=2)
                    vars_dict["Turrets"][i] = t_var
                    row += 1

            # --- SEKCJA AMUNICJI ---
            ttk.Separator(frame, orient='horizontal').grid(row=row, column=0, columnspan=2, sticky='ew', pady=10)
            row += 1
            ttk.Label(frame, text=self.t('lbl_ammo_sec'), font=("Arial", 10, "bold")).grid(row=row, column=0, columnspan=2, pady=(5,5))
            row += 1
            
            ammo_btn_frame = ttk.Frame(frame)
            ammo_btn_frame.grid(row=row, column=0, columnspan=2, pady=5)
            ttk.Button(ammo_btn_frame, text=self.t('btn_rnd_ammo'), command=lambda p=prof_key: self.rnd_ammo(p)).pack(side=tk.LEFT, padx=5)
            ttk.Button(ammo_btn_frame, text=self.t('btn_max_ammo'), command=lambda p=prof_key: self.max_ammo(p)).pack(side=tk.LEFT, padx=5)
            row += 1
            
            ammo_dict = prof_data.get("Ammo", {})
            for ak, av in ammo_dict.items():
                ttk.Label(frame, text=f"{ak}:").grid(row=row, column=0, padx=10, pady=2, sticky=tk.W)
                a_var = tk.StringVar(value=str(av))
                ttk.Entry(frame, textvariable=a_var).grid(row=row, column=1, padx=10, pady=2)
                vars_dict["Ammo"][ak] = a_var
                row += 1

    # ================= LOGIKA LOSOWANIA I MAKSOWANIA =================
    def rnd_basic(self, profile_key):
        vars_dict = self.profile_vars.get(profile_key)
        if not vars_dict: return
        vars_dict["Money"].set(str(random.randint(400_000_000, 850_000_000)))
        self.log(f"Wylosowano bezpieczną ilość gotówki dla / Safe money rolled for {profile_key}.")

    def rnd_turrets(self, profile_key):
        vars_dict = self.profile_vars.get(profile_key)
        if not vars_dict: return
        for tvar in vars_dict["Turrets"].values():
            tvar.set(str(random.randint(1500, 8500)))
        self.log(f"Wylosowano ilości wieżyczek dla / Turrets randomized for {profile_key}.")

    def max_turrets(self, profile_key):
        vars_dict = self.profile_vars.get(profile_key)
        if not vars_dict: return
        for tvar in vars_dict["Turrets"].values():
            tvar.set("9999")
        self.log(f"Zbrojownia wymaksowana dla / Turrets maxed for {profile_key}.")

    def rnd_ammo(self, profile_key):
        vars_dict = self.profile_vars.get(profile_key)
        if not vars_dict: return
        for ak, avar in vars_dict["Ammo"].items():
            if "grenades" in ak:
                avar.set(str(random.randint(3000, 8500)))
            else:
                avar.set(str(random.randint(2_500_000, 8_900_000)))
        self.log(f"Wylosowano unikalną amunicję dla / Ammo randomly distributed for {profile_key}.")

    def max_ammo(self, profile_key):
        vars_dict = self.profile_vars.get(profile_key)
        if not vars_dict: return
        for ak, avar in vars_dict["Ammo"].items():
            avar.set("9999" if "grenades" in ak else "9999999")
        self.log(f"Wymaksowano amunicję dla / Ammo maxed out for {profile_key}.")

    # ================= ZAPIS =================
    def apply_ui_to_data(self):
        if not self.current_data: return False
        try:
            for prof_key, vars_dict in self.profile_vars.items():
                prof_data = self.current_data["Inventory"][prof_key]
                prof_data["Money"] = int(vars_dict["Money"].get())
                prof_data["FreeSkillsReset"] = bool(vars_dict["FreeReset"].get())
                
                if "Skills" not in prof_data: prof_data["Skills"] = {}
                prof_data["Skills"]["AvailableSkillPoints"] = int(vars_dict["SkillPoints"].get())
                prof_data["Skills"]["AvailableBlackKeys"] = int(vars_dict["BlackKeys"].get())
                prof_data["Skills"]["AvailableEliteAugmentCores"] = int(vars_dict["EliteCores"].get())
                
                for i, tvar in vars_dict["Turrets"].items():
                    prof_data["Turrets"][i]["TurretCount"] = int(tvar.get())
                for ak, avar in vars_dict["Ammo"].items():
                    prof_data["Ammo"][ak] = int(avar.get())
            return True
        except ValueError:
            messagebox.showerror("Błąd / Error", "W polach liczbowych wpisuj wyłącznie cyfry! / Use numbers only!")
            return False

    def validate_data(self):
        if not self.apply_ui_to_data(): return False
        self.log("Walidacja / Validation started...")
        anomalies = 0
        for prof_key, prof_data in self.current_data.get("Inventory", {}).items():
            if not prof_data.get("Loaded", False): continue
            if prof_data.get("Money", 0) > MAX_MONEY:
                self.log(f"[WARNING] {prof_key} exceeds money limit ({MAX_MONEY})!")
                anomalies += 1
            skills = prof_data.get("Skills", {})
            if skills.get("AvailableBlackKeys", 0) > MAX_KEYS_CORES:
                self.log(f"[WARNING] {prof_key} has risky amount of keys (> {MAX_KEYS_CORES}).")
        if anomalies == 0:
            self.log("Walidacja pomyślna / Validation PASSED.")
            return True
        else:
            self.log("Ostrzeżenia walidacji / Validation WARNINGS. Check logs.")
            return False

    def encode_file(self):
        if not self.current_data:
            self.log("Najpierw pobierz pliki / Open and decode file first!")
            return
        
        target_dir = self.target_dir_var.get()
        if not target_dir:
            self.log(self.t('msg_no_path'))
            return

        if not self.validate_data():
            if not messagebox.askyesno("Uwaga / Warning", "Wykryto ryzyko. Zapisać? / Anomalies detected. Save anyway?"): return

        self.create_backup()
        self.log("Szyfrowanie i wgrywanie / Encoding and syncing 3 save files...")
        try:
            with open("Profile.json", "w", encoding="utf-8") as f:
                json.dump(self.current_data, f, separators=(',', ':'))
                
            with open("Profile.json", "rb") as fin, open("Profile_temp.save", "wb") as fout:
                encode_readwrite_helper(fout, fin)
            
            shutil.copy2("Profile_temp.save", os.path.join(target_dir, "Profile.save"))
            shutil.copy2("Profile_temp.save", os.path.join(target_dir, "OldProfile.save"))
            shutil.copy2("Profile_temp.save", os.path.join(target_dir, "TempProfile.save"))
            
            cache_dir = os.path.normpath(os.path.join(target_dir, "..", "Cache", "com.ninjakiwi.link"))
            if os.path.exists(cache_dir):
                shutil.rmtree(cache_dir)
                self.log("Wyczyszczono Cache (Zatarto stary ślad synchronizacji) / Cache wiped.")
            else:
                self.log("Brak Cache (Czysty start do synchronizacji) / No Cache to wipe.")
            
            self.log("SUKCES! Gotowe. / SUCCESS! Modded files injected.")
            messagebox.showinfo("Gotowe / Ready", "Wszystkie pliki zaktualizowane / All 3 files updated successfully!\nUruchom grę offline / Run SAS4 Offline to load local changes.")
        except Exception as e:
            self.log(f"BŁĄD ZAPISU / ENCODE ERROR: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = SAS4EditorApp(root)
    root.mainloop()