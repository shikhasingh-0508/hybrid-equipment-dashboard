import sys
import requests
import numpy as np
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QTableWidget, QTableWidgetItem, QWidget, 
                             QFileDialog, QMessageBox, QLabel, QHeaderView)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QColor, QFont
import matplotlib
matplotlib.use('Qt5Agg') 
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

class SafetyApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("FOSSEE Industrial Safety Monitor - Ultra")
        self.resize(1400, 950)
        self.setStyleSheet("background-color: #11111b; color: #cdd6f4;")
        
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)

        # Top Header
        self.header = QLabel("SYSTEM ANALYTICS & SAFETY OVERVIEW")
        self.header.setAlignment(Qt.AlignCenter)
        self.header.setStyleSheet("font-size: 24px; font-weight: bold; color: #89b4fa; padding: 15px; background-color: #1e1e2e; border-radius: 10px;")
        self.main_layout.addWidget(self.header)

        # Upper Layout: Table and Upload
        self.top_row = QHBoxLayout()
        
        # Table Styling
        self.table = QTableWidget(4, 3)
        self.table.setHorizontalHeaderLabels(["Parameter", "Current Avg", "Peak Recorded"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setStyleSheet("""
            QTableWidget { background-color: #181825; gridline-color: #313244; border-radius: 10px; }
            QHeaderView::section { background-color: #313244; color: #89b4fa; font-weight: bold; }
        """)
        self.top_row.addWidget(self.table, 2)

        self.upload_btn = QPushButton("UPLOAD\nDATASET")
        self.upload_btn.setFixedSize(150, 100)
        self.upload_btn.setStyleSheet("background-color: #fab387; color: #11111b; font-weight: bold; border-radius: 15px;")
        self.upload_btn.clicked.connect(self.upload_csv)
        self.top_row.addWidget(self.upload_btn)
        
        self.main_layout.addLayout(self.top_row)

        # Lower Layout: Graphs
        self.graph_layout = QHBoxLayout()
        
        # 1. Equipment Bar Chart
        self.fig_bar = Figure(facecolor='#11111b', tight_layout=True)
        self.canvas_bar = FigureCanvas(self.fig_bar)
        self.graph_layout.addWidget(self.canvas_bar)

        # 2. Parameter Comparison Chart
        self.fig_comp = Figure(facecolor='#11111b', tight_layout=True)
        self.canvas_comp = FigureCanvas(self.fig_comp)
        self.graph_layout.addWidget(self.canvas_comp)

        self.main_layout.addLayout(self.graph_layout)

        self.timer = QTimer()
        self.timer.timeout.connect(self.play_animation)
        self.step = 0
        self.summary = {}

    def upload_csv(self):
        path, _ = QFileDialog.getOpenFileName(self, "Open CSV", "", "CSV Files (*.csv)")
        if path:
            try:
                files = {'file': open(path, 'rb')}
                res = requests.post('http://127.0.0.1:8000/api/upload/', files=files)
                if res.status_code == 200:
                    self.summary = res.json().get('summary')
                    self.update_table()
                    self.step = 0
                    self.timer.start(30)
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))

    def update_table(self):
        s = self.summary
        data = [
            ("Pressure (bar)", s['avg_pressure'], s['max_pressure'], 7.0),
            ("Temperature (°C)", s['avg_temperature'], s['max_temperature'], 120.0),
            ("Flowrate (m3/h)", s['avg_flowrate'], s['avg_flowrate'], 999),
            ("System Load", s['total_records'], s['total_records'], 500)
        ]
        
        for i, (name, avg, peak, limit) in enumerate(data):
            self.table.setItem(i, 0, QTableWidgetItem(name))
            
            avg_item = QTableWidgetItem(str(avg))
            peak_item = QTableWidgetItem(str(peak))
            
            if peak > limit:
                peak_item.setForeground(QColor("#f38ba8")) # Red for danger
                peak_item.setText(f"{peak} ⚠")
                
            self.table.setItem(i, 1, avg_item)
            self.table.setItem(i, 2, peak_item)

    def play_animation(self):
        self.step += 1
        self.draw_bar_chart()
        self.draw_comparison_chart()
        if self.step >= 30: self.timer.stop()

    def draw_bar_chart(self):
        self.fig_bar.clear()
        ax = self.fig_bar.add_subplot(111)
        ax.set_facecolor('#1e1e2e')
        dist = self.summary.get('type_dist', {})
        if dist:
            x = list(dist.keys())
            y = [v * (self.step / 30) for v in dist.values()]
            ax.bar(x, y, color='#89b4fa', alpha=0.8)
            ax.set_title("Units Per Category", color='white')
            ax.tick_params(colors='white')
        self.canvas_bar.draw()

    def draw_comparison_chart(self):
        self.fig_comp.clear()
        ax = self.fig_comp.add_subplot(111)
        ax.set_facecolor('#1e1e2e')
        
        # Normalizing data to show on one scale (0-100% of safety limit)
        params = ['Pressure', 'Temp', 'Flowrate']
        
        # Calculate % of limit reached
        p_pct = (self.summary['max_pressure'] / 7.0) * 100
        t_pct = (self.summary['max_temperature'] / 120.0) * 100
        f_pct = (self.summary['avg_flowrate'] / 50.0) * 100 # Assuming 50 is max flow
        
        values = [v * (self.step / 30) for v in [p_pct, t_pct, f_pct]]
        
        colors = ['#f38ba8' if v > 100 else '#a6e3a1' for v in [p_pct, t_pct, f_pct]]
        
        ax.barh(params, values, color=colors)
        ax.set_xlim(0, 120) # Show up to 120% to visualize overflow
        ax.axvline(100, color='#f38ba8', linestyle='--', label='Safety Limit')
        ax.set_title("Safety Limit Usage (%)", color='white')
        ax.tick_params(colors='white')
        ax.legend()
        
        self.canvas_comp.draw()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SafetyApp()
    window.show()
    sys.exit(app.exec_())