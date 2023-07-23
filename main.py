import cv2
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import os
import threading
import time
import itertools

# Global variable for output link
output_link = None

# Global variable for video path
video_path = None

# Function to extract frames from the selected video
def extract_frames(video_path, output_folder):
    # Open video
    video_capture = cv2.VideoCapture(video_path)

    # Initialize variables
    frame_count = 0

    # Get the total number of frames in the video
    total_frames = int(video_capture.get(cv2.CAP_PROP_FRAME_COUNT))

    while True:
        # Read the next frame from the video
        ret, frame = video_capture.read()

        # Check if there are any frames left
        if not ret:
            break

        # Save the frame as an image file in the output folder
        frame_filename = f"{output_folder}/frame_{frame_count:04d}.jpg"
        cv2.imwrite(frame_filename, frame)

        # Update the progress bar and label status
        progress_bar_extract["value"] = frame_count
        label_status_extract.config(text=f"Processing Frame {frame_count}/{total_frames}")
        root.update_idletasks()

        # Increase the frame count
        frame_count += 1

    # Close the video capture after finishing
    video_capture.release()

    # Update the progress bar and label status to indicate that extraction is completed
    progress_bar_extract["value"] = total_frames
    label_status_extract.config(text=f"Extraction completed!")
    root.update_idletasks()

# Function to create video from images
def create_video_from_images(image_folder, output_file, width, height, fps=30):
    global output_link

    images = [img for img in os.listdir(image_folder) if img.endswith(".jpg") or img.endswith(".png")]
    images.sort(key=str.lower)  # Sort images based on file name (alphanumeric)

    # Get the dimension of the first image
    image_path = os.path.join(image_folder, images[0])
    frame = cv2.imread(image_path)
    height, width, _ = frame.shape

    # If the output_file does not have the .mp4 extension, automatically add it
    if not output_file.endswith(".mp4"):
        output_file += ".mp4"

    # Add index number to the output_file name if it already exists
    index = 1
    while os.path.exists(output_file):
        base_name, extension = os.path.splitext(output_file)
        output_file = f"{base_name}_{index}{extension}"
        index += 1

    # Create a video writer
    video_writer = cv2.VideoWriter(output_file, cv2.VideoWriter_fourcc(*"mp4v"), fps, (width, height))

    # Show the progress bar on the GUI
    total_frames = len(images)
    progress_bar["maximum"] = total_frames

    def update_progress_bar():
        for i, image in enumerate(images, 1):
            image_path = os.path.join(image_folder, image)
            frame = cv2.imread(image_path)
            frame_resized = cv2.resize(frame, (width, height))  # Resize the frame to the chosen size
            video_writer.write(frame_resized)

            # Update the progress bar on the GUI
            progress_bar["value"] = i
            root.update_idletasks()

            # Show the frame image on the GUI
            show_frame(image_path)

            # Set the duration of each frame in the video (milliseconds)
            time.sleep(1000 / fps / 1000)

        # Close the video writer
        video_writer.release()

        # Show "Video berhasil dibuat!" status on the GUI
        label_status.config(text="Video berhasil dibuat!")
        # Show the output video location as a clickable link
        output_link = tk.Label(main_frame, text="Lokasi Video : " + os.path.abspath(output_file), fg="white", cursor="hand2", background="#1c1c1c")
        output_link.grid(row=1, column=0, columnspan=2, pady=5)
        output_link.bind("<Enter>", lambda e: output_link.config(fg="white", underline=True))
        output_link.bind("<Leave>", lambda e: output_link.config(fg="white", underline=False))
        output_link.bind("<Button-1>", lambda e: os.startfile(os.path.abspath(output_file)))

    # Start a thread for the video creation process
    progress_thread = threading.Thread(target=update_progress_bar)
    progress_thread.start()

# Function to browse image folder
def browse_image_folder():
    global folder_path
    folder_path = filedialog.askdirectory()
    entry_folder_path.delete(0, tk.END)
    entry_folder_path.insert(0, folder_path)

# Function to browse video file
def select_video():
    global video_path
    file_path = filedialog.askopenfilename(title="Select Video File", filetypes=[("Video Files", "*.mp4 *.avi")])
    if file_path:
        entry_video_path.delete(0, tk.END)
        entry_video_path.insert(tk.END, file_path)
        video_path = file_path
        btn_check_fps.config(state=tk.NORMAL)  # Enable the "Check FPS" button when a video is selected


# Function to browse output folder
def select_output_folder():
    folder_path = filedialog.askdirectory(title="Select Output Folder")
    if folder_path:
        entry_output_folder.delete(0, tk.END)
        entry_output_folder.insert(tk.END, folder_path)

def check_video_fps(video_path):
    # Open video
    video_capture = cv2.VideoCapture(video_path)
    
    # Get FPS from video
    fps = video_capture.get(cv2.CAP_PROP_FPS)
    
    # Release the video capture after checking FPS
    video_capture.release()
    
    return fps

def update_fps_label(fps_value):
    label_fps.config(text=f"Video FPS: {fps_value}")

def start_fps_check():
    global label_fps
    video_path = entry_video_path.get()

    if not video_path:
        messagebox.showwarning("Warning", "Please select a video file first.")
        return

    fps = check_video_fps(video_path)
    label_fps.config(text=f"Video FPS: {fps}")


# Function to start extraction
def start_extraction():
    global video_path
    video_path = entry_video_path.get()

    if not os.path.exists(video_path):
        messagebox.showerror("Error", "Video file not found.")
        return

    output_folder = entry_output_folder.get()

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    extraction_thread = threading.Thread(target=extract_frames, args=(video_path, output_folder))
    extraction_thread.start()

# Function to switch to the "Extract Video Frames" tab
def switch_to_extract_frames_tab():
    tab_control.select(extract_frames_tab)

# Function to switch to the "Create Video from Images" tab
def switch_to_create_video_tab():
    tab_control.select(create_video_tab)

# Function to show frame on the GUI
def show_frame(image_path):
    if image_path is None:
        # Local default image (black solid image)
        default_image_path = "default_image.jpg"
        img = Image.open(default_image_path)
    else:
        img = Image.open(image_path)

    img.thumbnail((400, 300))
    img = ImageTk.PhotoImage(img)
    label_frame.config(image=img)
    label_frame.image = img

# Function to create video from images
def create_video():
    folder_path = entry_folder_path.get()
    output_video = entry_output_video.get()
    width = int(entry_width.get())
    height = int(entry_height.get())
    frame_per_second = int(entry_fps.get())

    if not os.path.exists(folder_path):
        messagebox.showerror("Error", "Folder foto tidak ditemukan.")
        return

    if len(output_video.strip()) == 0:
        messagebox.showerror("Error", "Masukkan nama video keluaran.")
        return

    create_video_from_images(folder_path, output_video, width, height, frame_per_second)

# Function to open output folder
def open_output_folder():
    output_video = entry_output_video.get()
    if not output_video.endswith(".mp4"):
        output_video += ".mp4"
    output_folder = os.path.dirname(os.path.abspath(output_video))
    os.startfile(output_folder)

# Function to refresh the GUI
def refresh():
    global output_link
    label_status.config(text="")
    if output_link:
        output_link.grid_forget()

# Function to open tutorial link in browser
def open_tutorial():
    # Replace "https://www.example.com/tutorial" with the actual tutorial website URL
    tutorial_url = "https://www.stableart.cloud"
    import webbrowser
    webbrowser.open(tutorial_url)

def open_discord():
    import webbrowser
    webbrowser.open("https://discord.gg/mWraTpkW3H")  # Replace "https://discord.gg/example" with your Discord link
    webbrowser.open(open_discord)

def animate_text_color(label):
    colors = ['red', 'green', 'blue', 'purple', 'orange', 'yellow']
    color_cycle = itertools.cycle(colors)

    def update_color():
        label.config(fg=next(color_cycle))
        root.after(500, update_color)

    update_color()


def resize_window(event):
    content_width = root.winfo_reqwidth()
    content_height = root.winfo_reqheight()

    window_width = content_width + 20
    window_height = content_height + 40
    root.geometry(f"{window_width}x{window_height}")

root = tk.Tk()
root.title("StableArt v0.1.4 (Beta)")

root.pack_propagate(False)

root.config(bg="#1c1c1c")

style = ttk.Style()
style.theme_use("clam")
style.configure(".", background="#1c1c1c", foreground="white")
style.configure("TButton", background="#444444", foreground="white")
style.configure("TEntry", background="black", foreground="black")
style.map("TButton",
          foreground=[('active', 'white'),
                      ('pressed', 'white')],
          background=[('active', '#444444'),
                      ('pressed', '#666666')])

menu_bar = tk.Menu(root)
root.config(menu=menu_bar)

file_menu = tk.Menu(menu_bar, tearoff=0)
menu_bar.add_cascade(label="File", menu=file_menu)
file_menu.add_command(label="Open Output Folder", command=open_output_folder)
file_menu.add_command(label="Exit", command=root.quit)

help_menu = tk.Menu(menu_bar, tearoff=0)
menu_bar.add_cascade(label="Help", menu=help_menu)
help_menu.add_command(label="About", command=lambda: messagebox.showinfo("About", "Aplikasi ini dibuat oleh www.stableart.cloud"))
help_menu.add_command(label="Tutorial", command=open_tutorial)

main_frame = ttk.Frame(root)
main_frame.grid(row=0, column=0, sticky="nsew")

main_frame.columnconfigure(0, weight=1)
main_frame.columnconfigure(1, weight=1)

image_frame = ttk.Frame(main_frame, width=400, height=300)
image_frame.grid(row=0, column=0, padx=20, pady=20)

label_frame = ttk.Label(image_frame)
label_frame.pack()

form_frame = ttk.Frame(main_frame)
form_frame.grid(row=0, column=1, padx=20, pady=20)

tab_control = ttk.Notebook(form_frame)
tab_control.pack(expand=1, fill="both")

extract_frames_tab = ttk.Frame(tab_control)
tab_control.add(extract_frames_tab, text="Extract Video Frames")

extract_frames_frame = ttk.Frame(extract_frames_tab)
extract_frames_frame.pack(pady=10)

label_video_path = ttk.Label(extract_frames_frame, text="Select Video:")
label_video_path.pack(pady=5)
entry_video_path = ttk.Entry(extract_frames_frame)
entry_video_path.pack(pady=5, padx=10, fill="x", expand=True)
button_browse_video = ttk.Button(extract_frames_frame, text="Browse", command=select_video)
button_browse_video.pack(pady=5)

btn_check_fps = ttk.Button(extract_frames_frame, text="Check FPS", command=start_fps_check)
btn_check_fps.pack(pady=5)

label_fps = ttk.Label(extract_frames_frame, text="")
label_fps.pack(pady=5)

label_output_folder = ttk.Label(extract_frames_frame, text="Select Output Folder:")
label_output_folder.pack(pady=5)
entry_output_folder = ttk.Entry(extract_frames_frame)
entry_output_folder.pack(pady=5, padx=10, fill="x", expand=True)
button_browse_output = ttk.Button(extract_frames_frame, text="Browse", command=select_output_folder)
button_browse_output.pack(pady=5)

button_start_extraction = ttk.Button(extract_frames_frame, text="Start Extraction", command=start_extraction)
button_start_extraction.pack(pady=10)

progress_bar_extract = ttk.Progressbar(extract_frames_frame, orient="horizontal", length=200, mode="determinate")
progress_bar_extract.pack(pady=10)

label_status_extract = ttk.Label(extract_frames_frame, text="")
label_status_extract.pack(pady=5)

create_video_tab = ttk.Frame(tab_control)
tab_control.add(create_video_tab, text="Create Video from Images")

create_video_frame = ttk.Frame(create_video_tab)
create_video_frame.pack(pady=10)

label_folder_path = ttk.Label(create_video_frame, text="Folder Foto:")
label_folder_path.pack(pady=5)
entry_folder_path = ttk.Entry(create_video_frame)
entry_folder_path.pack(pady=5, padx=10, fill="x", expand=True)
button_browse_folder = ttk.Button(create_video_frame, text="Cari Folder", command=browse_image_folder)
button_browse_folder.pack(pady=5)

label_output_video = ttk.Label(create_video_frame, text="Nama Video:")
label_output_video.pack(pady=5)
entry_output_video = ttk.Entry(create_video_frame)
entry_output_video.pack(pady=5, padx=10, fill="x", expand=True)

label_width = ttk.Label(create_video_frame, text="Lebar (pixel):")
label_width.pack(pady=5)
entry_width = ttk.Entry(create_video_frame)
entry_width.pack(pady=5, padx=10, fill="x", expand=True)

label_height = ttk.Label(create_video_frame, text="Tinggi (pixel):")
label_height.pack(pady=5)
entry_height = ttk.Entry(create_video_frame)
entry_height.pack(pady=5, padx=10, fill="x", expand=True)

label_video_fps = ttk.Label(create_video_frame, text="Frame Per Second:")
label_video_fps.pack(pady=5)
entry_fps = ttk.Entry(create_video_frame)
entry_fps.pack(pady=5, padx=10, fill="x", expand=True)

button_create_video = ttk.Button(create_video_frame, text="Buat Video", command=create_video)
button_create_video.pack(pady=10)

progress_bar = ttk.Progressbar(create_video_frame, orient="horizontal", length=200, mode="determinate")
progress_bar.pack(pady=10)

label_status = ttk.Label(create_video_frame, text="")
label_status.pack(pady=5)

button_open_folder = ttk.Button(create_video_frame, text="Lokasi", command=open_output_folder)
button_open_folder.pack(pady=5)

tab_control.add(extract_frames_tab, text="Extract Video Frames")
tab_control.add(create_video_tab, text="Create Video from Images")

tab_control.select(extract_frames_tab)

label_discord = ttk.Label(root, text="Join our Discord Server", cursor="hand2", font=("Arial", 10), underline=True, wraplength=200, justify="center")
label_discord.grid(row=4, column=0, pady=5)
label_discord.bind("<Button-1>", lambda e: open_discord())

root.mainloop()
