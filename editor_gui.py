import sys
import os
import json
import shutil
import winreg
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog

# Próba importu silnika DGDATA
try:
    from kucingoren.gameio.dgdata import iter_decode_fromfile, encode_readwrite_helper #
except ImportError as e:
    print(f"[ERROR]: {e}\nUpewnij się, że folder 'kucingoren' leży obok skryptu lub w tym samym katalogu exe.") #[cite: 1]
    sys.exit(1)

MAX_MONEY = 999_999_999 #[cite: 1]
MAX_SKILL_POINTS = 500 #[cite: 1]
MAX_KEYS_CORES = 10_000 #[cite: 1]

class ScrollableFrame(ttk.Frame):
    def __init__(self, container, *args, **kwargs):
        super().__init__(container, *args, **kwargs)
        self.canvas = tk.Canvas(self, borderwidth=0, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview) #[cite: 1]
        self.inner_frame = ttk.Frame(self.canvas)
        self.inner_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.create_window((0, 0), window=self.inner_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units") #[cite: 1]

class SAS4EditorApp:
    def __init__(self, root):
        self.root = root
        self.current_lang = "PL"
        self.translations = {
            "PL": {
                "title": "SAS:ZA4 Ultimate GUI Editor by Wikmaz",
                "path_frame": "Lokalizacja plików zapisu (Steam)",
                "auto_btn": "🔍 Auto-Wyszukiwanie",
                "manual_btn": "📂 Wybierz ręcznie",
                "backup_lbl": "Kopie Zapasowe",
                "make_backup": "Zrób Kopię (Backup)",
                "restore_backup": "Przywróć Zaznaczone",
                "refresh_backup": "Odśwież Listę",
                "btn_open": "1. Otwórz (Pobierz ze wskazanej ścieżki)",
                "btn_val": "2. Walidacja danych",
                "btn_save": "3. Zapisz i Wstrzyknij (Synchronizuj 3 pliki)",
                "log_frame": "Konsola zdarzeń",
                "sys_ready": "Witaj w edytorze! System gotowy do pracy.",
                "lang_switch": "🇬🇧 Switch to English",
                "money": "Gotówka (Money):",
                "sp": "Wolne Punkty Umiejętności:",
                "bkeys": "Czarne Klucze:",
                "ecores": "Elitarne Rdzenie:",
                "freset": "Darmowy Reset Umiejętności",
                "turrets_title": "--- WIEŻYCZKI WSPARCIA ---",
                "ammo_btn": "⚡ Wymaksuj całą Amunicję i Granaty ⚡"
            },
            "EN": {
                "title": "SAS:ZA4 Ultimate GUI Editor by Wikmaz",
                "path_frame": "Save File Location (Steam)",
                "auto_btn": "🔍 Auto-Search",
                "manual_btn": "📂 Select Manually",
                "backup_lbl": "Backups",
                "make_backup": "Create Backup",
                "restore_backup": "Restore Selected",
                "refresh_backup": "Refresh List",
                "btn_open": "1. Open (Load from path)",
                "btn_val": "2. Validate Data",
                "btn_save": "3. Save & Inject (Sync 3 files)",
                "log_frame": "Event Console",
                "sys_ready": "Welcome! System ready.",
                "lang_switch": "🇵🇱 Zmień na Polski",
                "money": "Money:",
                "sp": "Available Skill Points:",
                "bkeys": "Black Keys:",
                "ecores": "Elite Cores:",
                "freset": "Free Skill Reset",
                "turrets_title": "--- SUPPORT TURRETS ---",
                "ammo_btn": "⚡ Max All Ammo & Grenades ⚡"
            }
        }
        
        self.root.title(self.t("title"))
        self.root.geometry("900x750")
        self.current_data = None
        self.profile_vars = {} 
        self.backup_dir = "backups" #[cite: 1]
        
        if not os.path.exists(self.backup_dir): os.makedirs(self.backup_dir)

        self.main_container = ttk.Frame(self.root)
        self.main_container.pack(fill=tk.BOTH, expand=True)
        
        self.setup_ui()
        self.refresh_backup_list() #[cite: 1]
        self.log(self.t("sys_ready"))
        self.auto_find_steam_path() #[cite: 1]

    def t(self, key):
        return self.translations[self.current_lang].get(key, key)

    def toggle_lang(self):
        self.current_lang = "EN" if self.current_lang == "PL" else "PL"
        self.root.title(self.t("title"))
        for widget in self.main_container.winfo_children(): widget.destroy()
        self.setup_ui()
        self.refresh_backup_list()
        if self.current_data: self.build_profile_tabs()

    def setup_ui(self):
        top_bar = ttk.Frame(self.main_container)
        top_bar.pack(fill=tk.X, padx=5, pady=2)
        ttk.Button(top_bar, text=self.t("lang_switch"), command=self.toggle_lang).pack(side=tk.RIGHT)

        path_frame = ttk.LabelFrame(self.main_container, text=self.t("path_frame"))
        path_frame.pack(fill=tk.X, padx=5, pady=5)
        self.target_dir_var = tk.StringVar()
        ttk.Entry(path_frame, textvariable=self.target_dir_var, state='readonly').pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5, pady=5)
        ttk.Button(path_frame, text=self.t("auto_btn"), command=self.auto_find_steam_path).pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Button(path_frame, text=self.t("manual_btn"), command=self.manual_select_path).pack(side=tk.LEFT, padx=5, pady=5)

        paned = ttk.PanedWindow(self.main_container, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        left_frame = ttk.Frame(paned, width=220)
        right_frame = ttk.Frame(paned)
        paned.add(left_frame, weight=1)
        paned.add(right_frame, weight=4)

        ttk.Label(left_frame, text=self.t("backup_lbl"), font=("Arial", 10, "bold")).pack(pady=5)
        self.backup_listbox = tk.Listbox(left_frame)
        self.backup_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        ttk.Button(left_frame, text=self.t("make_backup"), command=self.create_backup).pack(fill=tk.X, padx=5, pady=2)
        ttk.Button(left_frame, text=self.t("restore_backup"), command=self.restore_backup).pack(fill=tk.X, padx=5, pady=2)
        ttk.Button(left_frame, text=self.t("refresh_backup"), command=self.refresh_backup_list).pack(fill=tk.X, padx=5, pady=2)

        action_frame = ttk.Frame(right_frame)
        action_frame.pack(fill=tk.X, pady=5)
        ttk.Button(action_frame, text=self.t("btn_open"), command=self.decode_file).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text=self.t("btn_val"), command=self.validate_data).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text=self.t("btn_save"), command=self.encode_file).pack(side=tk.LEFT, padx=5)

        self.notebook = ttk.Notebook(right_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        log_frame = ttk.LabelFrame(self.main_container, text=self.t("log_frame"))
        log_frame.pack(fill=tk.X, padx=5, pady=5)
        self.log_text = scrolledtext.ScrolledText(log_frame, height=8, state=tk.DISABLED)
        self.log_text.pack(fill=tk.X, padx=5, pady=5)

    def log(self, message):
        self.log_text.config(state=tk.NORMAL)
        time_str = datetime.now().strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{time_str}] {message}\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)

    # --- Poniżej skrócona (kompatybilna) logika plików z Twojego kodu ---
    def auto_find_steam_path(self):
        self.log("Szukam ścieżki...")
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Valve\Steam") as key:
                steam_path = winreg.QueryValueEx(key, "SteamPath")[0]
                steam_path = os.path.normpath(steam_path)
        except Exception:
            steam_path = r"C:\Program Files (x86)\Steam"
        userdata_dir = os.path.join(steam_path, "userdata")
        if not os.path.exists(userdata_dir): return
        found_path = None
        for user_id in os.listdir(userdata_dir):
            docs_path = os.path.join(userdata_dir, user_id, "678800", "local", "Data", "Docs") #[cite: 1]
            if os.path.isdir(docs_path):
                for hash_folder in os.listdir(docs_path):
                    fp = os.path.join(docs_path, hash_folder)
                    if os.path.isdir(fp) and os.path.exists(os.path.join(fp, "Profile.save")): #[cite: 1]
                        found_path = fp; break
        if found_path:
            self.target_dir_var.set(found_path)
            self.log(f"Znaleziono: {found_path}")

    def manual_select_path(self):
        sel = filedialog.askdirectory()
        if sel: self.target_dir_var.set(sel)

    def refresh_backup_list(self):
        self.backup_listbox.delete(0, tk.END)
        for f in sorted(os.listdir(self.backup_dir), reverse=True):
            if f.endswith(".save"): self.backup_listbox.insert(tk.END, f)

    def create_backup(self):
        tdir = self.target_dir_var.get()
        if not tdir: return
        sf = os.path.join(tdir, "Profile.save") #[cite: 1]
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        bn = f"Profile_{ts}.save"
        shutil.copy2(sf, os.path.join(self.backup_dir, bn))
        self.refresh_backup_list()

    def restore_backup(self):
        sel = self.backup_listbox.curselection()
        if not sel: return
        bn = self.backup_listbox.get(sel[0])
        bp = os.path.join(self.backup_dir, bn)
        td = self.target_dir_var.get()
        shutil.copy2(bp, os.path.join(td, "Profile.save")) #[cite: 1]
        shutil.copy2(bp, os.path.join(td, "OldProfile.save")) #[cite: 1]
        shutil.copy2(bp, os.path.join(td, "TempProfile.save")) #[cite: 1]
        self.log("Backup przywrócony do 3 plików.")

    def decode_file(self):
        td = self.target_dir_var.get()
        sf = os.path.join(td, "Profile.save") #[cite: 1]
        with open(sf, "rb") as fin, open("Profile.json", "wb") as fout:
            for chunk in iter_decode_fromfile(fin): fout.write(chunk) #[cite: 1]
        with open("Profile.json", "r", encoding="utf-8") as f:
            self.current_data = json.load(f)
        self.build_profile_tabs()

    def build_profile_tabs(self):
        for tab in self.notebook.tabs(): self.notebook.forget(tab)
        self.profile_vars.clear()
        inventory = self.current_data.get("Inventory", {})
        for pk, pdata in inventory.items():
            if not pdata.get("Loaded", False): continue
            name = pdata.get("Name", "Unknown")
            lvl = pdata.get("Skills", {}).get("PlayerLevel", 0)
            sf = ScrollableFrame(self.notebook)
            self.notebook.add(sf, text=f"{name} (Lvl {lvl})")
            frame = sf.inner_frame
            vd = {
                "Money": tk.StringVar(value=str(pdata.get("Money", 0))),
                "SkillPoints": tk.StringVar(value=str(pdata.get("Skills", {}).get("AvailableSkillPoints", 0))),
                "BlackKeys": tk.StringVar(value=str(pdata.get("Skills", {}).get("AvailableBlackKeys", 0))),
                "EliteCores": tk.StringVar(value=str(pdata.get("Skills", {}).get("AvailableEliteAugmentCores", 0))),
                "FreeReset": tk.BooleanVar(value=pdata.get("FreeSkillsReset", False)),
                "Turrets": {}, "Ammo": {}
            }
            self.profile_vars[pk] = vd
            
            row = 0
            ttk.Label(frame, text=self.t("money")).grid(row=row, column=0, sticky=tk.W); ttk.Entry(frame, textvariable=vd["Money"]).grid(row=row, column=1); row+=1
            ttk.Label(frame, text=self.t("sp")).grid(row=row, column=0, sticky=tk.W); ttk.Entry(frame, textvariable=vd["SkillPoints"]).grid(row=row, column=1); row+=1
            ttk.Label(frame, text=self.t("bkeys")).grid(row=row, column=0, sticky=tk.W); ttk.Entry(frame, textvariable=vd["BlackKeys"]).grid(row=row, column=1); row+=1
            ttk.Label(frame, text=self.t("ecores")).grid(row=row, column=0, sticky=tk.W); ttk.Entry(frame, textvariable=vd["EliteCores"]).grid(row=row, column=1); row+=1
            
            ttk.Label(frame, text=self.t("turrets_title")).grid(row=row, column=0, columnspan=2); row+=1
            for i, t in enumerate(pdata.get("Turrets", [])):
                tvar = tk.StringVar(value=str(t.get("TurretCount", 0)))
                ttk.Label(frame, text=f"Turret ID {t.get('TurretId')}:").grid(row=row, column=0, sticky=tk.W)
                ttk.Entry(frame, textvariable=tvar).grid(row=row, column=1)
                vd["Turrets"][i] = tvar
                row+=1

            ttk.Button(frame, text=self.t("ammo_btn"), command=lambda p=pk: self.max_ammo(p)).grid(row=row, column=0, columnspan=2); row+=1
            for ak, av in pdata.get("Ammo", {}).items():
                avar = tk.StringVar(value=str(av))
                ttk.Label(frame, text=f"{ak}:").grid(row=row, column=0, sticky=tk.W); ttk.Entry(frame, textvariable=avar).grid(row=row, column=1)
                vd["Ammo"][ak] = avar; row+=1

    def max_ammo(self, pk):
        vd = self.profile_vars.get(pk)
        for ak, avar in vd["Ammo"].items(): avar.set("9999" if "grenades" in ak else "9999999")

    def apply_ui_to_data(self):
        try:
            for pk, vd in self.profile_vars.items():
                pd = self.current_data["Inventory"][pk]
                pd["Money"] = int(vd["Money"].get())
                pd["Skills"]["AvailableSkillPoints"] = int(vd["SkillPoints"].get())
                pd["Skills"]["AvailableBlackKeys"] = int(vd["BlackKeys"].get())
                pd["Skills"]["AvailableEliteAugmentCores"] = int(vd["EliteCores"].get())
                for i, tvar in vd["Turrets"].items(): pd["Turrets"][i]["TurretCount"] = int(tvar.get())
                for ak, avar in vd["Ammo"].items(): pd["Ammo"][ak] = int(avar.get())
            return True
        except ValueError: return False

    def validate_data(self): return self.apply_ui_to_data()

    def encode_file(self):
        self.apply_ui_to_data()
        self.create_backup()
        td = self.target_dir_var.get()
        with open("Profile.json", "w", encoding="utf-8") as f: json.dump(self.current_data, f, separators=(',', ':'))
        with open("Profile.json", "rb") as fin, open("Profile_temp.save", "wb") as fout:
            encode_readwrite_helper(fout, fin) #[cite: 1]
        shutil.copy2("Profile_temp.save", os.path.join(td, "Profile.save")) #[cite: 1]
        shutil.copy2("Profile_temp.save", os.path.join(td, "OldProfile.save")) #[cite: 1]
        shutil.copy2("Profile_temp.save", os.path.join(td, "TempProfile.save")) #[cite: 1]
        self.log("ZAPISANO I WSTRZYKNIĘTO!")
        messagebox.showinfo("OK", "Zaktualizowano 3 pliki: Profile.save, OldProfile.save, TempProfile.save") #[cite: 1]

if __name__ == "__main__":
    root = tk.Tk()
    root.tk.call("tk", "scaling", 1.5) # Skalowanie dla wygody oczu!
    app = SAS4EditorApp(root)
    root.mainloop()
