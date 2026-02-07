from ClockAssistLogic import toggle, start, set_tolerance, set_boost, set_mouse_button
import ClockAssistLogic
import customtkinter
from PIL import Image
import os
import ctypes

script_dir = os.path.dirname(__file__)

source_icon = os.path.join(os.path.dirname(__file__), "icon.ico")
output_icon = os.path.join(os.path.dirname(__file__), "icon_fixed.ico")
img = Image.open(source_icon)
img.save(output_icon, format='ICO', sizes=[(32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])

toggle_state = ("Disabled", False)
default_tolerance = 10
default_boost = 10
clicks_per_second = 0
# Modern color palette
COLORS = {
    "bg": "#250000",       
    "surface": "#070000",    
    "primary": "#FFFFFF",     
    "success": "#06d6a0",     
    "danger": "#ef476f",    
    "text": "#FFFFFF",
    "text_dim": "#a0a0a0",
}

class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        
        # Set app ID for Windows taskbar FIRST
        myappid = 'clickassist.app.v2.0'
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
        
        # Window setup
        self.geometry("550x550")
        self.title("Click Assist")
        self.minsize(550, 550)
        self.maxsize(550, 550)
        icon_path = os.path.join(os.path.dirname(__file__), "icon_fixed.ico")
        self.iconbitmap(icon_path)  # No need for after() anymore
        
        # Set theme
        customtkinter.set_appearance_mode("dark")
        customtkinter.set_default_color_theme("blue")
        self.configure(fg_color=COLORS["bg"])
        
        # Main container frame for better organization
        self.main_frame = customtkinter.CTkFrame(self, fg_color=COLORS["bg"])
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        self.create_header()
        self.create_main_controls()
        self.create_settings()


        self.update_cps_display()
        
    def create_header(self):
        header_frame = customtkinter.CTkFrame(self.main_frame, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 20))
        
        self.title_label = customtkinter.CTkLabel(
            header_frame,
            text="Click Assist V2.0",
            font=("Segoe UI", 36, "bold"),
            text_color=COLORS["primary"]
        )
        self.title_label.pack()
        
    def create_main_controls(self):
        control_frame = customtkinter.CTkFrame(
            self.main_frame,
            fg_color=COLORS["surface"],
            corner_radius=15
        )
        control_frame.pack(fill="x", pady=(0, 20), padx=10)
        control_frame.pack_propagate(False)
        control_frame.configure(height=180)
        
        # CPS Display
        self.cps_label = customtkinter.CTkLabel(
            control_frame,
            text=f"{ClockAssistLogic.measured_cps}",
            font=("Segoe UI", 48, "bold"),
            text_color=COLORS["text"],
        )
        self.cps_label.pack(pady=(15, 0))
        self.update_cps_display()
        
        cps_subtitle = customtkinter.CTkLabel(
            control_frame,
            text="Clicks Per Second",
            font=("Segoe UI", 12),
            text_color=COLORS["text_dim"]
        )
        cps_subtitle.pack()
        
        # Main toggle button
        self.toggle_button = customtkinter.CTkButton(
            control_frame,
            text=toggle_state[0].upper(),
            command=self.button_click,
            width=200,
            height=45,
            font=("Segoe UI", 16, "bold"),
            fg_color=COLORS["danger"],
            hover_color=self.darken_color(COLORS["danger"]),
            corner_radius=10,
            border_width=0
        )
        self.toggle_button.pack(pady=(10, 15))
        
    def create_settings(self):
        settings_frame = customtkinter.CTkFrame(
            self.main_frame,
            fg_color=COLORS["surface"],
            corner_radius=15
        )
        settings_frame.pack(fill="both", expand=True, padx=10)
        settings_frame.pack_propagate(False)
        settings_frame.configure(height=300)
        
        # Mouse button selector
        button_frame = customtkinter.CTkFrame(settings_frame, fg_color="transparent")
        button_frame.pack(fill="x", padx=20, pady=(15, 10))
        
        customtkinter.CTkLabel(
            button_frame,
            text="Mouse Button",
            font=("Segoe UI", 12, "bold"),
            text_color=COLORS["text"]
        ).pack(side="left")
        
        self.current_button = "left"
        self.mouse_button = customtkinter.CTkButton(
            button_frame,
            text=self.current_button.title(),
            command=self.toggle_mouse_button,
            width=100,
            height=30,
            font=("Segoe UI", 12),
            text_color=COLORS["surface"],
            fg_color=COLORS["primary"],
            hover_color=self.darken_color(COLORS["primary"]),
            corner_radius=8
        )
        self.mouse_button.pack(side="right")
        
        # Tolerance slider
        self.create_slider_control(
            settings_frame,
            "Tolerance",
            2, 15, 13,
            default_tolerance,
            self.tolerance_changed
        )
        
        # Boost slider
        self.create_slider_control(
            settings_frame,
            "Boost",
            1, 10, 9,
            default_boost,
            self.boost_changed
        )
        
    def create_slider_control(self, parent, label_text, from_, to, steps, default, command):
        container = customtkinter.CTkFrame(parent, fg_color="transparent")
        container.pack(fill="x", expand=True, padx=20, pady=10)
        
        # Top row: label and value
        top_row = customtkinter.CTkFrame(container, fg_color="transparent")
        top_row.pack(fill="x", pady=(0, 5))
        
        customtkinter.CTkLabel(
            top_row,
            text=label_text,
            font=("Segoe UI", 12, "bold"),
            text_color=COLORS["text"]
        ).pack(side="left")
        
        value_label = customtkinter.CTkLabel(
            top_row,
            text=str(int(default)),
            font=("Segoe UI", 12, "bold"),
            text_color=COLORS["primary"]
        )
        value_label.pack(side="right")
        
        # Slider
        slider = customtkinter.CTkSlider(
            container,
            from_=from_,
            to=to,
            number_of_steps=steps,
            command=lambda v: self.slider_callback(v, value_label, command),
            width=490,
            height=22,  # Taller = definitely round
            button_color=COLORS["primary"],
            button_hover_color=self.darken_color(COLORS["primary"]),
            progress_color=COLORS["primary"],
            fg_color=COLORS["bg"],
            button_length=22  # ← Add this to control handle size explicitly
)
        
        slider.set(default)
        slider.pack(fill="x")
        
        if label_text == "Tolerance":
            self.tolerance_label = value_label
            self.tolerance_slider = slider
        else:
            self.boost_label = value_label
            self.boost_slider = slider
            
    def slider_callback(self, value, label, command):
        value_int = int(value)
        label.configure(text=str(value_int))
        command(value)
        
    def button_click(self):
        global toggle_state
        toggle_state = toggle(toggle_state)
        text, enabled = toggle_state
        
        self.toggle_button.configure(
            text=text.upper(),
            fg_color=COLORS["success"] if enabled else COLORS["danger"],
            hover_color=self.darken_color(COLORS["success"] if enabled else COLORS["danger"])
        )
        
    def tolerance_changed(self, value):
        global default_tolerance
        value_int = int(value)
        default_tolerance = value_int
        set_tolerance(value_int)
        
    def boost_changed(self, value):
        global default_boost
        value_int = int(value)
        default_boost = value_int
        set_boost(value_int)
        
    def toggle_mouse_button(self):
        self.current_button = "right" if self.current_button == "left" else "left"
        set_mouse_button(self.current_button)
        self.mouse_button.configure(text=self.current_button.title())

    def update_cps_display(self):
        current_cps = ClockAssistLogic.measured_cps  # Access from the module
        self.cps_label.configure(text=f"{current_cps}")
        self.after(100, self.update_cps_display)

    @staticmethod
    def darken_color(hex_color, factor=0.8):
        hex_color = hex_color.lstrip('#')
        r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        r, g, b = int(r * factor), int(g * factor), int(b * factor)
        return f"#{r:02x}{g:02x}{b:02x}"
    

    

start()

app = App()
app.mainloop()