#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#  CubeEncounters.py
#
#  Copyright (c) 2025 Rocket.Giovanni.Boss
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to deal
#  in the Software without restriction, including without limitation the rights
#  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#  copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in all
#  copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#  SOFTWARE.
#

# ========================================================================================= #
# CUBE ENCOUNTERS - GUIDED USER INTERFACE -v0.5 #
# ========================================================================================= #

import tkinter as tk
from tkinter import ttk, filedialog
from tkinter import messagebox
import shutil
import json
import pandas as pd
import os
import re
from PIL import Image, ImageTk

#------------------------------------------------------------------------------------------ #
# ---------- WARNINGS AND DISCLAIMERS ---------- #
#------------------------------------------------------------------------------------------ #

""" WARNINGS AND DISCLAIMERS: I'm a begginer programmer and probably melted a bit of every 
sector in my brain coding this, even with the help of OpenAI's GPT-kun.
This CubeEncounters tool was originally aimed for PERSONAL USE only, but since it was useful
to me, I'm making it available in hopes it's useful to others who are not good at programming
or handling pokeheartgold's files such as myself, or for those who simply want a more visual
sollution for editing HeartGold and SoulSilver endless and varied list of wild encounters. 
That being said, use this code as a tool AT YOUR OWN RISK!
Since I know I'm not good at this, I've already tried to set this code so it doesn't change
anything directly into the pret project file, however, even so, user discretion and setting 
up a backup of the original project are both strongly advised!"""

#------------------------------------------------------------------------------------------ #
# ---------- Auto Load Last Project ---------- #
#------------------------------------------------------------------------------------------ #

# When debugging this I think selecting the project again and again to test cost me hours!
# To avoid further waste of time, this code will recall where I was the last time I opened a session:
CONFIG_FILE = "config.json"

# Function to save the last session's directory for the pokeheartgold pret project:
def save_config(project_path, csv_choice, profile_name=""):
    data = {
        "project_path": project_path,
        "csv_choice": csv_choice,
        "profile_name": profile_name
    }
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f)

# If there is a session save file, it'll load it and get the user back to where they were:
def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return None

#------------------------------------------------------------------------------------------ #
# ---------- User-Friendly Map Names ---------- #
#------------------------------------------------------------------------------------------ #
"""The map list in the wild encounter csv has map names as codes which non-extreme pokenerds
will find diffult to associate to which route/area they represent. This part of the code will
read the file "maps.h", check which route/area the codes refer to and display each "codename"
in the side bar with that name without changing it in the sessions data or exported csvs"""


def parse_maps_h(maps_h_path):
    """
    Faz o parsing do arquivo maps.h e retorna um dict:
    { código_do_map (ex: 'D17R1101') : nome_legivel (ex: 'MAP_BELLCHIME_TOWER') }
    """
    mapping = {}
    with open(maps_h_path, "r", encoding="utf-8") as f:
        for line in f:
            m = re.match(r"#define\s+(MAP_[A-Z0-9_]+)\s+\d+\s+//\s+MAP_([A-Z0-9]+)", line)
            if m:
                nome_legivel, codigo = m.groups()
                mapping[codigo] = nome_legivel
    return mapping

#------------------------------------------------------------------------------------------ #
# ---------- Species Loading Class ---------- #
#------------------------------------------------------------------------------------------ #

class SpeciesLoader:
    def __init__(self, project_path):
        self.project_path = project_path
        self.species_dict = {}
        self.placeholder = None
        self.load_species()
        self.create_placeholder()

    def load_species(self):
        species_path = os.path.join(self.project_path, "include", "constants", "species.h")
        with open(species_path, encoding="utf-8") as f:
            for line in f:
                match = re.match(r"#define (SPECIES_[A-Z0-9_]+)\s+(\d+)", line)
                if match:
                    name, num = match.groups()
                    display_name = name.replace("SPECIES_", "")
                    self.species_dict[display_name] = (name, int(num))

    def get_sprite(self, species_num, species_name=None):
        """This function will get the species' sprite in the project's directory, crop it and display it,
        it's set to go for the male sprite, however, since some species are female-only, it'll check for that
        before loading the sprite, going for fallback or an empty placeholder transparent 80x80 sprite depending
        on what it checks."""
        # Detects if the species is female:
        is_female_only = False
        if species_name and species_name.endswith("_F"):
            is_female_only = True

        base_dir = os.path.join(
            self.project_path, "files", "poketool", "pokegra", "pokegra", f"{species_num:04d}"
        )

        # If it's a female-only species such as SPECIES_NIDORAN_F, it'll try for female sprite:
        search_paths = []
        if is_female_only:
            search_paths.append(os.path.join(base_dir, "female", "front.png"))
        else:
            search_paths.append(os.path.join(base_dir, "male", "front.png"))
            search_paths.append(os.path.join(base_dir, "female", "front.png"))

        for sprite_path in search_paths:
            if os.path.exists(sprite_path):
                try:
                    img = Image.open(sprite_path).crop((0, 0, 80, 80)).convert("RGBA")
                    return ImageTk.PhotoImage(img)
                except:
                    continue

        return self.placeholder

    # Placeholder 80x80 transparent png in case no sprite is found.
    def create_placeholder(self):
        img = Image.new("RGBA", (80, 80), (0, 0, 0, 0))
        self.placeholder = ImageTk.PhotoImage(img)

#------------------------------------------------------------------------------------------ #
# ---------- Encounter Tab ---------- #
#------------------------------------------------------------------------------------------ #

"""This will load the tabs with the wild encounter information collected from the .csv"""

class EncounterTab:
    def __init__(self, parent, name, df_row, species_loader, species_cols,
                 level_cols=None, shared_level_vars=None, min_max_cols=None):
        self.frame = tk.Frame(parent)
        self.name = name
        self.df_row = df_row
        self.species_loader = species_loader
        self.species_cols = species_cols
        self.level_cols = level_cols
        self.min_max_cols = min_max_cols
        self.species_vars = []
        self.level_vars = []
        self.min_max_vars = []
        self.build_tab(shared_level_vars)

    # Tab-building function:
    def build_tab(self, shared_level_vars=None):
        self.sprite_labels = []
        for i, col in enumerate(self.species_cols):
            row, col_pos = divmod(i, 4)

            # Sprite
            species_name = self.df_row[col]
            display_name = species_name.replace("SPECIES_", "") if isinstance(species_name, str) else "NONE"
            species_num = self.species_loader.species_dict.get(display_name, ("SPECIES_NONE", 0))[1]
            sprite_img = self.species_loader.get_sprite(species_num)
            sprite_label = tk.Label(self.frame, image=sprite_img)
            sprite_label.image = sprite_img
            sprite_label.grid(row=row*4, column=col_pos * 2, pady=2)  # note o col_pos * 2 aqui
            self.sprite_labels.append(sprite_label)

            # Combobox
            var = tk.StringVar(value=display_name)
            cb = ttk.Combobox(self.frame, textvariable=var,
                              values=sorted(self.species_loader.species_dict.keys()), width=15)
            cb.grid(row=row*4 + 1, column=col_pos * 2, padx=2, pady=2)

            cb.bind("<<ComboboxSelected>>", lambda e, idx=i: self.on_species_selected(idx))
            self.species_vars.append((var, col))

            # Min/Max Level (Surf, Smash, Rods):
            if self.min_max_cols:
                min_col, max_col = self.min_max_cols[i]
                min_var = tk.StringVar(value=str(self.df_row[min_col]))
                max_var = tk.StringVar(value=str(self.df_row[max_col]))

                tk.Label(self.frame, text="Min. Level").grid(row=row*4 + 2, column=col_pos * 2, sticky="ew")
                tk.Entry(self.frame, textvariable=min_var, width=5).grid(row=row*4 + 2, column=col_pos * 2 + 1, sticky="ew", pady=1)

                tk.Label(self.frame, text="Max. Level").grid(row=row*4 + 3, column=col_pos * 2, sticky="ew")
                tk.Entry(self.frame, textvariable=max_var, width=5).grid(row=row*4 + 3, column=col_pos * 2 + 1, sticky="ew", pady=1)

                self.min_max_vars.append(((min_var, min_col), (max_var, max_col)))

            # Regular Level for land Species (Morning/Day/Night):
            elif self.level_cols:
                lvl_col = self.level_cols[i]
                if shared_level_vars:
                    lvl_var = shared_level_vars[i]
                else:
                    lvl_var = tk.StringVar(value=str(self.df_row[lvl_col]))

                tk.Label(self.frame, text="Species Level").grid(row=row*4 + 2, column=col_pos * 2, sticky="ew")
                tk.Entry(self.frame, textvariable=lvl_var, width=5).grid(row=row*4 + 2, column=col_pos * 2 + 1, sticky="ew", pady=1)

                self.level_vars.append((lvl_var, lvl_col))

    # This function updates the new selected species' sprite into the session's data:
    def on_species_selected(self, idx):
            var, col = self.species_vars[idx]
            species_name = var.get()
            species_num = self.species_loader.species_dict.get(species_name, ("SPECIES_NONE", 0))[1]
            new_sprite = self.species_loader.get_sprite(species_num)

            label = self.sprite_labels[idx]
            label.configure(image=new_sprite)
            label.image = new_sprite

    def update_df(self, df, df_row):
        for var, col in self.species_vars:
            df.loc[df_row.name, col] = "SPECIES_" + var.get()
        for var, col in self.level_vars:
            df.loc[df_row.name, col] = int(var.get()) if var.get().isdigit() else 0
        for (min_var, min_col), (max_var, max_col) in self.min_max_vars:
            df.loc[df_row.name, min_col] = int(min_var.get()) if min_var.get().isdigit() else 0
            df.loc[df_row.name, max_col] = int(max_var.get()) if max_var.get().isdigit() else 0

#------------------------------------------------------------------------------------------ #
# ---------- Main App ---------- #
#------------------------------------------------------------------------------------------ #

"""This is the App's GUI"""

class EncounterEditorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("CubeEncounters - Wild Encounter Editor")

        self.profile_name_var = tk.StringVar()
        self.project_path = None
        self.df = None
        self.species_loader = None
        self.current_row_idx = None
        self.encounter_tabs = []
        self.tabs_notebook = None

        self.master_frame = tk.Frame(self.root)
        self.master_frame.pack(fill="both", expand=True, padx=5, pady=5)

        self.create_top_frame()
        self.create_left_frame()
        self.create_main_frame()
        self.create_bottom_frame()

        self.maps_dict = {}
        self.map_display_to_code = {}
        self.map_code_to_display = {}

        # Loads Profile Last Session applied changes if any:
        config = load_config()

        if config and os.path.exists(config.get("project_path", "")):
            self.project_path = config["project_path"]

            # Creates Species Loader using the previous session data if any:
            self.species_loader = SpeciesLoader(self.project_path)

            # Updates map list so "map codes" become recognizable map names:
            maps_h_path = os.path.join(self.project_path, "include", "constants", "maps.h")
            if os.path.exists(maps_h_path):
                self.maps_dict = parse_maps_h(maps_h_path)
            else:
                self.maps_dict = {}

            # Populates Comboboxes and updates it with the previously selected .csv file:
            enc_path = os.path.join(self.project_path, "files", "fielddata", "encountdata")
            available = []
            if os.path.exists(os.path.join(enc_path, "g_enc_data.csv")):
                available.append("HeartGold (g_enc_data.csv)")
            if os.path.exists(os.path.join(enc_path, "s_enc_data.csv")):
                available.append("SoulSilver (s_enc_data.csv)")
            self.csv_choice["values"] = available

            csv_to_select = config.get("csv_choice")
            if csv_to_select in available:
                self.csv_choice.set(csv_to_select)
            elif "HeartGold (g_enc_data.csv)" in available:
                self.csv_choice.set("HeartGold (g_enc_data.csv)")
            else:
                self.csv_choice.set(available[0] if available else "")

            # Loads CSV in self.df:
            self.load_csv()

            # Defines last session profile name in the interface:
            profile_name = config.get("profile_name", "")
            self.profile_name_var.set(profile_name)

            # If there's a saved profile, it loads that profile's session:
            if profile_name:
                self.load_profile_session(profile_name)

        else:
            # No valid configuration, so it initializes SpeciesLoader as "None" for safety reasons:
            self.species_loader = None


    # This selects the project's directory:
    def create_top_frame(self):
        frame = tk.Frame(self.master_frame)
        frame.pack(fill="x", padx=5, pady=5)

        # Directory/Version Frame
        dir_frame = tk.LabelFrame(frame, text="Directory/Version")
        dir_frame.pack(side="left", padx=5, pady=5, fill="x", expand=True)

        tk.Button(dir_frame, text="Select Project Folder", command=self.select_project).pack(side="left", padx=5, pady=5)

        self.csv_choice = ttk.Combobox(dir_frame, values=[])
        self.csv_choice.pack(side="left", padx=5, pady=5)
        self.csv_choice.bind("<<ComboboxSelected>>", self.load_csv)

        # Output Frame
        output_frame = tk.LabelFrame(frame, text="Output")
        output_frame.pack(side="left", padx=5, pady=5, fill="x", expand=True)
        
        # Current Project's Profile Name:
        tk.Label(output_frame, text="Profile:").pack(side="left", padx=(5, 0), pady=5)

        self.profile_name_var = tk.StringVar()
        self.profile_entry = tk.Entry(output_frame, textvariable=self.profile_name_var, width=15)
        self.profile_entry.pack(side="left", padx=5, pady=5)

        tk.Button(output_frame, text="Apply Changes", command=self.apply_changes).pack(side="left", padx=5, pady=5)
        tk.Button(output_frame, text="Export CSV", command=self.export_csv).pack(side="left", padx=5, pady=5)
    
    # This is where the Map Tree is loaded. Click map names to load Encounter Tabs.
    def create_left_frame(self):
        # This creates a container to set up a tittle on top of the map tree list:
        container = tk.Frame(self.master_frame)
        container.pack(side="left", fill="y", padx=5, pady=5)

        # This adds an outline box around the map tree list as it creates it:
        frame = tk.LabelFrame(container, text="Map Index")
        frame.pack(side="top", fill="y", expand=True, padx=5, pady=5)

        scrollbar = tk.Scrollbar(frame, orient="vertical")
        scrollbar.pack(side="right", fill="y")

        self.map_list = tk.Listbox(frame, width=30, yscrollcommand=scrollbar.set)
        self.map_list.pack(side="left", fill="both", expand=True)

        scrollbar.config(command=self.map_list.yview)

        self.map_list.bind("<<ListboxSelect>>", self.select_map)
    
    # Guess what this does, I DARE YOU!
    def create_main_frame(self):
        frame = tk.Frame(self.master_frame)
        frame.pack(side="left", fill="both", expand=True, padx=5, pady=5)

        rates_frame = tk.LabelFrame(frame, text="Encounter Rates")
        rates_frame.pack(fill="x", pady=5)

        self.rate_vars = {}

        for col, rate_name in enumerate(["rate_walk", "rate_surf", "rate_smash",
                                         "rate_oldrod", "rate_goodrod", "rate_superrod"]):
            tk.Label(rates_frame, text=rate_name).grid(row=0, column=col * 2, padx=2, pady=2, sticky="e")
            var = tk.StringVar()
            tk.Entry(rates_frame, textvariable=var, width=5).grid(row=0, column=col * 2 + 1, padx=2, pady=2)
            self.rate_vars[rate_name] = var

        self.tabs_notebook = ttk.Notebook(frame)
        self.tabs_notebook.pack(fill="both", expand=True)
    
    # Apply and Export Button Frame. Click to Apply changes and export CSV.
    def create_bottom_frame(self):
        frame = tk.Frame(self.root)
        frame.pack(side="bottom", fill="x", pady=5)
        label = tk.Label(frame, text="By Rocket.Giovanni.Boss, 2025", font=("Arial", 10, "italic"))
        label.pack(pady=2, expand=True)

    # Makes map codenames become their readable version, such as R35 becoming Route_35:
    def populate_map_list(self):
        # Checks if there's a readable equivalence for the map codename in the project:
        readable_names = [self.map_code_to_display.get(code, code) for code in self.df["mapname"]]

        # Removes duplicates:
        unique_sorted = sorted(set(readable_names))

        self.map_list.delete(0, tk.END)
        for name in unique_sorted:
            self.map_list.insert(tk.END, name)

    # When you click "Apply", this will make the app save your current session state without exporting it.
    # This way, when you open the session again, the "Profile" field will be saved and temporary changes too.
    def save_profile_session(self):
        profile = self.profile_name_var.get().strip()
        if not profile:
            return

        session_data = {
            "project_path": self.project_path,
            "csv_choice": self.csv_choice.get(),
            "profile_name": profile,
            "data": self.df.to_dict(orient="records")  # salva todo o dataframe em forma de lista de dicts
        }
        session_path = os.path.join(os.getcwd(), f"profile_session_{profile}.json")
        with open(session_path, "w", encoding="utf-8") as f:
            json.dump(session_data, f, indent=4)

    # This loads the last session Profile data saved by using the method above:
    def load_profile_session(self, profile_name):
        session_path = os.path.join(os.getcwd(), f"profile_session_{profile_name}.json")
        if os.path.exists(session_path):
            with open(session_path, "r", encoding="utf-8") as f:
                session_data = json.load(f)
            # Updates the app's DataFrame:
            data_records = session_data.get("data", [])
            if data_records:
                self.df = pd.DataFrame(data_records)
                # Updates GUI with the loaded data parameters:
                self.refresh_ui_after_load()
            # Updates Profile Name entry, just in case:
            self.profile_name_var.set(session_data.get("profile_name", ""))
        else:
            print(f"No saved session found for profile '{profile_name}'.")

    # This one you'll never guess!
    def refresh_ui_after_load(self):
        self.populate_map_list()  # Populates map_list with readable reconizable names.

        # Clears all Tabs:
        for tab in self.encounter_tabs:
            self.tabs_notebook.forget(tab.frame)
        self.encounter_tabs.clear()

        # Clears selected map's index:
        self.current_row_idx = None

        # (Re)loads tabs for the first map on the list.
        if self.df is not None and not self.df.empty:
            self.map_list.selection_set(0)  # Selects first map.
            self.select_map()  # Calls tab creation.

    # This applies the current changes into the app's temporary database:
    def apply_changes(self):
        profile_name = self.profile_name_var.get().strip()
        if not profile_name:
            messagebox.showwarning("No Profile Name", "Please enter a profile name before applying changes.")
            return
        
        # If profile name already exists, warn user:
        profile_path = os.path.join(self.project_path, f"Profile{profile_name}")
        if os.path.exists(profile_path):
            proceed = messagebox.askyesno(
                "Profile Exists",
                f"There is already a Profile named '{profile_name}'. Apply changes to it?"
            )
            if not proceed:
                return
        
        # A map needs to be selected on the map list on the left, otherwise what changes are you even applying?
        if self.current_row_idx is None:
            messagebox.showwarning("Warning", "No map selected!")
            return
        row = self.df.iloc[self.current_row_idx]
        
        # Updates rates:
        for rate_name in self.rate_vars:
            self.df.loc[row.name, rate_name] = int(self.rate_vars[rate_name].get()) if self.rate_vars[rate_name].get().isdigit() else 0
        
        # Updates tabs:
        for tab in self.encounter_tabs:
            tab.update_df(self.df, row)
        messagebox.showinfo("Applied", f"Changes applied to map '{row['mapname']}'.")
        print(f"Saving config with profile_name: '{profile_name}'")
        save_config(self.project_path, self.csv_choice.get(), profile_name)
        self.save_profile_session()
        

    # This exports the app's current database as CSVs into the app's directory (not into the project's directory):
    def export_csv(self):
        profile_name = self.profile_name_var.get().strip()

        base_dir = os.getcwd()

        if profile_name:
            # Uses the curent session's Profile name to create the export folder:
            export_base_dir = os.path.join(base_dir, profile_name)
            if not os.path.exists(export_base_dir):
                os.makedirs(export_base_dir)
        else:
            # If there isn't a Profile name set, it'll give the folder a generic RemakeXXXX name.
            # It'll check for Remake0000, Remake0001, and so on to find a new export folder name.
            count = 1
            while True:
                remake_dir = os.path.join(base_dir, f"Remake{count:04d}")
                if not os.path.exists(remake_dir):
                    os.makedirs(remake_dir)
                    export_base_dir = remake_dir
                    break
                count += 1
        
        # Here this function will check if the user is exporting a HeartGold or SoulSilver .csv.
        choice = self.csv_choice.get()
        file_name = "g_enc_data.csv" if "HeartGold" in choice else "s_enc_data.csv"
        export_path = os.path.join(export_base_dir, file_name)

        self.df.to_csv(export_path, index=False, encoding="utf-8")
        messagebox.showinfo("Exported", f"CSV exported to:\n{export_path}")

    # This selects the project's directory that the user wants to edit.
    # It'll load the one from the previous session if any by default.
    def select_project(self):
        path = filedialog.askdirectory()
        if not path:
            return
        self.project_path = path
        self.species_loader = SpeciesLoader(path)
        maps_h_path = os.path.join(self.project_path, "include", "constants", "maps.h")
        if os.path.exists(maps_h_path):
            self.maps_dict = parse_maps_h(maps_h_path)
        else:
            self.maps_dict = {}

        self.map_display_to_code = {}
        self.map_code_to_display = {}

        enc_path = os.path.join(path, "files", "fielddata", "encountdata")
        available = []
        if os.path.exists(os.path.join(enc_path, "g_enc_data.csv")):
            available.append("HeartGold (g_enc_data.csv)")
        if os.path.exists(os.path.join(enc_path, "s_enc_data.csv")):
            available.append("SoulSilver (s_enc_data.csv)")
        self.csv_choice["values"] = available

        # Selects the HeartGold csv by default for the sake of saving a click in the combobox:
        if "HeartGold (g_enc_data.csv)" in available:
            self.csv_choice.set("HeartGold (g_enc_data.csv)")
        elif available:
            self.csv_choice.set(available[0])
        else:
            self.csv_choice.set("")

        # This saves configurations for next session of the app.
        save_config(self.project_path, self.csv_choice.get())

        # This calls for the csv when the user selects a new one.
        self.load_csv()

    # This loads the csv files that define encounters.
    # g_enc_data.csv is the file for HeartGold Encounters.
    # s_enc_data.csv is the file for SoulSilver Encounters.
    def load_csv(self, event=None):
        enc_path = os.path.join(self.project_path, "files", "fielddata", "encountdata")
        choice = self.csv_choice.get()
        file = "g_enc_data.csv" if "HeartGold" in choice else "s_enc_data.csv"
        self.df = pd.read_csv(os.path.join(enc_path, file), encoding="utf-8")
        self.map_list.delete(0, tk.END)
        self.map_display_to_code.clear()
        self.map_code_to_display.clear()

        map_display_pairs = []
        for mapname in self.df["mapname"]:
            display = self.maps_dict.get(mapname, mapname)
            if display.startswith("MAP_"):
                display = display[4:]
            map_display_pairs.append( (display, mapname) )

        map_display_pairs.sort(key=lambda x: x[0])  # This will sort map "recognizable" names in alphabetical order.

        self.map_list.delete(0, tk.END)
        self.map_display_to_code.clear()
        self.map_code_to_display.clear()

        for display, mapname in map_display_pairs:
            self.map_display_to_code[display] = mapname
            self.map_code_to_display[mapname] = display
            self.map_list.insert(tk.END, display)

        # This saves configurations for next session of the app.
        save_config(self.project_path, choice)

    # Generate tabs when user clicks a map's name on the Map Tree list on the left:
    def select_map(self, event=None):
        sel = self.map_list.curselection()
        if not sel or self.df is None:
            return
        display_name = self.map_list.get(sel[0])
        actual_map_code = self.map_display_to_code.get(display_name, display_name)

        # This will find the name of the map in the game instead of it's code:
        matches = self.df.index[self.df["mapname"] == actual_map_code].tolist()
        if not matches:
            return
        idx = matches[0]

        self.current_row_idx = idx
        row = self.df.iloc[idx]

        # Handles Rates:
        for rate_name in self.rate_vars:
            self.rate_vars[rate_name].set(row[rate_name])

        # Clears tabs
        for tab in self.tabs_notebook.tabs():
            self.tabs_notebook.forget(tab)
        self.encounter_tabs.clear()

        # Shared levels for Land species (Morning/Day/Night):
        shared_level_vars = [tk.StringVar(value=str(row[f"land_lvl{i}"])) for i in range(12)]

        # Tabs for Land encounters (Morning/Day/Night).
        self.add_tab("Land Morning", row, [f"land_species_morn{i}" for i in range(12)],
                     [f"land_lvl{i}" for i in range(12)], shared_level_vars)
        self.add_tab("Land Day", row, [f"land_species_day{i}" for i in range(12)],
                     [f"land_lvl{i}" for i in range(12)], shared_level_vars)
        self.add_tab("Land Night", row, [f"land_species_nite{i}" for i in range(12)],
                     [f"land_lvl{i}" for i in range(12)], shared_level_vars)

        # Tabs for Hoenn/Sinnoh encounters.
        self.add_tab("Hoenn", row, ["hoenn1", "hoenn2"])
        self.add_tab("Sinnoh", row, ["sinnoh1", "sinnoh2"])

        # Tabs for Surf / Smash / Rods / Swarm encounters.
        self.add_tab("Surf", row, [f"species_surf{i}" for i in range(5)],
                     min_max_cols=[(f"lvl_min_surf{i}", f"lvl_max_surf{i}") for i in range(5)])
        self.add_tab("Smash", row, [f"species_smash{i}" for i in range(2)],
                     min_max_cols=[(f"lvl_min_smash{i}", f"lvl_max_smash{i}") for i in range(2)])
        self.add_tab("Old Rod", row, [f"species_oldrod{i}" for i in range(5)],
                     min_max_cols=[(f"lvl_min_oldrod{i}", f"lvl_max_oldrod{i}") for i in range(5)])
        self.add_tab("Good Rod", row, [f"species_goodrod{i}" for i in range(5)],
                     min_max_cols=[(f"lvl_min_goodrod{i}", f"lvl_max_goodrod{i}") for i in range(5)])
        self.add_tab("Super Rod", row, [f"species_superrod{i}" for i in range(5)],
                     min_max_cols=[(f"lvl_min_superrod{i}", f"lvl_max_superrod{i}") for i in range(5)])
        self.add_tab("Swarm", row, [f"swarm_species{i}" for i in range(4)])
    
    # Function to add new Tab:
    def add_tab(self, name, row, species_cols, level_cols=None, shared_level_vars=None, min_max_cols=None):
        tab = EncounterTab(self.tabs_notebook, name, row, self.species_loader,
                           species_cols, level_cols, shared_level_vars, min_max_cols)
        self.tabs_notebook.add(tab.frame, text=name)
        self.encounter_tabs.append(tab)

if __name__ == "__main__":
    root = tk.Tk()
    app = EncounterEditorApp(root)
    root.geometry("1000x600")  # Default Window Size.
    # Center the app in the user's screen:
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f"{width}x{height}+{x}+{y-30}")
    root.mainloop()

#------------------------------------------------------------------------------------------ #
# ---------- WARNINGS AND DISCLAIMERS AGAIN (JUST IN CASE) ---------- #
#------------------------------------------------------------------------------------------ #

""" WARNINGS AND DISCLAIMERS: I'm a begginer programmer and probably melted a bit of every 
sector in my brain coding this, even with the help of OpenAI's GPT-kun.
This CubeEncounters tool was originally aimed for PERSONAL USE only, but since it was useful
to me, I'm making it available in hopes it's useful to others who are not good at programming
or handling pokeheartgold's files such as myself, or for those who simply want a more visual
sollution for editing HeartGold and SoulSilver endless and varied list of wild encounters. 
That being said, use this code as a tool AT YOUR OWN RISK!
Since I know I'm not good at this, I've already tried to set this code so it doesn't change
anything directly into the pret project file, however, even so, user discretion and setting 
up a backup of the original project are both strongly advised!"""

# ========================================================================================= #
# By Rocket.Giovanni.Boss, 2025 #
# ========================================================================================= #
