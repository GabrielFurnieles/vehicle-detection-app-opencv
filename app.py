import tkinter as tk
from tkinter import filedialog, ttk
import cv2
import numpy as np
from PIL import Image, ImageTk

import tkinter as tk
from tkinter import filedialog
import cv2
import numpy as np
from PIL import Image, ImageTk

from tracker import *

class VideoApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Counting Vehicle App")
        
        # Video variables
        self.cap = None
        self.video_label = tk.Label(root)
        self.video_label.pack(expand=True)

        # Buttons
        self.start_counting_btn = tk.Button(root, text="Start Counting", command=self.start_counting, state=tk.DISABLED)
        self.start_counting_btn.pack(side=tk.LEFT, padx=10)

        self.mask_video_btn = tk.Button(root, text="Mask Video", command=self.mask_video)
        self.mask_video_btn.pack(side=tk.RIGHT, padx=10)

        # Loading field
        self.loading_label = tk.Label(root, text="No video loaded", font=("Helvetica", 16))
        self.loading_label.pack(expand=True)

        # Flag to check if mask is set
        self.mask_set = False

    def load_video(self):
        file_path = filedialog.askopenfilename(title="Select Video File", filetypes=[("Video files", "*.mp4;*.avi")])
        if file_path:
            self.file_path = file_path
            self.cap = cv2.VideoCapture(file_path)
            self.ret_first, self.first_frame = self.cap.read()
            self.show_frame(first=True)
            self.start_counting_btn.config(state=tk.DISABLED)

    def show_frame(self, first=False):
        if first:
            ret, frame = True, self.first_frame
        else:
            ret, frame = self.cap.read()
        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame)
            img = ImageTk.PhotoImage(img)
            self.video_label.config(image=img)
            self.video_label.image = img
            self.loading_label.pack_forget()  # Hide the loading label
        else:
            self.loading_label.config(text="End of video reached", fg="red")

    def mask_video(self):
        # Implement your video masking logic here
        print("Video masked")
        self.mask_set = True
        self.start_counting_btn.config(state=tk.NORMAL)  # Enable the Start Counting button

        self.mask_editor = MaskEditor(self.first_frame)
        self.root.wait_window(self.mask_editor.window)

    def start_counting(self):
        if self.mask_set or self.mask_editor.saved_mask is not None:
            counting_window = tk.Toplevel(self.root)
            counting_window.geometry("640x480")  # Adjust the size as needed

            counting_window_label = tk.Label(counting_window, text="Vehicle Counting in Progress...")
            counting_window_label.pack()

            self.run_counting(counting_window)
        else:
            tk.messagebox.showwarning("Warning", "Please set or save a mask before counting.")

    def run_counting(self, counting_window):
        self.cap = cv2.VideoCapture(self.file_path)
        vehicle_count_window = CountingWindow(counting_window, self.cap, self.mask_editor.saved_mask)

        # Wait for the counting window to close
        counting_window.wait_window(vehicle_count_window.window)
        self.on_counting_window_close()

    def on_counting_window_close(self):
        self.cap.release()  # Release the video capture when the counting window is closed

class MaskEditor:
    def __init__(self, frame):
        self.frame = frame
        self.window = tk.Toplevel()
        self.window.title("Mask Editor")

        self.canvas = tk.Canvas(self.window)
        self.canvas.pack(expand=True, fill=tk.BOTH)
        self.canvas.bind("<B1-Motion>", self.paint)
        self.canvas.bind("<B3-Motion>", self.erase)

        self.brush_size_var = tk.IntVar(value=10)
        self.paint_mode_var = tk.StringVar(value="road_segmentation")

        self.brush_size_slider = tk.Scale(self.window, label="Brush Size", variable=self.brush_size_var, from_=1, to=50, orient=tk.HORIZONTAL)
        self.brush_size_slider.pack(side=tk.LEFT, padx=10)

        paint_mode_frame = tk.Frame(self.window)
        paint_mode_frame.pack(side=tk.RIGHT, padx=10)

        road_segmentation_radio = tk.Radiobutton(paint_mode_frame, text="Road Segmentation", variable=self.paint_mode_var, value="road_segmentation")
        road_segmentation_radio.pack()

        # counting_line_radio = tk.Radiobutton(paint_mode_frame, text="Counting Line", variable=self.paint_mode_var, value="counting_line")
        # counting_line_radio.pack()

        self.save_mask_btn = tk.Button(self.window, text="Save Mask", command=self.save_mask)
        self.save_mask_btn.pack(side=tk.BOTTOM, pady=10)

        self.saved_mask = None  # Variable to store the saved mask

        self.init_mask()
        self.instructions_popup()

    def instructions_popup(self):
        instructions = """
        Welcome to Mask Editor!
        
        - Left-click to paint.
        - Right-click to erase.
        - Adjust brush size using the slider.
        - Save your mask using the 'Save Mask' button.
        """
        tk.messagebox.showinfo("Instructions", instructions)

    def init_mask(self):
        self.mask = np.zeros_like(self.frame)

        frame_ = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(frame_)
        img = ImageTk.PhotoImage(img)
        self.canvas.config(width=img.width(), height=img.height())
        self.canvas.create_image(0, 0, anchor=tk.NW, image=img)
        self.canvas.image = img

    def save_mask(self):
        self.saved_mask = np.copy(self.mask)
        self.window.destroy()

    def paint(self, event):
        brush_size = self.brush_size_var.get()
        paint_mode = self.paint_mode_var.get()

        x1, y1 = (event.x - brush_size // 2), (event.y - brush_size // 2)
        x2, y2 = (event.x + brush_size // 2), (event.y + brush_size // 2)

        color = (0, 255, 0) if paint_mode == "road_segmentation" else (0, 0, 255)
        cv2.rectangle(self.mask, (x1, y1), (x2, y2), color, -1)

        self.update_canvas()

    def erase(self, event):
        brush_size = self.brush_size_var.get()

        x1, y1 = (event.x - brush_size // 2), (event.y - brush_size // 2)
        x2, y2 = (event.x + brush_size // 2), (event.y + brush_size // 2)

        cv2.rectangle(self.mask, (x1, y1), (x2, y2), (0, 0, 0), -1)

        self.update_canvas()

    def update_canvas(self):
        frame_ = cv2.addWeighted(self.frame, 1, self.mask, 0.5, 0)
        frame_ = cv2.cvtColor(frame_, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(frame_)
        img = ImageTk.PhotoImage(img)
        self.canvas.itemconfig(self.canvas.find_all()[0], image=img)
        self.canvas.image = img

class CountingWindow:
    def __init__(self, window, video_cap, mask):
        self.window = window
        self.window.title("Vehicle Counting Window")

        self.video_cap = video_cap
        self.mask = mask

        # Add a notebook to have multiple tabs
        self.notebook = ttk.Notebook(window)
        self.notebook.pack(fill='both', expand=True)

        # Tab 1: Parameters Input
        self.tab1 = ttk.Frame(self.notebook)
        self.notebook.add(self.tab1, text='Parameters')

        self.pixel_to_km_label = tk.Label(self.tab1, text="Pixel to Km ratio:")
        self.pixel_to_km_label.grid(row=0, column=0)

        self.pixel_to_km_entry = tk.Entry(self.tab1)
        self.pixel_to_km_entry.grid(row=0, column=1)
        self.pixel_to_km_entry.bind('<FocusOut>', self.validate_pixel_to_km)

        self.start_button = tk.Button(self.tab1, text="Start", command=self.start_counting)
        self.start_button.grid(row=1, column=0, columnspan=2)
        self.start_button["state"] = "disabled"  # Initially, the button is disabled

        self.disclaimer_label = tk.Label(self.tab1, text="If you can't hit the Start button after entering parameters, press TAB key")
        self.disclaimer_label.grid(row=2, column=0, columnspan=2, pady=10)

        # Tab 2: Vehicle Counting
        self.tab2 = ttk.Frame(self.notebook)
        self.notebook.add(self.tab2, text='Vehicle Counting')

        self.vehicle_count_label = tk.Label(self.tab2, text="")
        self.vehicle_count_label.pack()

        self.save_button = tk.Button(self.tab2, text="Save Vehicle Info", command=self.save_vehicle_info)
        self.save_button.pack()

        self.vehicle_info_text = tk.Text(self.tab2, height=10, width=50)
        self.vehicle_info_text.pack()

        # Bind event to show disclaimer when switching to the Parameters tab
        self.notebook.bind("<<NotebookTabChanged>>", self.show_disclaimer)


    def validate_pixel_to_km(self, event):
        try:
            # Try converting the input to a float
            float_value = float(self.pixel_to_km_entry.get())
            if float_value > 0:
                # Enable the "Start" button if a valid value is entered
                self.start_button["state"] = "normal"
            else:
                # Disable the "Start" button for invalid values
                self.start_button["state"] = "disabled"
        except ValueError:
            # Disable the "Start" button for non-numeric input
            self.start_button["state"] = "disabled"

    def start_counting(self):
        # Get the user-provided Pixel to Km ratio
        pixel_to_km_value = self.pixel_to_km_entry.get()

        if not pixel_to_km_value or not pixel_to_km_value.replace(".", "").isdigit():
            # Show a message to the user to fill in the parameters
            tk.messagebox.showwarning("Missing Parameters", "Please fill in the Pixel to Km ratio.")
            return

        # Convert the ratio to a float
        pixel_to_km_ratio = float(pixel_to_km_value)

        # Call your custom vehicle_counter algorithm with the video_cap, mask, and ratio
        print("checking cap")
        # Check if camera opened successfully
        if (self.video_cap.isOpened() == False):
            print(self.video_cap)
            raise RuntimeError("Error opening video file in CountingWindow")

        vehicle_count, vehicle_info = vehicle_counter2(self.video_cap, self.mask, pixel_to_km_ratio)
        self.vehicle_count_label.config(text=f"{vehicle_count} vehicles counted!")

        # Store the vehicle info for later use
        self.vehicle_info = vehicle_info

        # Display a sample of the vehicle info in the Text widget
        sample_info = vehicle_info.head().to_string(index=False)
        self.vehicle_info_text.insert(tk.END, sample_info)

        # Enable the Save button
        self.save_button["state"] = "normal"

    def save_vehicle_info(self):
        try:
            # Ask the user for the file name to save the CSV
            file_path = tk.filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])

            if file_path:
                # Save the vehicle info to the CSV file
                self.vehicle_info.to_csv(file_path, index=False)
                tk.messagebox.showinfo("Save Successful", "Vehicle info saved successfully!")
        except Exception as e:
            tk.messagebox.showerror("Error", f"An error occurred: {str(e)}")


# class CountingWindow:
#     def __init__(self, window, video_cap, mask, on_counting_window_close):
#         self.window = window
#         self.window.title("Vehicle Counting Window")

#         self.video_cap = video_cap
#         self.mask = mask

#         self.vehicle_count_label = tk.Label(window, text="")
#         self.vehicle_count_label.pack()

#         self.count_vehicles()
#         on_counting_window_close()

#     def count_vehicles(self):
#         # Call your custom vehicle_counter algorithm with the video_cap and mask
#         vehicle_count = vehicle_counter2(self.video_cap, self.mask)
#         self.vehicle_count_label.config(text=f"{vehicle_count} vehicles counted!")

if __name__ == "__main__":
    root = tk.Tk()
    app = VideoApp(root)

    load_video_btn = tk.Button(root, text="Load Video", command=app.load_video)
    load_video_btn.pack()

    root.mainloop()
