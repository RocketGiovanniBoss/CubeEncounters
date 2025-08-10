# 🎯 CubeEncounters (v0.5) — Wild Pokémon Encounter Editor

![Python Version](https://img.shields.io/badge/python-3.7%2B-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux-lightgrey.svg)
![Status](https://img.shields.io/badge/status-active-success.svg)

**CubeEncounters** is a graphical editor for `.csv` wild encounter table files from the [Pokémon Disassembly Project (PRET) - *pokeheartgold*](https://github.com/pret/pokeheartgold).  
It allows you to **view, edit, and export** encounter data for HeartGold/SoulSilver in an intuitive (or at least I hope so), tabbed interface.

---

## WARNINGS AND DISCLAIMERS:
I'm a begginer programmer and am just trying to help/contribute how I can to the community.
This code is functional, but since it's my first project, you can probably guess I melted a bit of every sector in my brain coding this, even with the help of OpenAI's GPT-kun.
This CubeEncounters tool was originally aimed for PERSONAL USE only, but since it was useful to me, I'm making it available in hopes it's useful to others who are not good at programming or handling pokeheartgold's files such as myself, or for those who simply want a more visual solution for editing HeartGold and SoulSilver endless and varied list of wild encounters. 
That being said, use this code as a tool AT YOUR OWN RISK! Since I know I'm not good at this, I've already tried to set this code so it doesn't change anything directly into the pret project file, however, even so, user discretion and setting up a backup of the original project are both strongly advised!

---

## ✨ Features

- 🔄 **Auto-load** the last used project.
- 📂 **Multiple editing profiles** to keep different setups.
- 📝 **Temporary changes** that can be exported to CSV anytime.
- 🗂 **Tabbed interface** for quick navigation between encounter types.
- 💻 Works on **Windows** and **Linux** (Python 3 + Tkinter).

---

## 📦 Requirements

- **Python** 3.7 or later  
- **Python packages**:
  - `pandas`
  - `pillow` (PIL)
- **OS**: Windows or Linux

---

## 🚀 How to Use

1. **Clone or download** this repository.
2. **Install dependencies**:
   ```bash
   pip install pandas pillow

    Run the program:

    python main_gui.py

    Select your PRET project directory (HeartGold/SoulSilver).

    Edit encounters and save them into profiles.

    Export changes to CSV whenever you want.

📜 License

This project is licensed under the MIT License — see the LICENSE file for details.
📬 Contact

Author: Rocket.Giovanni.Boss
📧 Email: rocket.giovanni.boss@gmail.com
💬 Discord: rocket.giovanni.boss

🕹 Have fun editing your Pokémon encounters!

© 2025 — Rocket.Giovanni.Boss
