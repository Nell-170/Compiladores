# Import libraries
import sys
import tkinter as tk
from tkinter import ttk, filedialog
from datetime import datetime
from PIL import Image, ImageTk
from tkinter import messagebox
from graphic import create_chart  # Import the function to create the chart
from analysis import read_file, count_categories, read_description, errorsAndWarningsReportGenerator, read_time # Import the functions
from parser import parser_tester, structures_parser_tester 

path = "large_complex_log.txt" 
file_path = path

# Function to show a specific page and hide the others
def show_page(page_name):

    # Hide all pages first
    for page in all_pages:
        page.grid_forget()
    
    # Show the selected page
    if page_name == "home": 
        home_page.grid(row = 1, column = 0, sticky = "nsew", padx = 20, pady = 20)
    elif page_name == "page_1":
        page_1.grid(row = 1, column = 0, sticky = "nsew", padx = 20, pady = 20)
    elif page_name == "page_2":
        page_2.grid(row = 1, column = 0, sticky = "nsew", padx = 20, pady = 20)
        render_feature_2()
    elif page_name == "page_3":
        page_3.grid(row = 1, column = 0, sticky = "nsew", padx = 20, pady = 20)
    elif page_name == "page_4":
        page_4.grid(row = 1, column = 0, sticky = "nsew", padx = 20, pady = 20)

# Function to change the button color when hovering over it
def on_enter(event, button):
    button.config(bg = "#45a049")  # Darker green when hovering

def on_leave(event, button):
    button.config(bg = "#4CAF50")  # Original green when not hovering

# Function to open and read the file
def open_file():
    file_path_m = filedialog.askopenfilename(title="Selecciona un archivo de texto", filetypes=[("Archivos de texto", "*.txt")])

    global path
    path = file_path_m

    global file_path
    file_path = path

    if file_path:  # Checks if the user selected a file
        with open(file_path, "r", encoding="utf-8") as file:
            content = file.read()
            text_display.config(state="normal")  # Temporarily enable editing
            text_display.delete("1.0", tk.END)  # Clear previous content
            text_display.insert(tk.END, content)  # Insert the contents of the file
            text_display.config(state="disabled")  # Disable editing

    return file_path

# Function to render the chart on page_2
def render_feature_2():

    """Opens a file, counts categories, and shows a bar chart in Tkinter."""
    global path
    file_path = path

    if not file_path:
        return

    # Read the file and count the categories
    lines = read_file(file_path)
    total, errors, warnings, info, debug = count_categories(lines)

    count = {
        "Errors": len(errors),
        "Warnings": len(warnings),
        "Info": len(info),
        "Debug": len(debug)
    }

    # Create the chart
    img = create_chart(count)
    # Show image in Tkinter
    label_img.config(image = img)
    # Avoid the image from being deleted from memory
    label_img.image = img

# function to check for possible errors detected by the parser
def errors_detected_by_parser():
    try:
        with open("Parser_report.txt", "r", encoding="utf-8") as f:
            first_line = f.readline()

            if "Error" in first_line or "Illegal" in first_line:
                return True
            
    except FileNotFoundError:
        print("El archivo Parser_report.txt no fue encontrado.")

    return False

# The lexer and parser are tested before starting the app's GUI.
if parser_tester(path) == False:
    sys.exit(1)

if errors_detected_by_parser() == True: 
    sys.exit(1)
        
# Create the main Tkinter window
HomePage = tk.Tk()
HomePage.title("Home Page")
HomePage.geometry("1600x900")
HomePage.config(bg = "#fdfdfd")

# Configure the main window to expand
HomePage.grid_rowconfigure(0, weight = 0)
HomePage.grid_rowconfigure(1, weight = 1)
HomePage.grid_columnconfigure(0, weight = 1)

# Create the top bar
HeaderBox = tk.Frame(HomePage, bg = "#4CAF50", pady = 0)
HeaderBox.grid(row = 0, column = 0, sticky = "ew", padx = 0, pady = 0)

# Create the header frame
HeaderFrame = tk.Frame(HeaderBox, bg = "#4CAF50")
HeaderFrame.grid(row = 0, column = 0, sticky = "ew", padx = 0)

# Button style
button_style = {
    'width': 12,
    'height': 2,
    'relief': 'flat',
    'bg': '#4CAF50',
    'fg': 'white',
    'font': ("Helvetica", 12, "bold"),
    'padx': 10,
    'pady': 5
}

# Custom navigation buttons
home_button = tk.Button(HeaderFrame, text = "Home", command = lambda: show_page("home"), **button_style)
home_button.grid(row = 0, column = 1, padx = 10)
home_button.bind("<Enter>", lambda event, button = home_button: on_enter(event, button))
home_button.bind("<Leave>", lambda event, button = home_button: on_leave(event, button))

page_1_button = tk.Button(HeaderFrame, text = "Error report", command = lambda: show_page("page_1"), **button_style)
page_1_button.grid(row = 0, column = 2, padx = 10)
page_1_button.bind("<Enter>", lambda event, button = page_1_button: on_enter(event, button))
page_1_button.bind("<Leave>", lambda event, button = page_1_button: on_leave(event, button))

page_2_button = tk.Button(HeaderFrame, text = "Graphic", command = lambda: show_page("page_2"), **button_style)
page_2_button.grid(row = 0, column = 3, padx = 10)
page_2_button.bind("<Enter>", lambda event, button = page_2_button: on_enter(event, button))
page_2_button.bind("<Leave>", lambda event, button = page_2_button: on_leave(event, button))

page_3_button = tk.Button(HeaderFrame, text = "Logs By Time", command = lambda: show_page("page_3"), **button_style)
page_3_button.grid(row = 0, column = 4, padx = 10)
page_3_button.bind("<Enter>", lambda event, button = page_3_button: on_enter(event, button))
page_3_button.bind("<Leave>", lambda event, button = page_3_button: on_leave(event, button))

page_4_button = tk.Button(HeaderFrame, text = "Import", command = lambda: show_page("page_4"), **button_style)
page_4_button.grid(row = 0, column = 5, padx = 10)
page_4_button.bind("<Enter>", lambda event, button = page_4_button: on_enter(event, button))
page_4_button.bind("<Leave>", lambda event, button = page_4_button: on_leave(event, button))

# Home page
# ==================
home_page = ttk.Frame(HomePage, style="TFrame")
home_page.grid(row=0, column=0, sticky="nsew")

# Configure style for the frame and labels
style = ttk.Style()
style.configure("TFrame", background = "#fdfdfd")
style.configure("TLabel", background = "#fdfdfd", font=("Helvetica", 16))

# Add the first label (description read from the log)
label = ttk.Label(home_page, text = read_description(path), style = "TLabel", wraplength = 1000, anchor = "center")
label.grid(row = 0, column = 0, padx = 20, pady=(20, 50), sticky= "nsew")

# Description text
descriptionText = "This program has 5 different options:" \
"\n\n1. Home: This page with a description of the program." \
"\n\n2. Error report: Reads how many errors and warnings are in the log file." \
"\n\n3. Graphic: A page with a chart showing the distribution of log messages." \
"\n\n4. Logs by time: Gets all the entries within a certain hour range." \
"\n\n5. Import: Add another file print it." 

# Add the second label with options
description = ttk.Label(home_page, text=descriptionText, style="TLabel", wraplength=1000, anchor="center")
description.grid(row=1, column=0, padx=20, pady=(20, 50), sticky="nsew")

# Load the logo image
logo_image = Image.open("media/logo.jpeg")
logo_image = logo_image.resize((300, 150), Image.LANCZOS) 
logo_photo = ImageTk.PhotoImage(logo_image)

# Add the logo image below the description label
logo_label = tk.Label(home_page, image = logo_photo, bg = "#fdfdfd")
logo_label.image = logo_photo
logo_label.grid(row = 2, column = 0, pady=(20, 50), sticky = "nsew")

# Configure the grid rows and columns
home_page.grid_rowconfigure(0, weight=0)
home_page.grid_rowconfigure(1, weight=1)
home_page.grid_rowconfigure(2, weight=0)
home_page.grid_columnconfigure(0, weight=1)
 
# Page 3 with the hours range
# =========================
page_3 = ttk.Frame(HomePage, style="TFrame")

# Label for time range selection
ttk.Label(page_3, text="Select the range of hours", style="TLabel").grid(row=0, column=0, columnspan=6, pady=10)

# Function to get the selected time range
def get_time_range():
    start_year = start_year_var.get()
    start_month = start_month_var.get()
    start_day = start_day_var.get()
    start_hours = start_hour_var.get()
    start_minutes = start_minutes_var.get()
    start_seconds = start_seconds_var.get()
    
    end_year = end_year_var.get()
    end_month = end_month_var.get()
    end_day = end_day_var.get()
    end_hours = end_hour_var.get()
    end_minutes = end_minutes_var.get()
    end_seconds = end_seconds_var.get()

    category_type = categories_var.get()
    
    # Format the start and end times as HH:MM:SS
    start_time_str = f"{start_year}-{start_month}-{start_day} {start_hours}:{start_minutes}:{start_seconds}"
    end_time_str = f"{end_year}-{end_month}-{end_day} {end_hours}:{end_minutes}:{end_seconds}"
    
    # Convert to datetime objects
    try:
        start_time = datetime.strptime(start_time_str, "%Y-%m-%d %H:%M:%S")
        end_time = datetime.strptime(end_time_str, "%Y-%m-%d %H:%M:%S")
        
        # Update the label with the selected time range
        logs = read_time(path, start_time, end_time, category_type)
        shownTime = (f"Selected Time Range: {start_time.strftime('%Y-%m-%d %H:%M:%S')} "
                    f"to {end_time.strftime('%Y-%m-%d %H:%M:%S')}\n\n"
                    + "\n".join(logs))
        time_range_label.config(text=shownTime)
        
    except ValueError:
        time_range_label.config(text="Invalid time format.")

# Create StringVar for start time (year, month, day, hours, minutes, seconds)
start_year_var = tk.StringVar()
start_month_var = tk.StringVar()
start_day_var = tk.StringVar()
start_hour_var = tk.StringVar()
start_minutes_var = tk.StringVar()
start_seconds_var = tk.StringVar()

# Create StringVar for end time (year, month, day, hours, minutes, seconds)
end_year_var = tk.StringVar()
end_month_var = tk.StringVar()
end_day_var = tk.StringVar()
end_hour_var = tk.StringVar()
end_minutes_var = tk.StringVar()
end_seconds_var = tk.StringVar()

# Create combobox for categories
categories_var = tk.StringVar()

# Options for hours, minutes, and seconds
year_options = [str(i) for i in range(2020, 2031)]
month_options = [str(i).zfill(2) for i in range(1, 13)]
day_options = [str(i).zfill(2) for i in range(1, 32)]
hour_options = [str(i).zfill(2) for i in range(24)]
minutes_options = [str(i).zfill(2) for i in range(60)]
seconds_options = [str(i).zfill(2) for i in range(60)]

# Category options
category_options = ["ALL", "INFO", "WARN", "ERROR", "DEBUG"]

# Start Time Widgets
ttk.Label(page_3, text="Start Time:", style="TLabel").grid(row=1, column=0, padx=5, pady=5, sticky="w")

start_year_combobox = ttk.Combobox(page_3, textvariable=start_year_var, values=year_options, state="readonly", width=5)
start_year_combobox.grid(row=1, column=4, padx=5, pady=5)
start_year_combobox.set(year_options[0])

start_month_combobox = ttk.Combobox(page_3, textvariable=start_month_var, values=month_options, state="readonly", width=5)
start_month_combobox.grid(row=1, column=5, padx=5, pady=5)
start_month_combobox.set(month_options[0])

start_day_combobox = ttk.Combobox(page_3, textvariable=start_day_var, values=day_options, state="readonly", width=5)
start_day_combobox.grid(row=1, column=6, padx=5, pady=5)
start_day_combobox.set(day_options[0])

start_hours_combobox = ttk.Combobox(page_3, textvariable=start_hour_var, values=hour_options, state="readonly", width=5)
start_hours_combobox.grid(row=1, column=1, padx=5, pady=5)
start_hours_combobox.set(hour_options[0])

start_minutes_combobox = ttk.Combobox(page_3, textvariable=start_minutes_var, values=minutes_options, state="readonly", width=5)
start_minutes_combobox.grid(row=1, column=2, padx=5, pady=5)
start_minutes_combobox.set(minutes_options[0])

start_seconds_combobox = ttk.Combobox(page_3, textvariable=start_seconds_var, values=seconds_options, state="readonly", width=5)
start_seconds_combobox.grid(row=1, column=3, padx=5, pady=5)
start_seconds_combobox.set(seconds_options[0])

# End Time Widgets
ttk.Label(page_3, text="End Time:", style="TLabel").grid(row=2, column=0, padx=5, pady=5, sticky="w")

end_year_combobox = ttk.Combobox(page_3, textvariable=end_year_var, values=year_options, state="readonly", width=5)
end_year_combobox.grid(row=2, column=4, padx=5, pady=5)
end_year_combobox.set(year_options[0])

end_month_combobox = ttk.Combobox(page_3, textvariable=end_month_var, values=month_options, state="readonly", width=5)
end_month_combobox.grid(row=2, column=5, padx=5, pady=5)
end_month_combobox.set(month_options[0])

end_day_combobox = ttk.Combobox(page_3, textvariable=end_day_var, values=day_options, state="readonly", width=5)
end_day_combobox.grid(row=2, column=6, padx=5, pady=5)
end_day_combobox.set(day_options[0])

end_hours_combobox = ttk.Combobox(page_3, textvariable=end_hour_var, values=hour_options, state="readonly", width=5)
end_hours_combobox.grid(row=2, column=1, padx=5, pady=5)
end_hours_combobox.set(hour_options[0])

end_minutes_combobox = ttk.Combobox(page_3, textvariable=end_minutes_var, values=minutes_options, state="readonly", width=5)
end_minutes_combobox.grid(row=2, column=2, padx=5, pady=5)
end_minutes_combobox.set(minutes_options[0])

end_seconds_combobox = ttk.Combobox(page_3, textvariable=end_seconds_var, values=seconds_options, state="readonly", width=5)
end_seconds_combobox.grid(row=2, column=3, padx=5, pady=5)
end_seconds_combobox.set(seconds_options[0])

# Category Combobox
categories_combobox = ttk.Combobox(page_3, textvariable=categories_var, values=category_options, state="readonly", width=5)
categories_combobox.grid(row=3, column=1, padx=5, pady=5)
categories_combobox.set(category_options[0])

# Button to show the selected time range
btn_show = ttk.Button(page_3, text="Show", command=get_time_range)
btn_show.grid(row=3, column=0, columnspan=6, padx=20, pady=10)

# Add a label to display the selected time range
time_range_label = ttk.Label(page_3, text="", style="TLabel")
time_range_label.grid(row=4, column=0, columnspan=6, pady=10)

# Page 2 with the chart
# =========================
page_2 = ttk.Frame(HomePage, style = "TFrame")
ttk.Label(page_2, text = "", style = "TLabel").grid(row = 0, column = 0, pady = 20)

# Widget to display the chart image
label_img = tk.Label(page_2)
label_img.grid(row = 2, column = 0, pady = 20)

# Page 1 whit the detailed report
# ==================
page_1 = ttk.Frame(HomePage, style="TFrame")
ttk.Label(page_1, text="Report of errors and warnings", style="TLabel").grid(row=0, column=0, pady=20)

# Page 4 whit the detailed report
# ==================
page_4 = ttk.Frame(HomePage, style="TFrame")

# Button to select file
btn_select_file = tk.Button(page_4, text="Select file", command=open_file, bg="#4CAF50", fg="white", font=("Helvetica", 12, "bold"))
btn_select_file.pack(pady=10)

# Text area to display the contents of the file
text_display = tk.Text(page_4, height=40, width=200, wrap="word", state="disabled")
text_display.pack(pady=10)

# Show page 4
page_4.tkraise()

# Frame to Text and scroll bar is created
text_frame = ttk.Frame(page_1)
text_frame.grid(row=2, column=0, padx=20, pady=20, sticky="nsew")

# widget Text is created
txt_todo = tk.Text(text_frame, wrap="word", font=("Helvetica", 17))
txt_todo.grid(row=0, column=0, sticky="nsew")

# Scroll bar is created
scrollbar = ttk.Scrollbar(text_frame, orient="vertical", command=txt_todo.yview)
scrollbar.grid(row=0, column=1, sticky="ns")

# The text to use the scroll bar is configurated 
txt_todo.config(yscrollcommand=scrollbar.set)

# The button to analyze is created (Pressing it prints the report)
btn_analizar = ttk.Button(page_1, text="Get report", command=lambda: save_and_display_information(file_path))
btn_analizar.grid(row=1, column=0, padx=20, pady=20, sticky="nsew")

# Funtion to do all process related to the report
def save_and_display_information(path):
    errorsAndWarningsReportGenerator(path)
    display_file_content()

# Function to read the file and show it content in GUI
def display_file_content():
    try:
        # Read the content of the file
        with open("System status report.txt", 'r', encoding='utf-8') as file:
            content = file.read()

        # Make the text to be displayed in the GUI
        texto = f"File Content:\n"
        texto += "--------------------\n"
        texto += f"Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        texto += content

        # Show the text in the widget of text (txt_todo)
        txt_todo.delete(1.0, tk.END)  # Clean the last content
        txt_todo.insert(tk.END, texto)  # Insert the new text

    except Exception as e:
        # Handle errors (e.g. if the file does not exist)
        error_message = f"Error reading file: {str(e)}"
        txt_todo.delete(1.0, tk.END)
        txt_todo.insert(tk.END, error_message)

# Configure the grid to be responsive
page_1.grid_rowconfigure(2, weight=1)
page_1.grid_columnconfigure(0, weight=1)

# Add all pages to a list
all_pages = [home_page, page_1, page_2, page_3, page_4]

# Show the home page by default
show_page("home")

# Start the Tkinter event loop
HomePage.mainloop()