

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import subprocess
from ping3 import ping
import statistics


# Scan WiFi Networks

def scan_wifi():
    try:
        output = subprocess.check_output(
            ["netsh", "wlan", "show", "networks"],
            encoding="utf-8",
            errors="ignore"
        )
    except:
        return []

    networks = []
    current = None

    for line in output.split("\n"):
        line = line.strip()

        if line.startswith("SSID") and ":" in line:
            if current:
                networks.append(current)
            current = {"SSID": line.split(":", 1)[1].strip()}

        elif current and "Authentication" in line:
            current["Security"] = line.split(":", 1)[1].strip()

    if current:
        networks.append(current)

    return networks



# Network Quality Test
-
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



# Improvement Suggestions

def suggestions(avg, loss, security):
    tips = []

    if loss > 2:
        tips.append("Reduce number of connected devices")
        tips.append("Change WiFi channel to avoid congestion")

    if avg and avg > 80:
        tips.append("Move closer to the router")
        tips.append("Restart router to clear congestion")

    if security and "WPA3" not in security:
        tips.append("Upgrade WiFi security to WPA3")

    if not tips:
        tips.append("Your WiFi setup is well optimized")

    return tips



# GUI FUNCTIONS

def run_scan():
    tree.delete(*tree.get_children())
    nets = scan_wifi()

    if not nets:
        messagebox.showerror("Error", "Unable to scan WiFi networks")
        return

    for n in nets:
        tree.insert("", "end", values=(
            n.get("SSID", ""),
            n.get("Security", "")
        ))


def run_test():
    selected = tree.focus()

    if not selected:
        messagebox.showwarning("Select Network", "Please select a WiFi network")
        return

    ssid, security = tree.item(selected)["values"]

    output.delete(1.0, tk.END)
    avg, loss = test_network()
    rating, rating_msg = get_rating(avg, loss)

    output.insert(tk.END, f"Selected Network : {ssid}\n")
    output.insert(tk.END, "-" * 45 + "\n")

    if avg:
        output.insert(tk.END, f"Average Latency : {round(avg,2)} ms\n")
    else:
        output.insert(tk.END, "Average Latency : Blocked / No Reply\n")

    output.insert(tk.END, f"Packet Loss     : {round(loss,2)} %\n")
    output.insert(tk.END, f"Security Type   : {security}\n\n")

    output.insert(tk.END, f"Network Rating  : {rating}\n")
    output.insert(tk.END, f"Remarks         : {rating_msg}\n\n")

    output.insert(tk.END, "Improvement Suggestions:\n")
    output.insert(tk.END, "-" * 30 + "\n")
    for t in suggestions(avg, loss, security):
        output.insert(tk.END, f"• {t}\n")



# GUI SETUP

root = tk.Tk()
root.title("WiFi Analyzer")
root.geometry("860x560")
root.configure(bg="#f4f6f8")

style = ttk.Style()
style.theme_use("clam")
style.configure("Header.TLabel", font=("Segoe UI", 20, "bold"), foreground="#1f4fd8")
style.configure("TButton", font=("Segoe UI", 11, "bold"), padding=6)
style.configure("Treeview", font=("Segoe UI", 10), rowheight=28)
style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"))

ttk.Label(root, text="WiFi Analyzer", style="Header.TLabel").pack(pady=10)
ttk.Label(root, text="Basic WiFi Quality and Security Analysis (Windows)").pack()

card = tk.Frame(root, bg="white")
card.pack(padx=20, pady=15, fill="both", expand=True)

btn_frame = tk.Frame(card, bg="white")
btn_frame.pack(pady=10)

ttk.Button(btn_frame, text="Scan WiFi Networks", command=run_scan).pack(side="left", padx=10)
ttk.Button(btn_frame, text="Test Selected Network", command=run_test).pack(side="left", padx=10)

columns = ("SSID", "Security")
tree = ttk.Treeview(card, columns=columns, show="headings", height=8)
for c in columns:
    tree.heading(c, text=c)
    tree.column(c, width=350, anchor="center")
tree.pack(padx=15, pady=10)

output = scrolledtext.ScrolledText(
    card,
    height=9,
    font=("Consolas", 11),
    bg="#f9fafb",
    relief="flat"
)
output.pack(fill="both", padx=15, pady=10)

root.mainloop()

