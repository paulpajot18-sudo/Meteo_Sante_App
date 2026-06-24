import sys
import os
import json
import customtkinter as ctk
from tkinter import messagebox
from PIL import Image

class WeatherApp(ctk.CTk):
    def __init__(self, weather_service):
        super().__init__()
        self.weather_service = weather_service
        
        # --- Initialisation des variables de l'application ---
        self.title("Observatoire Météo & Santé")
        self.geometry("700x750")
        self.liters_drunk = 0.0
        self.current_goal = 1.50
        
        # --- Définition des thèmes requis par setup_ui ---
        self.weather_themes = {
            "default": ("#1e293b", "#0f172a", "#f8fafc")
        }
        
        # --- Configuration du stockage dans AppData (évite les bugs de droits d'écriture) ---
        appdata_dir = os.path.join(os.environ.get("LOCALAPPDATA", os.path.expanduser("~")), "MeteoSanteApp")
        os.makedirs(appdata_dir, exist_ok=True) 
        self.config_file = os.path.join(appdata_dir, "config.json")
        
        self.load_config()
        
        # --- Construction de l'interface graphique ---
        self.setup_ui()
        
        # --- Lancement automatique de la météo pour la dernière ville au démarrage ---
        self.after(100, self.refresh_weather)

    def load_config(self):
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, "r") as f:
                    self.config = json.load(f)
            except Exception:
                self.config = {"last_city": "Paris", "unit": "celsius"}
        else:
            self.config = {"last_city": "Paris", "unit": "celsius"}

    def save_config(self):
        try:
            with open(self.config_file, "w") as f:
                json.dump(self.config, f, indent=4)
        except Exception as e:
            print(f"Impossible de sauvegarder la configuration : {e}")

    def load_real_image(self, filename, size=(150, 150)):
        """Système d'injection d'images compatible PyInstaller."""
        try:
            if hasattr(sys, '_MEIPASS'):
                base_path = sys._MEIPASS
            else:
                base_path = os.path.abspath(".")

            full_path = os.path.join(base_path, filename)

            if os.path.exists(full_path):
                return ctk.CTkImage(light_image=Image.open(full_path), dark_image=Image.open(full_path), size=size)
        except Exception as e:
            print(f"Erreur de chargement d'image : {e}")
        return None

    def update_water_visuals(self):
        """Met à jour l'état de l'écosystème de la plante en temps réel."""
        ratio = self.liters_drunk / self.current_goal
        self.water_progress.set(min(1.0, ratio))
        self.lbl_progress_pct.configure(text=f"{int(min(1.0, ratio) * 100)} % de l'objectif quotidien complété")
        self.lbl_water_status.configure(text=f"Volume absorbé : {self.liters_drunk:.2f} L  /  Cible Médicale : {self.current_goal:.2f} L")

        # Choix de l'image de la plante selon l'avancement
        if ratio < 0.35:
            img = self.load_real_image("plante_soif.png")
            status_txt = "État : Écosystème déshydraté"
        elif ratio < 0.85:
            img = self.load_real_image("plante_ok.png")
            status_txt = "État : Écosystème équilibré"
        else:
            img = self.load_real_image("plante_fleurie.png")
            status_txt = "État : Écosystème florissant !"

        if img:
            self.lbl_plant_img.configure(image=img, text="")
        else:
            self.lbl_plant_img.configure(image=None, text="🪴\n[Image HD Non Trouvée]")
        
        self.lbl_plant_status.configure(text=status_txt)

    def add_water(self):
        """Enregistrement instantané du verre d'eau."""
        if self.liters_drunk < self.current_goal:
            self.liters_drunk = min(self.current_goal, self.liters_drunk + 0.25)
            self.update_water_visuals()
            if self.liters_drunk >= self.current_goal:
                messagebox.showinfo("Santé", "Objectif de sécurité hydratation atteint pour aujourd'hui. Parfait.")

    def reset_water(self):
        self.liters_drunk = 0.0
        self.update_water_visuals()

    def setup_ui(self):
        bg_col, card_col, txt_col = self.weather_themes["default"]
        self.configure(fg_color=bg_col)

        # --- BARRE DE COMMANDE HAUTE ---
        self.top_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.top_frame.pack(pady=15, fill="x", padx=40)
        
        self.search_entry = ctk.CTkEntry(self.top_frame, placeholder_text="Saisir une localité...", width=450, height=45, font=("Helvetica", 15), corner_radius=12)
        self.search_entry.pack(side="left", padx=(0, 15))
        self.search_entry.insert(0, self.config.get("last_city", "Paris"))
        self.search_entry.bind("<Return>", lambda event: self.refresh_weather())
        
        self.search_btn = ctk.CTkButton(self.top_frame, text="Synchroniser Météo", font=("Helvetica", 14, "bold"), height=45, corner_radius=12, fg_color="#3b82f6", hover_color="#2563eb", command=self.refresh_weather)
        self.search_btn.pack(side="left")

        # --- MODULE CÉLESTE (AFFICHAGE PRINCIPAL) ---
        self.main_card = ctk.CTkFrame(self, corner_radius=20, fg_color=card_col)
        self.main_card.pack(fill="x", padx=40, pady=10)

        self.lbl_city = ctk.CTkLabel(self.main_card, text="Initialisation...", font=("Helvetica", 32, "bold"), text_color=txt_col)
        self.lbl_city.pack(pady=(15, 5))

        self.info_frame = ctk.CTkFrame(self.main_card, fg_color="transparent")
        self.info_frame.pack(pady=5)

        self.lbl_icon = ctk.CTkLabel(self.info_frame, text="✨", font=("Helvetica", 85))
        self.lbl_icon.pack(side="left", padx=30)

        self.lbl_temp = ctk.CTkLabel(self.info_frame, text="--°C", font=("Helvetica", 75, "bold"), text_color=txt_col)
        self.lbl_temp.pack(side="left", padx=30)

        self.lbl_cond = ctk.CTkLabel(self.main_card, text="Analyse environnementale en cours...", font=("Helvetica", 18, "italic"), text_color="#94a3b8")
        self.lbl_cond.pack(pady=(5, 15))

        # --- MODULE MÉDICAL ---
        self.water_card = ctk.CTkFrame(self, corner_radius=20, fg_color=card_col, border_width=1, border_color="#334155")
        self.water_card.pack(fill="x", padx=40, pady=10)

        self.water_left = ctk.CTkFrame(self.water_card, fg_color="transparent")
        self.water_left.pack(side="left", padx=25, pady=20, fill="both", expand=True)

        self.lbl_water_title = ctk.CTkLabel(self.water_left, text="🩺 Régulateur Hydrique Protecteur", font=("Helvetica", 18, "bold"), text_color=txt_col)
        self.lbl_water_title.pack(anchor="w")

        self.lbl_water_advice = ctk.CTkLabel(self.water_left, text="", font=("Helvetica", 13), wraplength=440, justify="left", text_color="#cbd5e1")
        self.lbl_water_advice.pack(anchor="w", pady=8)

        self.lbl_water_status = ctk.CTkLabel(self.water_left, text="", font=("Helvetica", 16, "bold"), text_color=txt_col)
        self.lbl_water_status.pack(anchor="w", pady=4)

        self.water_progress = ctk.CTkProgressBar(self.water_left, width=440, height=16, progress_color="#0ea5e9", fg_color="#1e293b")
        self.water_progress.pack(anchor="w", pady=6)
        self.water_progress.set(0.0)

        self.lbl_progress_pct = ctk.CTkLabel(self.water_left, text="0 %", font=("Helvetica", 12, "italic"), text_color="#64748b")
        self.lbl_progress_pct.pack(anchor="w")

        self.action_frame = ctk.CTkFrame(self.water_left, fg_color="transparent")
        self.action_frame.pack(anchor="w", pady=(15, 0))

        self.btn_add_water = ctk.CTkButton(self.action_frame, text="🥛 Confirmer Consommation (0.25 L)", font=("Helvetica", 14, "bold"), fg_color="#0ea5e9", text_color="white", hover_color="#0284c7", width=260, height=50, corner_radius=12, command=self.add_water)
        self.btn_add_water.pack(side="left", padx=(0, 15))

        self.btn_reset_water = ctk.CTkButton(self.action_frame, text="🔄 Reset", font=("Helvetica", 12), fg_color="#475569", text_color="white", hover_color="#334155", width=100, height=50, corner_radius=12, command=self.reset_water)
        self.btn_reset_water.pack(side="left")

        self.water_right = ctk.CTkFrame(self.water_card, fg_color="transparent")
        self.water_right.pack(side="right", padx=25, pady=20, fill="both")

        self.lbl_plant_img = ctk.CTkLabel(self.water_right, text="", width=150, height=150)
        self.lbl_plant_img.pack(pady=5)

        self.lbl_plant_status = ctk.CTkLabel(self.water_right, text="Ajustement...", font=("Helvetica", 12, "bold"), text_color="#94a3b8", width=160, wraplength=150)
        self.lbl_plant_status.pack()

        # --- PANEL PREVISIONNEL (5 JOURS) ---
        self.forecast_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.forecast_frame.pack(fill="x", padx=40, pady=10)
        self.forecast_frame.columnconfigure((0, 1, 2, 3, 4), weight=1)

        self.forecast_widgets = []
        for i in range(5):
            card = ctk.CTkFrame(self.forecast_frame, corner_radius=15, fg_color=card_col, border_width=1, border_color="#334155")
            card.grid(row=0, column=i, padx=5, sticky="nsew")
            
            lbl_day = ctk.CTkLabel(card, text="---", font=("Helvetica", 14, "bold"), text_color="white")
            lbl_day.pack(pady=6)
            lbl_icon = ctk.CTkLabel(card, text="❓", font=("Helvetica", 30))
            lbl_icon.pack()
            lbl_temp = ctk.CTkLabel(card, text="-- / --", font=("Helvetica", 13, "bold"), text_color="white")
            lbl_temp.pack(pady=6)
            lbl_rain = ctk.CTkLabel(card, text="🌧️ --%", font=("Helvetica", 11), text_color="#38bdf8")
            lbl_rain.pack(pady=(0, 10))
            
            self.forecast_widgets.append({"day": lbl_day, "icon": lbl_icon, "temp": lbl_temp, "rain": lbl_rain})

        self.lbl_update = ctk.CTkLabel(self, text="Calculateur d'Analyse : Connecté", font=("Helvetica", 11, "italic"), text_color="#475569")
        self.lbl_update.pack(side="bottom", pady=15)

    def refresh_weather(self):
        city = self.search_entry.get().strip()
        if not city: return

        data = self.weather_service.get_weather_data(city)
        if data:
            self.lbl_city.configure(text=data["city"])
            self.lbl_temp.configure(text=f"{data['temp']}°C")
            self.lbl_cond.configure(text=f"{data['condition']} • Humidité: {data['humidity']}% • Vent: {data['wind']} km/h\n🌅 Lever: {data['sunrise']} - 🌇 Coucher: {data['sunset']}")
            self.lbl_icon.configure(text=data["icon"])

            if data["temp"] >= 26:
                self.current_goal = 2.00  
                self.lbl_water_advice.configure(
                    text="⚠️ SEUIL DE SÉCURITÉ THERMIQUE CRITIQUE : Température élevée détectée. L'objectif d'hydratation passe à 2.0 Litres pour limiter le stress cellulaire lié à la chaleur.", 
                    text_color="#facc15"
                )
            else:
                self.current_goal = 1.50
                self.lbl_water_advice.configure(
                    text="📋 PRÉCONISATION STANDARD : Rythme de croisière gériatrique à 1.5 Litre. Consommer un verre régulièrement permet d'entretenir les facultés intellectuelles et musculaires.", 
                    text_color="#cbd5e1"
                )

            for i, day_data in enumerate(data["forecast"]):
                self.forecast_widgets[i]["day"].configure(text=day_data["day"])
                self.forecast_widgets[i]["icon"].configure(text=day_data["icon"])
                self.forecast_widgets[i]["temp"].configure(text=f"{day_data['max']}° | {day_data['min']}°")
                self.forecast_widgets[i]["rain"].configure(text=f"🌧️ {day_data['rain_prob']}%")

            self.lbl_update.configure(text=f"Dernier diagnostic global : {data['update_time']}")
            self.update_water_visuals()
            
            self.config["last_city"] = city
            self.save_config()
        else:
            messagebox.showerror("Erreur Météo", f"Impossible de localiser '{city}'. Vérifiez l'orthographe ou la connexion.")

if __name__ == "__main__":
    from weather import WeatherService
    app = WeatherApp(WeatherService())
    app.mainloop()