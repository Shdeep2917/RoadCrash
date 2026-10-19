"""Road Accident Prediction System - beginner portfolio project.

Libraries: NumPy, Pandas, Matplotlib, Scikit-learn, Tkinter.
Input: Road_Crashes_Data(3).xlsx (select it with Browse if it is elsewhere).
Install: pip install numpy pandas matplotlib scikit-learn openpyxl
Run: python Road_Accident_Prediction.py

Note: the workbook contains only 10 annual rows for the main statistics sheet.
This project is for learning and portfolio demonstration; predictions are trend
estimates, not reliable operational forecasts.
"""
from pathlib import Path
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

APP_TITLE = "Road Accident Prediction System"
DEFAULT_FILE = "Road_Crashes_Data.xlsx"
TARGETS = ["Road Crashes", "Road Crash Fatalities", "Fatal Road Crashes"]


class RoadAccidentApp:
    def __init__(self, root):
        self.root = root
        self.root.title(APP_TITLE)
        self.root.geometry("1180x760")
        self.root.minsize(900, 600)
        self.path = Path(__file__).resolve().parent / DEFAULT_FILE
        self.sheets = {}
        self.stats = pd.DataFrame()
        self.model = None
        self.target = TARGETS[0]
        self.metrics = {}
        self._style()
        self._header()
        self._tabs()
        if self.path.exists():
            self.load_workbook(self.path)
        else:
            self.file_label.config(text="No workbook loaded. Click Browse Excel.")

    def _style(self):
        self.root.configure(bg="grey")
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure("TFrame", background="White")
        style.configure("TLabel", background="White", foreground="Black", font=("Segoe UI", 10))
        style.configure("Title.TLabel", font=("Segoe UI", 19, "bold"), foreground="Blue")
        style.configure("TButton", font=("Segoe UI", 10), padding=7)
        style.configure("Treeview", rowheight=26, font=("Segoe UI", 9))
        style.configure("Treeview.Heading", font=("Segoe UI", 9, "bold"))

    def _header(self):
        header = ttk.Frame(self.root, padding=(18, 14, 18, 8))
        header.pack(fill="x")
        ttk.Label(header, text=APP_TITLE, style="Title.TLabel").pack(anchor="w")
        ttk.Label(header, text="Delhi crash data • Excel analytics • Machine Learning trend estimates").pack(anchor="w", pady=(3, 10))
        line = ttk.Frame(header)
        line.pack(fill="x")
        self.file_label = ttk.Label(line, text="Loading workbook...")
        self.file_label.pack(side="left", fill="x", expand=True)
        ttk.Button(line, text="Browse Excel", command=self.browse).pack(side="right")

    def _tabs(self):
        self.tabs = ttk.Notebook(self.root)
        self.tabs.pack(fill="both", expand=True, padx=18, pady=(4, 16))
        self.dashboard = ttk.Frame(self.tabs, padding=14)
        self.predict_tab = ttk.Frame(self.tabs, padding=14)
        self.data_tab = ttk.Frame(self.tabs, padding=10)
        self.charts_tab = ttk.Frame(self.tabs, padding=10)
        self.model_tab = ttk.Frame(self.tabs, padding=14)
        for frame, title in [(self.dashboard, "Dashboard"), (self.predict_tab, "Predict"),
                             (self.data_tab, "Excel Data"), (self.charts_tab, "Charts"),
                             (self.model_tab, "Model & Metrics")]:
            self.tabs.add(frame, text=title)
        self._dashboard_ui()
        self._predict_ui()
        self._data_ui()
        self.chart_holder = ttk.Frame(self.charts_tab)
        self.chart_holder.pack(fill="both", expand=True)
        ttk.Label(self.model_tab, text="Model details and evaluation", style="Title.TLabel").pack(anchor="w")
        self.model_text = tk.Text(self.model_tab, wrap="word", font=("Consolas", 10), bg="white", relief="flat", padx=12, pady=12)
        self.model_text.pack(fill="both", expand=True, pady=(10, 0))
        self.model_text.configure(state="disabled")

    def _dashboard_ui(self):
        cards = ttk.Frame(self.dashboard)
        cards.pack(fill="x", pady=(0, 12))
        self.kpis = {}
        for title, key in [("Years recorded", "years"), ("Total crashes", "crashes"),
                           ("Total fatalities", "fatalities"), ("Latest year", "latest")]:
            card = tk.Frame(cards, bg="white", highlightbackground="light Grey", highlightthickness=1)
            card.pack(side="left", fill="both", expand=True, padx=(0, 9))
            tk.Label(card, text=title, bg="white", fg="Black", font=("Segoe UI", 9)).pack(anchor="w", padx=12, pady=(10, 2))
            value = tk.Label(card, text="—", bg="white", fg="Black", font=("Segoe UI", 17, "bold"))
            value.pack(anchor="w", padx=12, pady=(0, 10))
            self.kpis[key] = value
        self.summary = ttk.Label(self.dashboard, text="Load the Excel workbook to begin.", wraplength=1000, justify="left")
        self.summary.pack(anchor="w", fill="x", pady=(0, 8))
        self.dashboard_chart = ttk.Frame(self.dashboard)
        self.dashboard_chart.pack(fill="both", expand=True)

    def _predict_ui(self):
        ttk.Label(self.predict_tab, text="Estimate a yearly road-crash measure", style="Title.TLabel").pack(anchor="w")
        ttk.Label(self.predict_tab, text="The model learns a linear trend from the Year column and historical values.", wraplength=900).pack(anchor="w", pady=(4, 15))
        form = ttk.Frame(self.predict_tab)
        form.pack(anchor="w", fill="x")
        ttk.Label(form, text="Measure:").grid(row=0, column=0, sticky="w", padx=(0, 10), pady=7)
        self.target_var = tk.StringVar(value=TARGETS[0])
        self.target_box = ttk.Combobox(form, textvariable=self.target_var, values=TARGETS, state="readonly", width=30)
        self.target_box.grid(row=0, column=1, sticky="w", pady=7)
        self.target_box.bind("<<ComboboxSelected>>", lambda _e: self.train_model())
        ttk.Label(form, text="Year to estimate:").grid(row=1, column=0, sticky="w", padx=(0, 10), pady=7)
        self.year_var = tk.StringVar(value="2024")
        ttk.Entry(form, textvariable=self.year_var, width=33).grid(row=1, column=1, sticky="w", pady=7)
        ttk.Button(form, text="Predict", command=self.predict).grid(row=2, column=1, sticky="w", pady=10)
        self.prediction_card = tk.Frame(self.predict_tab, bg="white", highlightbackground="light Grey", highlightthickness=1)
        self.prediction_card.pack(fill="x", pady=(10, 12))
        self.prediction = tk.Label(self.prediction_card, text="Your prediction will appear here.", bg="white", fg="Black", font=("Segoe UI", 17, "bold"), justify="left", wraplength=900)
        self.prediction.pack(anchor="w", padx=16, pady=17)
        self.prediction_detail = ttk.Label(self.predict_tab, text="", wraplength=950, justify="left")
        self.prediction_detail.pack(anchor="w")
        ttk.Label(self.predict_tab, text="Limitations: the workbook has few annual observations. The model does not use weather, traffic volume, road location, or live conditions. Do not use this estimate for safety-critical decisions.", wraplength=950).pack(anchor="w", side="bottom", pady=(18, 0))

    def _data_ui(self):
        top = ttk.Frame(self.data_tab)
        top.pack(fill="x", pady=(0, 8))
        ttk.Label(top, text="Worksheet:").pack(side="left")
        self.sheet_var = tk.StringVar()
        self.sheet_box = ttk.Combobox(top, textvariable=self.sheet_var, state="readonly", width=45)
        self.sheet_box.pack(side="left", padx=8)
        self.sheet_box.bind("<<ComboboxSelected>>", lambda _e: self.show_sheet())
        self.row_label = ttk.Label(top, text="")
        self.row_label.pack(side="right")
        wrap = ttk.Frame(self.data_tab)
        wrap.pack(fill="both", expand=True)
        self.tree = ttk.Treeview(wrap, show="headings")
        ybar = ttk.Scrollbar(wrap, orient="vertical", command=self.tree.yview)
        xbar = ttk.Scrollbar(wrap, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=ybar.set, xscrollcommand=xbar.set)
        self.tree.grid(row=0, column=0, sticky="nsew")
        ybar.grid(row=0, column=1, sticky="ns")
        xbar.grid(row=1, column=0, sticky="ew")
        wrap.rowconfigure(0, weight=1)
        wrap.columnconfigure(0, weight=1)

    def browse(self):
        filename = filedialog.askopenfilename(title="Select Excel workbook", filetypes=[("Excel files", "*.xlsx *.xls"), ("All files", "*.*")])
        if filename:
            self.load_workbook(Path(filename))

    def load_workbook(self, path):
        try:
            raw = pd.read_excel(path, sheet_name=None)
            self.sheets = {str(name): df.copy() for name, df in raw.items() if df is not None and not df.empty}
            if not self.sheets:
                raise ValueError("No non-empty worksheets were found in this workbook.")
            found = None
            for name, df in self.sheets.items():
                df.columns = [str(c).strip() for c in df.columns]
                if {"Year", *TARGETS}.issubset(set(df.columns)):
                    found = (name, df)
                    break
            if found is None:
                raise ValueError("Could not find the annual statistics sheet. Required columns: Year, Road Crashes, Road Crash Fatalities, Fatal Road Crashes.")
            self.stats_sheet, self.stats = found
            for col in ["Year", *TARGETS]:
                self.stats[col] = pd.to_numeric(self.stats[col], errors="coerce")
            self.stats = self.stats.dropna(subset=["Year", *TARGETS]).sort_values("Year").reset_index(drop=True)
            if len(self.stats) < 3:
                raise ValueError("At least 3 valid yearly records are required for this demo model.")
            self.path = Path(path)
            self.file_label.config(text=f"Workbook: {self.path.name}")
            self.sheet_box["values"] = list(self.sheets.keys())
            self.sheet_var.set(self.stats_sheet)
            self.show_sheet()
            self.update_dashboard()
            self.draw_charts()
            self.train_model()
        except Exception as exc:
            messagebox.showerror("Workbook error", str(exc))

    def show_sheet(self):
        name = self.sheet_var.get()
        if name not in self.sheets:
            return
        df = self.sheets[name]
        cols = [str(c) for c in df.columns]
        self.tree.delete(*self.tree.get_children())
        self.tree["columns"] = cols
        for col in cols:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=max(100, min(230, len(col) * 8)), minwidth=85, stretch=True)
        clean = df.replace({np.nan: ""})
        for row in clean.head(1000).itertuples(index=False, name=None):
            self.tree.insert("", "end", values=[str(v)[:160] for v in row])
        self.row_label.config(text=f"{len(df)} rows • {len(cols)} columns; first 1,000 rows shown")

    def update_dashboard(self):
        df = self.stats
        self.kpis["years"].config(text=f"{len(df)}")
        self.kpis["crashes"].config(text=f"{int(df['Road Crashes'].sum()):,}")
        self.kpis["fatalities"].config(text=f"{int(df['Road Crash Fatalities'].sum()):,}")
        self.kpis["latest"].config(text=str(int(df["Year"].max())))
        self.summary.config(text=f"Source: {self.path.name}\nAnnual statistics worksheet: {self.stats_sheet}\nCoverage: {int(df['Year'].min())}–{int(df['Year'].max())}. Explore every non-empty worksheet in the Excel Data tab.")

    @staticmethod
    def clear_frame(frame):
        for widget in frame.winfo_children():
            widget.destroy()

    @staticmethod
    def embed_figure(parent, fig):
        canvas = FigureCanvasTkAgg(fig, master=parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)
        parent._canvas = canvas
        parent._figure = fig

    def draw_charts(self):
        self.clear_frame(self.dashboard_chart)
        self.clear_frame(self.chart_holder)
        df = self.stats
        fig, ax = plt.subplots(figsize=(9, 3.5), dpi=95)
        ax.plot(df["Year"], df["Road Crashes"], marker="o", label="Road Crashes")
        ax.plot(df["Year"], df["Road Crash Fatalities"], marker="s", label="Fatalities")
        ax.set_title("Road crashes and fatalities by year")
        ax.set_xlabel("Year")
        ax.set_ylabel("Recorded count")
        ax.grid(True, alpha=0.3)
        ax.legend()
        fig.tight_layout()
        self.embed_figure(self.dashboard_chart, fig)

        fig2, axes = plt.subplots(1, 2, figsize=(10, 4.5), dpi=95)
        axes[0].plot(df["Year"], df["Road Crashes"], marker="o")
        axes[0].set_title("Road crashes trend")
        axes[0].set_xlabel("Year")
        axes[0].set_ylabel("Crashes")
        axes[0].grid(True, alpha=0.3)
        axes[1].bar(df["Year"].astype(int).astype(str), df["Road Crash Fatalities"])
        axes[1].set_title("Fatalities by year")
        axes[1].set_xlabel("Year")
        axes[1].set_ylabel("Fatalities")
        axes[1].tick_params(axis="x", rotation=45)
        axes[1].grid(True, axis="y", alpha=0.3)
        fig2.tight_layout()
        self.embed_figure(self.chart_holder, fig2)

    def train_model(self):
        if self.stats.empty:
            return
        self.target = self.target_var.get() if hasattr(self, "target_var") else TARGETS[0]
        X = self.stats[["Year"]].astype(float)
        y = self.stats[self.target].astype(float)
        self.model = LinearRegression().fit(X, y)
        # Chronological holdout: train on earlier years and test on later years.
        split = max(2, int(len(self.stats) * 0.8))
        if len(self.stats) - split >= 1:
            test_model = LinearRegression().fit(X.iloc[:split], y.iloc[:split])
            pred = test_model.predict(X.iloc[split:])
            mae = mean_absolute_error(y.iloc[split:], pred)
            rmse = float(np.sqrt(mean_squared_error(y.iloc[split:], pred)))
            r2 = r2_score(y.iloc[split:], pred) if len(pred) >= 2 else None
        else:
            mae, rmse, r2 = np.nan, np.nan, None
        self.metrics = {"mae": mae, "rmse": rmse, "r2": r2}
        r2_text = f"{r2:.3f}" if r2 is not None else "Not available (fewer than 2 test rows)"
        text = (
            "MODEL: Linear Regression (scikit-learn)\n"
            f"Target: {self.target}\nFeature: Year\nRows used to fit final model: {len(X)}\n"
            f"Historical range: {int(X['Year'].min())}–{int(X['Year'].max())}\n\n"
            "Chronological holdout evaluation (later years held out)\n"
            f"MAE:  {mae:,.2f} counts\nRMSE: {rmse:,.2f} counts\nR²:   {r2_text}\n\n"
            "How it works\n1. Pandas reads the Excel workbook.\n"
            "2. NumPy/Pandas clean numeric columns.\n"
            "3. Scikit-learn learns the historical linear trend.\n"
            "4. A later-year holdout is used for a simple error check.\n"
            "5. Matplotlib displays the trends inside Tkinter.\n\n"
            "Important: there are very few annual records. Metrics can change greatly with one record, and R² is omitted when the test set has only one row. Use this as a beginner portfolio demonstration, not an operational safety forecast."
        )
        self.model_text.configure(state="normal")
        self.model_text.delete("1.0", "end")
        self.model_text.insert("1.0", text)
        self.model_text.configure(state="disabled")
        if hasattr(self, "prediction"):
            self.prediction.config(text="Choose a year and click Predict.")
            self.prediction_detail.config(text="")

    def predict(self):
        if self.model is None:
            messagebox.showwarning("Model not ready", "Load a valid workbook first.")
            return
        try:
            year = int(self.year_var.get().strip())
            if not 1900 <= year <= 2200:
                raise ValueError
        except ValueError:
            messagebox.showerror("Invalid year", "Enter a whole-number year between 1900 and 2200.")
            return
        estimate = max(0, int(round(float(self.model.predict(pd.DataFrame({"Year": [year]}))[0]))))
        self.prediction.config(text=f"Estimated {self.target.lower()} for {year}: {estimate:,}")
        lo, hi = int(self.stats["Year"].min()), int(self.stats["Year"].max())
        if year < lo or year > hi:
            note = f"{year} is outside the observed period ({lo}–{hi}); this is extrapolation and may be inaccurate."
        else:
            note = f"{year} is inside the observed period ({lo}–{hi}); the output is a model estimate, not the recorded value."
        self.prediction_detail.config(text=f"Model: Linear Regression | Input feature: Year = {year}\n{note}\nHoldout MAE: {self.metrics.get('mae', np.nan):,.2f} counts. The model does not account for weather, traffic volume, road design, or other causes.")


def main():
    root = tk.Tk()
    RoadAccidentApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
