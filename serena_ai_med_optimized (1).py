import sys
import os
import random
import logging
from datetime import datetime
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QLabel, QVBoxLayout, QWidget, QTextEdit
)
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QFont

# Minimal logging setup
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")

# Simulated medical data
medical_data = {
    "heart_rate": 72,
    "blood_pressure": "120/80",
    "oxygen_saturation": 98,
    "alerts": "None",
}
vitals_history = []

# Patient profile
patient_profile = {
    "condition": "Diabetes",
    "medication_schedule": {"Mounjaro": "0.5 mg weekly"}
}

# Medical knowledge base
MEDICAL_KNOWLEDGE_BASE = {
    "what is mounjaro": "Mounjaro is a GIP/GLP-1 receptor agonist for Type 2 Diabetes. Dosage: 2.5-15 mg weekly.",
    "patient education on diabetes": "Manage diabetes with Mounjaro, monitor glucose, and follow a low-GI diet.",
}

# Base directory for minimal file operations
try:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
except NameError:
    BASE_DIR = os.getcwd()  # Fallback to current working directory
AUDIT_LOG_PATH = os.path.join(BASE_DIR, "serena_audit_log.txt")

def simulate_medical_data():
    global medical_data, vitals_history
    medical_data["heart_rate"] = max(60, min(100, medical_data["heart_rate"] + random.uniform(-2, 2)))
    sys_bp = int(medical_data["blood_pressure"].split("/")[0]) + random.randint(-5, 5)
    dia_bp = int(medical_data["blood_pressure"].split("/")[1]) + random.randint(-3, 3)
    medical_data["blood_pressure"] = f"{max(90, min(140, sys_bp))}/{max(60, min(90, dia_bp))}"
    medical_data["oxygen_saturation"] = max(90, min(100, medical_data["oxygen_saturation"] + random.uniform(-1, 1)))
    alerts = []
    if medical_data["heart_rate"] > 90:
        alerts.append("High heart rate")
    if int(medical_data["blood_pressure"].split("/")[0]) > 130:
        alerts.append("High blood pressure")
    medical_data["alerts"] = ", ".join(alerts) if alerts else "None"
    vitals_history.append({
        "time": datetime.now().strftime("%H:%M:%S"),
        "heart_rate": medical_data["heart_rate"],
        "blood_pressure": medical_data["blood_pressure"],
        "oxygen_saturation": medical_data["oxygen_saturation"],
    })
    if len(vitals_history) > 5:  # Reduced history size
        vitals_history.pop(0)

def save_audit_log(command, response):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] Command: {command} | Response: {response}\n"
    try:
        with open(AUDIT_LOG_PATH, "a", encoding="utf-8") as f:
            f.write(log_entry)
    except Exception as e:
        logging.error(f"Failed to save audit log: {str(e)}")

def call_medical_api(command):
    for key in MEDICAL_KNOWLEDGE_BASE:
        if key in command.lower():
            return MEDICAL_KNOWLEDGE_BASE[key]
    return "Please ask a medical question, e.g., 'What is Mounjaro?'"

class SerenaAIMedWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Serena AI Med")
        self.setGeometry(100, 100, 400, 300)  # Smaller window size
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)

        self.font = QFont("Arial", 10)  # Smaller font size

        # Title label
        self.title_label = QLabel("Serena AI Med")
        self.title_label.setFont(self.font)
        self.main_layout.addWidget(self.title_label)

        # Medical data
        self.heart_rate_label = QLabel(f"Heart Rate: {medical_data['heart_rate']:.1f} bpm")
        self.heart_rate_label.setFont(self.font)
        self.main_layout.addWidget(self.heart_rate_label)

        self.bp_label = QLabel(f"BP: {medical_data['blood_pressure']} mmHg")
        self.bp_label.setFont(self.font)
        self.main_layout.addWidget(self.bp_label)

        self.oxygen_label = QLabel(f"SpO2: {medical_data['oxygen_saturation']:.1f}%")
        self.oxygen_label.setFont(self.font)
        self.main_layout.addWidget(self.oxygen_label)

        self.alerts_label = QLabel(f"Alerts: {medical_data['alerts']}")
        self.alerts_label.setFont(self.font)
        self.main_layout.addWidget(self.alerts_label)

        # Response
        self.response_label = QLabel("Ready for queries...")
        self.response_label.setFont(self.font)
        self.main_layout.addWidget(self.response_label)

        # History
        self.history_text = QTextEdit()
        self.history_text.setReadOnly(True)
        self.history_text.setFont(self.font)
        self.history_text.setFixedHeight(50)  # Smaller history box
        self.main_layout.addWidget(self.history_text)

        # Buttons
        self.patient_education_button = QPushButton("Patient Education")
        self.patient_education_button.clicked.connect(lambda: self.on_button_click("Patient Education", self.patient_education))
        self.main_layout.addWidget(self.patient_education_button)

        self.vitals_history_button = QPushButton("Vitals History")
        self.vitals_history_button.clicked.connect(lambda: self.on_button_click("Vitals History", self.show_vitals_history))
        self.main_layout.addWidget(self.vitals_history_button)

        # Timer for medical data updates (less frequent)
        self.data_timer = QTimer(self)
        self.data_timer.timeout.connect(self.update_medical_data)
        self.data_timer.start(60000)  # Update every 60 seconds

        self.append_history("Serena AI Med started.")
        logging.info("Initialization complete")

    def on_button_click(self, button_name, callback):
        self.response_label.setText(f"{button_name} activated.")
        self.append_history(f"{button_name} activated")
        if button_name in ["Vitals History", "Patient Education"]:
            simulate_medical_data()
            self.update_medical_data()
        callback()
        save_audit_log(button_name, f"{button_name} activated")

    def patient_education(self):
        command = f"patient education on {patient_profile['condition'].lower()}"
        response = call_medical_api(command)
        self.response_label.setText(response)
        self.append_history(f"Command: {command}\nResponse: {response}")
        save_audit_log(command, response)

    def show_vitals_history(self):
        if vitals_history:
            history_text = "Vitals History:\n" + "\n".join(
                f"{v['time']}: HR {v['heart_rate']:.1f}, BP {v['blood_pressure']}, SpO2 {v['oxygen_saturation']:.1f}%"
                for v in vitals_history
            )
            self.response_label.setText(history_text)
        else:
            self.response_label.setText("No vitals history available.")
        self.append_history("Viewed vitals history")
        save_audit_log("Vitals history", "Displayed vitals history")

    def update_medical_data(self):
        simulate_medical_data()
        self.heart_rate_label.setText(f"Heart Rate: {medical_data['heart_rate']:.1f} bpm")
        self.bp_label.setText(f"BP: {medical_data['blood_pressure']} mmHg")
        self.oxygen_label.setText(f"SpO2: {medical_data['oxygen_saturation']:.1f}%")
        self.alerts_label.setText(f"Alerts: {medical_data['alerts']}")
        logging.info("Medical data updated")

    def append_history(self, text):
        self.history_text.append(f"{datetime.now().strftime('%H:%M:%S')}: {text}\n")
        self.history_text.verticalScrollBar().setValue(self.history_text.verticalScrollBar().maximum())

if __name__ == "__main__":
    try:
        logging.info("Starting application")
        app = QApplication(sys.argv)
        window = SerenaAIMedWindow()
        window.show()
        sys.exit(app.exec_())
    except Exception as e:
        logging.error(f"Application error: {str(e)}")