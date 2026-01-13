# =====================================
# CONNECTED WIFI ANALYZER - WINDOWS

# =====================================

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import subprocess
from ping3 import ping
import statistics

# -------------------------
# Get Connected WiFi Info
# -------------------------
def get_connected_wifi():
    try:
        output = subprocess.check_output(
            ["netsh", "wlan", "show", "interfaces"],
            encoding="utf-8",
            errors="ignore"
        )
    except:
        return None, None

    ssid = None
    security = None

    for line in output.split("\n"):
        if "SSID" in line and ":" in line:
            ssid = line.split(":", 1)[1].strip()
        if "Authentication" in line:
            security = line.split(":", 1)[1].strip()

    return ssid, security


# -------------------------
# Network Quality Test
# -------------------------
def test_network():
    delays = []
    lost = 0

    for _ in range(5):
        try:
            d = ping("8.8.8.8", timeout=2)
            if d:
                delays.append(d * 1000)
            else:
                lost += 1
        except:
            lost += 1

    avg = statistics.mean(delays) if delays else None
    loss = (lost / 5) * 100
    return avg, loss


# -------------------------
# Rating Logic
# -------------------------
def get_rating(avg, loss):
    if avg is None or loss > 10:
        return "⭐ Poor", "Network is unstable"
    if avg < 40 and loss == 0:
        return "⭐⭐⭐⭐ Excellent", "Very stable connection"
    if avg < 80 and loss <= 2:
        return "⭐⭐⭐ Good", "Good for browsing and streaming"
    return "⭐⭐ Fair", "May face issues in video calls or gaming"


# -------------------------
# Suggestions
# -------------------------
def suggestions(avg, loss, security):
    tips = []

    if loss > 2:
        tips.append("Reduce number of connected devices")
        tips.append("Restart router to reduce congestion")

    if avg and avg > 80:
        tips.append("Move closer to the router")
        tips.append("Switch to 5 GHz WiFi band if available")

    if security and "WPA3" not in security:
        tips.append("Upgrade WiFi security to WPA3")

    if not tips:
        tips.append("Your WiFi setup is well optimized")

    return tips


# -------------------------
# GUI ACTION
# -------------------------
def run_test():
    ssid, security = get_connected_wifi()

    if not ssid:
        messagebox.showerror("Not Connected", "No WiFi network connected")
        return

    output.delete(1.0, tk.END)
    avg, loss = test_network()
    rating, remark = get_rating(avg, loss)

    output.insert(tk.END, f"Connected Network : {ssid}\n")
    output.insert(tk.END, "-" * 45 + "\n")

    if avg:
        output.insert(tk.END, f"Average Latency : {round(avg,2)} ms\n")
    else:
        output.insert(tk.END, "Average Latency : Blocked / No Reply\n")

    output.insert(tk.END, f"Packet Loss     : {round(loss,2)} %\n")
    output.insert(tk.END, f"Security Type   : {security}\n\n")

    output.insert(tk.END, f"Network Rating  : {rating}\n")
    output.insert(tk.END, f"Remarks         : {remark}\n\n")

    output.insert(tk.END, "Improvement Suggestions:\n")
    output.insert(tk.END, "-" * 30 + "\n")
    for tip in suggestions(avg, loss, security):
        output.insert(tk.END, f"• {tip}\n")


# -------------------------
# GUI SETUP
# -------------------------
root = tk.Tk()
root.title("WiFi Analyzer")
root.geometry("760x500")
root.configure(bg="#f4f6f8")

style = ttk.Style()
style.theme_use("clam")
style.configure("Header.TLabel", font=("Segoe UI", 20, "bold"), foreground="#1f4fd8")
style.configure("TButton", font=("Segoe UI", 12, "bold"), padding=8)

ttk.Label(root, text="WiFi Analyzer", style="Header.TLabel").pack(pady=12)
ttk.Label(
    root,
    text="Connected Network Quality Analysis (Windows)",
    foreground="#555555"
).pack()

card = tk.Frame(root, bg="white")
card.pack(padx=25, pady=20, fill="both", expand=True)

ttk.Button(
    card,
    text="Test Connected Network",
    command=run_test
).pack(pady=15)

output = scrolledtext.ScrolledText(
    card,
    height=12,
    font=("Consolas", 11),
    bg="#f9fafb",
    relief="flat"
)
output.pack(fill="both", padx=15, pady=10)

root.mainloop()
