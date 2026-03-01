"""
VAJRA-DRISHTHI - FIXED Clickable Cracks
Team Vishwakarmas - AMD Slingshot 2026

✅ Hover over cracks (cursor changes to hand)
✅ Click on any crack to open DETAILED INFO BLOCK
✅ Works for all cracks: C1, C2, C3... etc
"""

import cv2
import numpy as np
from PIL import Image, ImageTk
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from datetime import datetime
import os
import random

# ===========================================
# MODERN BUTTON CLASS
# ===========================================

class ModernButton(tk.Canvas):
    def __init__(self, parent, text, command, bg_color, hover_color, **kwargs):
        super().__init__(parent, highlightthickness=0, **kwargs)
        self.command = command
        self.bg_color = bg_color
        self.hover_color = hover_color
        
        self.width = kwargs.get('width', 200)
        self.height = kwargs.get('height', 50)
        self.create_rounded_rect(5, 5, self.width-5, self.height-5, 15, fill=bg_color, tags="button")
        self.create_text(self.width//2, self.height//2, text=text, fill='white', 
                        font=('Arial', 11, 'bold'), tags="text")
        
        self.tag_bind("button", "<Enter>", self.on_enter)
        self.tag_bind("button", "<Leave>", self.on_leave)
        self.tag_bind("button", "<Button-1>", self.on_click)
        self.tag_bind("text", "<Enter>", self.on_enter)
        self.tag_bind("text", "<Leave>", self.on_leave)
        self.tag_bind("text", "<Button-1>", self.on_click)
        
    def create_rounded_rect(self, x1, y1, x2, y2, radius, **kwargs):
        points = []
        for x, y in [(x1+radius, y1), (x2-radius, y1), (x2, y1), 
                     (x2, y1+radius), (x2, y2-radius), (x2, y2),
                     (x2-radius, y2), (x1+radius, y2), (x1, y2),
                     (x1, y2-radius), (x1, y1+radius), (x1, y1)]:
            points.extend([x, y])
        return self.create_polygon(points, smooth=True, **kwargs)
    
    def on_enter(self, event):
        self.itemconfig("button", fill=self.hover_color)
        
    def on_leave(self, event):
        self.itemconfig("button", fill=self.bg_color)
        
    def on_click(self, event):
        self.itemconfig("button", fill=self.bg_color)
        self.after(100, self.command)

# ===========================================
# CRACK INFO BLOCK - Opens when crack is clicked
# ===========================================

class CrackInfoBlock:
    """Popup block showing crack details when clicked"""
    
    def __init__(self, parent, crack_data):
        self.popup = tk.Toplevel(parent)
        self.popup.title(f"Crack {crack_data['display_id']} Details")
        self.popup.geometry("450x550")
        self.popup.configure(bg='#1a1a2a')
        self.popup.transient(parent)
        self.popup.grab_set()
        self.popup.resizable(False, False)
        
        # Center the popup
        self.center_popup()
        
        # Store crack data
        self.crack = crack_data
        
        # Create the info block
        self.create_info_block()
        
    def center_popup(self):
        self.popup.update_idletasks()
        x = (self.popup.winfo_screenwidth() - 450) // 2
        y = (self.popup.winfo_screenheight() - 550) // 2
        self.popup.geometry(f'450x550+{x}+{y}')
    
    def create_info_block(self):
        # ===========================================
        # HEADER with Crack ID
        # ===========================================
        header_frame = tk.Frame(self.popup, bg='#16213e', height=80)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)
        
        # Crack ID with large font
        tk.Label(
            header_frame,
            text=f"🔍 CRACK {self.crack['display_id']}",
            font=('Arial', 24, 'bold'),
            bg='#16213e',
            fg=self.get_severity_color(self.crack['severity'])
        ).pack(pady=(15,5))
        
        # Severity badge
        severity_frame = tk.Frame(header_frame, bg=self.get_severity_color(self.crack['severity']))
        severity_frame.pack(pady=5)
        
        tk.Label(
            severity_frame,
            text=f"  {self.crack['severity']}  ",
            font=('Arial', 12, 'bold'),
            bg=self.get_severity_color(self.crack['severity']),
            fg='white'
        ).pack()
        
        # ===========================================
        # CONTENT - Info blocks
        # ===========================================
        content = tk.Frame(self.popup, bg='#1a1a2a')
        content.pack(fill=tk.BOTH, expand=True, padx=20, pady=15)
        
        # Block 1: 📏 DIMENSIONS
        self.create_info_section(content, "📏 DIMENSIONS", [
            f"Width      : {self.crack['width_mm']} mm",
            f"Depth      : {self.crack.get('depth_mm', 'N/A')} mm",
            f"Area       : {self.crack['area']} pixels²",
            f"Volume     : {self.crack.get('volume_mm3', 0):.2f} mm³"
        ])
        
        # Block 2: 📍 LOCATION
        x, y, w, h = self.crack['bounds']
        self.create_info_section(content, "📍 LOCATION", [
            f"Position X : {x}",
            f"Position Y : {y}",
            f"Width      : {w} pixels",
            f"Height     : {h} pixels"
        ])
        
        # Block 3: ⚠️ SEVERITY INFO
        severity_info = self.get_severity_info(self.crack['severity'])
        self.create_info_section(content, "⚠️ SEVERITY INFO", severity_info)
        
        # Block 4: 🔍 ROOT CAUSE
        cause = self.analyze_cause(self.crack)
        self.create_info_section(content, "🔍 ROOT CAUSE", [
            f"Cause : {cause['cause']}",
            f"Details : {cause['description']}",
            f"Fix : {cause['fix']}"
        ])
        
        # Block 5: 🛠️ RECOMMENDATION
        risk = self.assess_risk(self.crack)
        self.create_info_section(content, "🛠️ RECOMMENDATION", [
            f"Risk Level : {risk['level']}",
            f"Action : {risk['action']}"
        ])
        
        # ===========================================
        # CLOSE BUTTON
        # ===========================================
        close_btn = tk.Button(
            self.popup,
            text="CLOSE",
            command=self.popup.destroy,
            bg='#ff4757',
            fg='white',
            font=('Arial', 12, 'bold'),
            width=15,
            height=2,
            bd=0,
            cursor='hand2'
        )
        close_btn.pack(pady=15)
        
        # Hover effect
        close_btn.bind("<Enter>", lambda e: close_btn.config(bg='#ff6b81'))
        close_btn.bind("<Leave>", lambda e: close_btn.config(bg='#ff4757'))
    
    def create_info_section(self, parent, title, lines):
        """Create a styled information section"""
        # Section frame
        section = tk.Frame(parent, bg='#16213e', relief=tk.RAISED, bd=1)
        section.pack(fill=tk.X, pady=5)
        
        # Title
        tk.Label(
            section,
            text=title,
            font=('Arial', 11, 'bold'),
            bg='#16213e',
            fg='#00a8ff'
        ).pack(anchor=tk.W, padx=10, pady=(8,2))
        
        # Separator
        sep = tk.Frame(section, bg='#2a2a3a', height=1)
        sep.pack(fill=tk.X, padx=10, pady=2)
        
        # Content lines
        for line in lines:
            tk.Label(
                section,
                text=line,
                font=('Arial', 9),
                bg='#16213e',
                fg='#cccccc',
                anchor=tk.W,
                justify=tk.LEFT
            ).pack(anchor=tk.W, padx=15, pady=1)
        
        # Spacer
        tk.Label(section, text="", bg='#16213e').pack()
    
    def get_severity_color(self, severity):
        colors = {
            'SEVERE': '#ff4757',
            'MODERATE': '#ffaa00',
            'MINOR': '#00ff88'
        }
        return colors.get(severity, '#ffffff')
    
    def get_severity_info(self, severity):
        info = {
            'SEVERE': [
                "• Width > 3mm",
                "• Depth > 7.5mm",
                "• Structural integrity compromised",
                "• Immediate action required"
            ],
            'MODERATE': [
                "• Width 1-3mm",
                "• Depth 2-7mm",
                "• Surface damage",
                "• Monitor regularly"
            ],
            'MINOR': [
                "• Width < 1mm",
                "• Depth < 2mm",
                "• Cosmetic only",
                "• Routine monitoring"
            ]
        }
        return info.get(severity, ["Unknown"])
    
    def analyze_cause(self, crack):
        width = crack['width_mm']
        if width < 1:
            return {
                'cause': 'Plastic Shrinkage',
                'description': 'Cracks formed during concrete curing',
                'fix': 'Apply surface sealant'
            }
        elif width < 3:
            return {
                'cause': 'Thermal Stress',
                'description': 'Cracks due to temperature changes',
                'fix': 'Fill with epoxy and monitor'
            }
        else:
            return {
                'cause': 'Structural Stress',
                'description': 'Cracks from overloading or settlement',
                'fix': 'IMMEDIATE ENGINEER CONSULTATION'
            }
    
    def assess_risk(self, crack):
        width = crack['width_mm']
        depth = crack.get('depth_mm', width * 1.5)
        score = min(width * 20, 60) + min(depth * 5, 40)
        
        if score < 30:
            return {'level': 'LOW', 'action': 'Monitor during routine checks'}
        elif score < 50:
            return {'level': 'MODERATE', 'action': 'Schedule repair within 3 months'}
        elif score < 70:
            return {'level': 'HIGH', 'action': 'Repair within 1 month'}
        else:
            return {'level': 'CRITICAL', 'action': 'IMMEDIATE ACTION REQUIRED'}

# ===========================================
# CLICKABLE IMAGE LABEL - FIXED VERSION
# ===========================================

class ClickableImageLabel(tk.Label):
    def __init__(self, parent, app, **kwargs):
        super().__init__(parent, **kwargs)
        self.app = app
        self.crack_rects = {}  # Store crack rectangles
        self.crack_data = []
        self.image_scale = 1.0
        self.photo_image = None
        
        # Bind mouse events
        self.bind("<Button-1>", self.on_click)
        self.bind("<Motion>", self.on_motion)
        
    def set_cracks(self, crack_data, image_scale):
        """Set crack data and calculate clickable areas"""
        self.crack_rects = {}
        self.crack_data = crack_data
        self.image_scale = image_scale
        
        print(f"Setting {len(crack_data)} clickable cracks")  # Debug
        
        # Calculate clickable rectangles for each crack
        for crack in crack_data:
            x, y, w, h = crack['bounds']
            
            # Scale coordinates to displayed image size
            scaled_x = int(x * image_scale)
            scaled_y = int(y * image_scale)
            scaled_w = max(1, int(w * image_scale))  # Ensure at least 1 pixel
            scaled_h = max(1, int(h * image_scale))
            
            # Store rectangle coordinates
            self.crack_rects[crack['id']] = {
                'x1': scaled_x,
                'y1': scaled_y,
                'x2': scaled_x + scaled_w,
                'y2': scaled_y + scaled_h,
                'crack': crack
            }
            
            print(f"Crack {crack['display_id']}: rect=({scaled_x},{scaled_y})-({scaled_x+scaled_w},{scaled_y+scaled_h})")  # Debug
    
    def on_click(self, event):
        """Handle click event - FIXED"""
        x, y = event.x, event.y
        print(f"Click at ({x}, {y})")  # Debug
        
        # Check if click is inside any crack rectangle
        for crack_id, rect in self.crack_rects.items():
            if (rect['x1'] <= x <= rect['x2'] and 
                rect['y1'] <= y <= rect['y2']):
                print(f"Clicked on crack {rect['crack']['display_id']}")  # Debug
                self.app.show_crack_details(rect['crack'])
                break
    
    def on_motion(self, event):
        """Handle mouse motion for hover effect"""
        x, y = event.x, event.y
        cursor_set = False
        
        # Check if mouse is over any crack
        for crack_id, rect in self.crack_rects.items():
            if (rect['x1'] <= x <= rect['x2'] and 
                rect['y1'] <= y <= rect['y2']):
                if not cursor_set:
                    self.config(cursor="hand2")
                    cursor_set = True
                break
        
        if not cursor_set:
            self.config(cursor="")

# ===========================================
# MAIN APPLICATION
# ===========================================

class VajraDrishthi:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("🏗️ VAJRA-DRISHTHI - Clickable Cracks")
        self.window.geometry("1400x800")
        self.window.configure(bg='#0a0a0f')
        
        self.center_window()
        
        # Create folders
        os.makedirs("reports", exist_ok=True)
        os.makedirs("images", exist_ok=True)
        
        # Settings
        self.pixels_per_mm = 10
        self.current_cracks = []
        self.image_scale = 1.0
        
        # Colors
        self.colors = {
            'bg_dark': '#0a0a0f',
            'bg_medium': '#1a1a2a',
            'bg_light': '#2a2a3a',
            'accent_blue': '#00a8ff',
            'accent_orange': '#ffaa00',
            'accent_red': '#ff4757',
            'text_secondary': '#cccccc',
            'border': '#3a3a4a'
        }
        
        self.setup_ui()
        
    def center_window(self):
        self.window.update_idletasks()
        width, height = self.window.winfo_width(), self.window.winfo_height()
        x = (self.window.winfo_screenwidth() - width) // 2
        y = (self.window.winfo_screenheight() - height) // 2
        self.window.geometry(f'{width}x{height}+{x}+{y}')
        
    def setup_ui(self):
        # Header
        header = tk.Frame(self.window, bg=self.colors['bg_medium'], height=100)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        tk.Label(header, text="🏗️ VAJRA-DRISHTHI", font=('Arial',28,'bold'),
                bg=self.colors['bg_medium'], fg=self.colors['accent_blue']).pack(pady=10)
        tk.Label(header, text="CLICK ON ANY CRACK to open DETAILED INFO BLOCK",
                font=('Arial',12), bg=self.colors['bg_medium'], fg=self.colors['text_secondary']).pack()
        
        # Stats
        stats = tk.Frame(self.window, bg=self.colors['bg_light'], height=60)
        stats.pack(fill=tk.X, pady=10)
        stats.pack_propagate(False)
        
        self.stats = tk.Frame(stats, bg=self.colors['bg_light'])
        self.stats.pack(expand=True)
        
        self.total_label = self.create_stat("Total Cracks", "0", 0)
        self.severe_label = self.create_stat("🔴 Severe", "0", 1)
        self.moderate_label = self.create_stat("🟠 Moderate", "0", 2)
        self.minor_label = self.create_stat("🟡 Minor", "0", 3)
        
        # Main container
        main = tk.Frame(self.window, bg=self.colors['bg_dark'])
        main.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Left panel - Image
        left = tk.Frame(main, bg=self.colors['bg_medium'], relief=tk.RAISED, bd=1)
        left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        # Image header
        img_header = tk.Frame(left, bg=self.colors['bg_light'], height=40)
        img_header.pack(fill=tk.X)
        img_header.pack_propagate(False)
        
        tk.Label(img_header, text="📸 CLICK ON ANY CRACK TO OPEN INFO BLOCK",
                font=('Arial',11,'bold'), bg=self.colors['bg_light'],
                fg=self.colors['accent_orange']).pack(side=tk.LEFT, padx=10, pady=10)
        
        # Image display
        img_frame = tk.Frame(left, bg=self.colors['border'], bd=2)
        img_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.image_label = ClickableImageLabel(
            img_frame, self,
            text="⬆️ UPLOAD IMAGE\n\nHover over cracks to highlight\nCLICK any crack for DETAILED INFO BLOCK",
            bg=self.colors['bg_medium'], fg=self.colors['text_secondary'],
            font=('Arial',14), justify=tk.CENTER
        )
        self.image_label.pack(fill=tk.BOTH, expand=True)
        
        # Upload button
        upload_btn = ModernButton(left, text="📤 UPLOAD IMAGE", command=self.upload_image,
                                 bg_color='#00a8ff', hover_color='#0097e6', width=200, height=45)
        upload_btn.pack(pady=15)
        
        # Right panel - Results
        right = tk.Frame(main, bg=self.colors['bg_medium'], width=500, relief=tk.RAISED, bd=1)
        right.pack(side=tk.RIGHT, fill=tk.BOTH, padx=5)
        right.pack_propagate(False)
        
        # Notebook
        self.notebook = ttk.Notebook(right)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TNotebook', background=self.colors['bg_medium'])
        style.configure('TNotebook.Tab', background=self.colors['bg_light'], foreground='white', padding=[10,5])
        style.map('TNotebook.Tab', background=[('selected', self.colors['accent_blue'])])
        
        # Create tabs
        self.create_tab("📊 DETAILED")
        self.create_tab("📋 LIST")
        self.create_tab("📄 LABEL")
        
        # Status bar
        self.status = tk.Frame(self.window, bg=self.colors['bg_light'], height=30)
        self.status.pack(side=tk.BOTTOM, fill=tk.X)
        self.status.pack_propagate(False)
        
        self.status_icon = tk.Label(self.status, text="●", font=('Arial',12),
                                   bg=self.colors['bg_light'], fg='#00ff00')
        self.status_icon.pack(side=tk.LEFT, padx=10)
        
        self.status_label = tk.Label(self.status, text="Ready - Upload image to begin",
                                    font=('Arial',10), bg=self.colors['bg_light'], fg='white')
        self.status_label.pack(side=tk.LEFT)
    
    def create_stat(self, label, value, col):
        card = tk.Frame(self.stats, bg=self.colors['bg_medium'], width=120, height=60)
        card.grid(row=0, column=col, padx=10)
        card.grid_propagate(False)
        
        val = tk.Label(card, text=value, font=('Arial',20,'bold'),
                      bg=self.colors['bg_medium'], fg='white')
        val.pack(pady=(5,0))
        
        tk.Label(card, text=label, font=('Arial',9),
                bg=self.colors['bg_medium'], fg=self.colors['text_secondary']).pack()
        return val
    
    def create_tab(self, title):
        tab = tk.Frame(self.notebook, bg=self.colors['bg_medium'])
        self.notebook.add(tab, text=title)
        
        text = tk.Text(tab, bg='#1a1a2a', fg='white', font=('Consolas',10),
                      wrap=tk.WORD, height=25, bd=0, padx=10, pady=10)
        text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scroll = tk.Scrollbar(tab, command=text.yview, bg=self.colors['bg_medium'])
        scroll.pack(side=tk.RIGHT, fill=tk.Y)
        text.config(yscrollcommand=scroll.set)
        
        if title == "📊 DETAILED":
            self.detailed_text = text
        elif title == "📋 LIST":
            self.list_text = text
        else:
            self.label_text = text
    
    def show_crack_details(self, crack_data):
        """Show info block when crack is clicked"""
        print(f"Opening details for crack {crack_data['display_id']}")  # Debug
        CrackInfoBlock(self.window, crack_data)
    
    def detect_cracks(self, image_path):
        img = cv2.imread(image_path)
        if img is None:
            return None, None, []
        
        original = img.copy()
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5,5), 0)
        edges = cv2.Canny(blurred, 30, 100)
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        result = original.copy()
        crack_data = []
        
        # Generate crack IDs (C1, C2, C3, etc.)
        for i, contour in enumerate(contours):
            area = cv2.contourArea(contour)
            if area < 50:
                continue
            
            x,y,w,h = cv2.boundingRect(contour)
            width_mm = w / self.pixels_per_mm
            
            if width_mm < 1:
                severity = "MINOR"
                color = (0,255,255)
            elif width_mm < 3:
                severity = "MODERATE"
                color = (0,165,255)
            else:
                severity = "SEVERE"
                color = (0,0,255)
            
            # Draw crack
            cv2.drawContours(result, [contour], -1, color, 2)
            
            # Add label
            label = f"C{i+1}"
            cv2.putText(result, label, (x, y-10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
            
            crack_data.append({
                'id': i+1,
                'display_id': f"C{i+1}",
                'width_mm': round(width_mm, 2),
                'severity': severity,
                'area': int(area),
                'bounds': (x,y,w,h)
            })
        
        # Add header
        cv2.putText(result, f"Cracks Found: {len(crack_data)}", (20,30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255,255,255), 2)
        
        return original, result, crack_data
    
    def simulate_lidar(self, crack_data):
        for crack in crack_data:
            width = crack['width_mm']
            if crack['severity'] == 'MINOR':
                depth = width * 1.2
            elif crack['severity'] == 'MODERATE':
                depth = width * 1.8
            else:
                depth = width * 2.5
            depth += np.random.normal(0, depth * 0.05)
            crack['depth_mm'] = round(depth, 2)
            crack['volume_mm3'] = round(crack['area'] * depth / 100, 2)
        return crack_data
    
    def upload_image(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Images", "*.jpg *.jpeg *.png *.bmp")]
        )
        if not file_path:
            return
        
        self.status_icon.config(fg='#ffaa00')
        self.status_label.config(text="Processing...")
        self.window.update()
        
        try:
            # Detect cracks
            original, result, crack_data = self.detect_cracks(file_path)
            if original is None:
                messagebox.showerror("Error", "Could not read image")
                return
            
            # Simulate LiDAR
            crack_data = self.simulate_lidar(crack_data)
            self.current_cracks = crack_data
            
            # Update stats
            severe = sum(1 for c in crack_data if c['severity'] == 'SEVERE')
            moderate = sum(1 for c in crack_data if c['severity'] == 'MODERATE')
            minor = sum(1 for c in crack_data if c['severity'] == 'MINOR')
            
            self.total_label.config(text=str(len(crack_data)))
            self.severe_label.config(text=str(severe))
            self.moderate_label.config(text=str(moderate))
            self.minor_label.config(text=str(minor))
            
            # Generate reports
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Detailed report
            detailed = f"""
╔══════════════════════════════════════════════════════════════╗
║              VAJRA-DRISHTHI ANALYSIS REPORT                  ║
╚══════════════════════════════════════════════════════════════╝

SUMMARY
───────────────────────────────────────────────────────────────
Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Total Cracks: {len(crack_data)}

SEVERITY
───────────────────────────────────────────────────────────────
SEVERE   : {severe}
MODERATE : {moderate}
MINOR    : {minor}

LIDAR MEASUREMENTS
───────────────────────────────────────────────────────────────
Total Volume: {sum(c.get('volume_mm3', 0) for c in crack_data):.2f} mm³
Max Depth   : {max((c.get('depth_mm', 0) for c in crack_data), default=0):.2f} mm

DETAILED CRACK ANALYSIS
───────────────────────────────────────────────────────────────
"""
            for c in crack_data:
                detailed += f"""
═══════════════════════════════════════════════════════════════
CRACK {c['display_id']} [{c['severity']}]
───────────────────────────────────────────────────────────────
   Width      : {c['width_mm']} mm
   Depth      : {c.get('depth_mm', 'N/A')} mm (LiDAR)
   Area       : {c['area']} pixels²
   Volume     : {c.get('volume_mm3', 0):.2f} mm³
   Location   : {c['bounds']}
   
   👆 CLICK on this crack in the image for complete analysis
"""
            
            # List report
            list_report = f"CRACKS FOUND: {len(crack_data)}\nSevere: {severe}\nModerate: {moderate}\nMinor: {minor}\n\n"
            for c in crack_data:
                list_report += f"{c['display_id']}\n{c['severity']}\n\n"
            list_report += "👆 Click any crack in image for details"
            
            # Label report
            label_report = f"# Cracks Found: {len(crack_data)}\n\n"
            for c in crack_data:
                label_report += f"{c['display_id']}: {c['severity']}\n"
            label_report += "\nSuccess\nOK\n\n👆 Click any crack in image for details"
            
            # Update text widgets
            self.detailed_text.delete(1.0, tk.END)
            self.detailed_text.insert(1.0, detailed)
            self.list_text.delete(1.0, tk.END)
            self.list_text.insert(1.0, list_report)
            self.label_text.delete(1.0, tk.END)
            self.label_text.insert(1.0, label_report)
            
            # Display image
            result_rgb = cv2.cvtColor(result, cv2.COLOR_BGR2RGB)
            img_pil = Image.fromarray(result_rgb)
            
            # Calculate scale for clickable regions
            orig_w, orig_h = img_pil.size
            img_pil.thumbnail((600,500))
            disp_w, disp_h = img_pil.size
            self.image_scale = disp_w / orig_w
            
            img_tk = ImageTk.PhotoImage(img_pil)
            self.image_label.config(image=img_tk, text="")
            self.image_label.image = img_tk
            
            # Set clickable regions
            self.image_label.set_cracks(crack_data, self.image_scale)
            
            # Save
            img_path = f"images/analysis_{timestamp}.jpg"
            cv2.imwrite(img_path, result)
            
            self.status_icon.config(fg='#00ff00')
            self.status_label.config(text=f"✅ Found {len(crack_data)} cracks - Click any crack for details")
            
            messagebox.showinfo("Success", 
                f"✅ Found {len(crack_data)} cracks\n\n"
                f"🔴 Severe: {severe}\n🟠 Moderate: {moderate}\n🟡 Minor: {minor}\n\n"
                f"👆 Now CLICK on any crack (C1, C2, C3...) in the image to see DETAILS!")
            
        except Exception as e:
            self.status_icon.config(fg='#ff4757')
            self.status_label.config(text=f"Error: {str(e)}")
            messagebox.showerror("Error", str(e))
    
    def run(self):
        self.window.mainloop()

# ===========================================
# MAIN
# ===========================================

if __name__ == "__main__":
    print("="*70)
    print("🏗️ VAJRA-DRISHTHI - CLICKABLE CRACKS (FIXED)")
    print("Team Vishwakarmas - AMD Slingshot 2026")
    print("="*70)
    print("""
    ✨ HOW TO USE:
    1. Upload an image
    2. HOVER over any crack (cursor changes to hand)
    3. CLICK on crack to open DETAILED INFO BLOCK
    
    Info Block contains:
    📏 Dimensions | 📍 Location | ⚠️ Severity
    🔍 Root Cause | 🛠️ Recommendations
    """)
    print("="*70)
    
    app = VajraDrishthi()
    app.run()