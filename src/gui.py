# =============================================================================
# LAND USE COMPATIBILITY ANALYZER - GUI
# Version 2.0 (using CustomTkinter for a modern look)
#
# Description:
# A modern graphical user interface for the land use compatibility analysis engine.
# This script expects the analysis engine to be located at 'src/analysis_engine.py'.
# =============================================================================

import customtkinter as ctk
from tkinter import filedialog, messagebox
import threading
import subprocess
import sys
import os
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Set the appearance mode and default color theme
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Glass Box Planner: Land Use Compatibility Analyzer")
        self.geometry("1200x850")
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        # --- Class Variables ---
        self.input_path = ctk.StringVar()
        self.gdb_layer = ctk.StringVar()
        self.matrix_path = ctk.StringVar()
        self.output_path = ctk.StringVar()
        self.land_use_col = ctk.StringVar()
        self.distance = ctk.StringVar(value="1")
        self.canvas1 = None
        self.canvas2 = None

        # --- Create Main Frames ---
        self.main_controls_frame = ctk.CTkFrame(self)
        self.main_controls_frame.grid(row=0, column=0, padx=20, pady=10, sticky="ew")
        self.main_controls_frame.grid_columnconfigure(0, weight=1)
        self.create_input_frame()
        self.create_parameters_frame()
        self.create_action_buttons()
        self.create_tab_view()

    def create_input_frame(self):
        input_frame = ctk.CTkFrame(self.main_controls_frame, corner_radius=10)
        input_frame.grid(row=0, column=0, padx=10, pady=(10, 5), sticky="ew")
        input_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(input_frame, text="Input Data Path:", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, padx=10, pady=10, sticky="w")
        ctk.CTkEntry(input_frame, textvariable=self.input_path).grid(row=0, column=1, padx=(0, 10), pady=10, sticky="ew")
        ctk.CTkButton(input_frame, text="Browse...", width=100, command=self.select_input).grid(row=0, column=2, padx=(0, 10), pady=10)

        ctk.CTkLabel(input_frame, text="Matrix CSV Path:", font=ctk.CTkFont(weight="bold")).grid(row=1, column=0, padx=10, pady=10, sticky="w")
        ctk.CTkEntry(input_frame, textvariable=self.matrix_path).grid(row=1, column=1, padx=(0, 10), pady=10, sticky="ew")
        ctk.CTkButton(input_frame, text="Browse...", width=100, command=self.select_matrix).grid(row=1, column=2, padx=(0, 10), pady=10)
        
        ctk.CTkLabel(input_frame, text="Output GeoPackage:", font=ctk.CTkFont(weight="bold")).grid(row=2, column=0, padx=10, pady=10, sticky="w")
        ctk.CTkEntry(input_frame, textvariable=self.output_path).grid(row=2, column=1, padx=(0, 10), pady=10, sticky="ew")
        ctk.CTkButton(input_frame, text="Save As...", width=100, command=self.select_output).grid(row=2, column=2, padx=(0, 10), pady=10)


    def create_parameters_frame(self):
        params_frame = ctk.CTkFrame(self.main_controls_frame, corner_radius=10)
        params_frame.grid(row=1, column=0,  padx=10, pady=5, sticky="ew")
        params_frame.grid_columnconfigure((1, 3), weight=1)

        ctk.CTkLabel(params_frame, text="Land Use Column Name:", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, padx=10, pady=10, sticky="w")
        ctk.CTkEntry(params_frame, textvariable=self.land_use_col).grid(row=0, column=1, padx=(0, 20), pady=10, sticky="ew")
        
        ctk.CTkLabel(params_frame, text="Adjacency Distance (m):", font=ctk.CTkFont(weight="bold")).grid(row=0, column=2, padx=10, pady=10, sticky="w")
        ctk.CTkEntry(params_frame, textvariable=self.distance).grid(row=0, column=3, padx=(0, 10), pady=10, sticky="ew")

        ctk.CTkLabel(params_frame, text="GDB Layer Name (if applicable):", font=ctk.CTkFont(weight="bold")).grid(row=1, column=0, padx=10, pady=10, sticky="w")
        ctk.CTkEntry(params_frame, textvariable=self.gdb_layer).grid(row=1, column=1, padx=(0, 20), pady=10, sticky="ew")


    def create_action_buttons(self):
        action_frame = ctk.CTkFrame(self.main_controls_frame, corner_radius=0, fg_color="transparent")
        action_frame.grid(row=2, column=0,  padx=10, pady=(5, 10), sticky="ew")
        action_frame.grid_columnconfigure(0, weight=1)
        
        self.run_button = ctk.CTkButton(action_frame, text="Run Analysis", font=ctk.CTkFont(size=14, weight="bold"), height=40, command=self.run_analysis_thread)
        self.run_button.grid(row=0, column=0, sticky="ew")
        

    def create_tab_view(self):
        """Creates the tab view for console and plots."""
        self.tab_view = ctk.CTkTabview(self, corner_radius=10)
        self.tab_view.grid(row=2, column=0, padx=20, pady=(0, 20), sticky="nsew")

        self.tab_view.add("Console")
        self.tab_view.add("Overall Summary")
        self.tab_view.add("Detailed Breakdown")
        
        self.console = ctk.CTkTextbox(self.tab_view.tab("Console"), wrap="word", font=("Courier New", 10))
        self.console.pack(expand=True, fill="both", padx=5, pady=5)
        self.console.configure(state="disabled")

        # Placeholder frames for plots
        self.plot_frame1 = ctk.CTkFrame(self.tab_view.tab("Overall Summary"), fg_color="transparent")
        self.plot_frame1.pack(expand=True, fill="both")
        self.plot_frame2 = ctk.CTkFrame(self.tab_view.tab("Detailed Breakdown"), fg_color="transparent")
        self.plot_frame2.pack(expand=True, fill="both")

    def update_visuals(self, output_gpkg_path):
        """Reads CSVs and generates matplotlib plots in the GUI."""
        try:
            gpkg_path = Path(output_gpkg_path)
            base = gpkg_path.stem
            overall_csv = gpkg_path.parent / f"{base}_overall_summary.csv"
            detailed_csv = gpkg_path.parent / f"{base}_detailed_breakdown.csv"

            if not overall_csv.exists() or not detailed_csv.exists():
                messagebox.showwarning("Warning", "Summary CSV files not found. Cannot generate plots.")
                return

            # --- Clear previous plots if they exist ---
            if self.canvas1: self.canvas1.get_tk_widget().destroy()
            if self.canvas2: self.canvas2.get_tk_widget().destroy()
            plt.close('all') # Close all previous matplotlib figures

            # --- Plot 1: Overall Summary ---
            df_overall = pd.read_csv(overall_csv)
            fig1, ax1 = plt.subplots(figsize=(10, 6), dpi=100)
            bars = ax1.bar(df_overall['compatibility_score'], df_overall['parcel_count'], color="#3B8ED0")
            ax1.set_title('Overall Parcel Count by Compatibility Score', fontsize=16)
            ax1.set_xlabel('Compatibility Score (1=Incompatible, 5=Compatible)', fontsize=12)
            ax1.set_ylabel('Number of Parcels', fontsize=12)
            ax1.set_xticks(range(1, 6))
            for bar in bars:
                yval = bar.get_height()
                ax1.text(bar.get_x() + bar.get_width()/2.0, yval, int(yval), va='bottom', ha='center') # va: vertical alignment
            fig1.tight_layout()

            self.canvas1 = FigureCanvasTkAgg(fig1, master=self.plot_frame1)
            self.canvas1.draw()
            self.canvas1.get_tk_widget().pack(expand=True, fill="both", padx=10, pady=10)

            # --- Plot 2: Detailed Breakdown ---
            df_detailed = pd.read_csv(detailed_csv, index_col=0)
            df_detailed = df_detailed.drop(columns=['total_parcels'])
            fig2, ax2 = plt.subplots(figsize=(14, 8), dpi=100)
            df_detailed.plot(kind='bar', stacked=True, ax=ax2, colormap='viridis')
            ax2.set_title('Parcel Count by Land Use and Compatibility Score', fontsize=16)
            ax2.set_xlabel('Land Use Type', fontsize=12)
            ax2.set_ylabel('Number of Parcels', fontsize=12)
            ax2.tick_params(axis='x', labelrotation=45)
            ax2.legend(title='Compatibility Score')
            fig2.tight_layout()

            self.canvas2 = FigureCanvasTkAgg(fig2, master=self.plot_frame2)
            self.canvas2.draw()
            self.canvas2.get_tk_widget().pack(expand=True, fill="both", padx=10, pady=10)

        except Exception as e:
            messagebox.showerror("Visualization Error", f"Could not generate plots: {e}")

    # --- (Backend and Threading Functions remain the same) ---
    def select_input(self):
        path = filedialog.askopenfilename(
            title="Select Input GIS Data",
            filetypes=[("Supported Files", "*.shp *.gpkg *.gdb"), ("Shapefile", "*.shp"), ("GeoPackage", "*.gpkg"), ("File Geodatabase", "*.gdb")]
        )
        if path: self.input_path.set(path)

    def select_matrix(self):
        path = filedialog.askopenfilename(title="Select Matrix CSV File", filetypes=[("CSV Files", "*.csv")])
        if path: self.matrix_path.set(path)

    def select_output(self):
        path = filedialog.asksaveasfilename(title="Save Output As", defaultextension=".gpkg", filetypes=[("GeoPackage", "*.gpkg")])
        if path: self.output_path.set(path)

    def write_config(self):
        """Validate fields and return a CLI-friendly config dict for the engine."""
        # --- Crucial Validation Step ---
        if not all([self.input_path.get(), self.matrix_path.get(), self.output_path.get(), self.land_use_col.get()]):
            messagebox.showerror("Missing Information", "Please fill in all path and column name fields before running the analysis.")
            return None

        # Build CLI-friendly values
        parcels = self.input_path.get()
        matrix = self.matrix_path.get()
        output_gp = self.output_path.get()
        try:
            adjacency = float(self.distance.get())
        except Exception:
            messagebox.showerror("Invalid Value", "Adjacency distance must be a number.")
            return None

        output_dir = str(Path(output_gp).parent)
        base_name = Path(output_gp).stem

        config = {
            "parcels": parcels,
            "matrix": matrix,
            "output_dir": output_dir,
            "base_name": base_name,
            "land_use_col": self.land_use_col.get(),
            "adjacency_distance": adjacency,
        }
        return config

    def run_analysis_thread(self):
        config = self.write_config()
        if not config:
            return # Stop if validation failed

        self.run_button.configure(state="disabled", text="Analysis in Progress...")
        self.console.configure(state="normal")
        self.console.delete("1.0", ctk.END)
        self.console.insert(ctk.END, "--- Configuration Sent to Engine ---\n\n")
        self.console.configure(state="disabled")

        thread = threading.Thread(target=self.execute_script, args=(config,))
        thread.daemon = True
        thread.start()

    def execute_script(self, config):
        engine_path = "src/analysis_engine.py"
        output_file_for_plots = str(Path(config["output_dir"]) / f"{config['base_name']}.gpkg")
        try:
            parcels = config["parcels"]
            matrix = config["matrix"]
            output_dir = config["output_dir"]
            base_name = config["base_name"]
            land_use = config["land_use_col"]
            adjacency = str(config["adjacency_distance"])

            cmd = [
                sys.executable,
                engine_path,
                "--parcels", parcels,
                "--matrix", matrix,
                "--output_dir", output_dir,
                "--base_name", base_name,
                "--land_use_col", land_use,
                "--adjacency_distance", adjacency,
            ]

            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding='utf-8',
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            )

            # Stream output to the GUI console
            for line in iter(process.stdout.readline, ''):
                self.console.configure(state="normal")
                self.console.insert(ctk.END, line)
                self.console.see(ctk.END)
                self.console.configure(state="disabled")
                self.update_idletasks()

            process.stdout.close()
            return_code = process.wait()

            if return_code == 0:
                messagebox.showinfo("Success", "Analysis completed successfully!")
                # Schedule plot update on the main thread
                self.after(0, self.update_visuals, output_file_for_plots)
            else:
                messagebox.showerror("Error", "An error occurred during analysis. Check the console for details.")

        except Exception as e:
            messagebox.showerror("Fatal Error", f"Failed to run analysis: {e}")
        finally:
            self.run_button.configure(state="normal", text="Run Analysis")


if __name__ == "__main__":
    app = App()
    app.mainloop()