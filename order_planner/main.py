import pandas as pd
import os
import subprocess
from tkinter import Tk, filedialog, messagebox, StringVar, Label, OptionMenu, Button, Radiobutton
from split_grouping import split_by_commodity_with_style_grouping
import sys

def open_file(filepath):
    # Automatically open the output file depending on the OS
    if os.name == 'nt':  # For Windows
        os.startfile(filepath)
    elif os.name == 'posix':  # For MacOS and Linux
        subprocess.call(('open', filepath))

def browse_file():
    # Create file dialog to browse and select a file
    Tk().withdraw()  # Hide the root window
    file_path = filedialog.askopenfilename(
        title="Select Excel File",
        filetypes=[("Excel files", "*.xlsx *.xls")]
    )
    if file_path:
        select_style(file_path)

    sys.exit()

def select_style(input_file):
    # Create a simple GUI for style selection
    root = Tk()
    root.title("Select Style and Sorting Option")

    selected_style = StringVar(root)
    selected_style.set("All")  # Default value to "All"

    styles = ["All", "Giro", "Fox", "Vex", "Bulk"]  # Added "All" option

    # Create dropdown menu for style selection
    label = Label(root, text="Select the style for filtering:")
    label.pack()

    style_dropdown = OptionMenu(root, selected_style, *styles)
    style_dropdown.pack()

    # Create a variable for sorting option
    sorting_option = StringVar(root)
    sorting_option.set("Style")  # Default value for sorting

    # Create radio buttons for sorting options
    label_sort = Label(root, text="Select sorting option:")
    label_sort.pack()

    Radiobutton(root, text="Style", variable=sorting_option, value="Style").pack(anchor="w")
    Radiobutton(root, text="Size and Grade", variable=sorting_option, value="Size and Grade").pack(anchor="w")

    # Create OK button to confirm selection
    def on_confirm():
        root.destroy()  # Close the dropdown menu
        split_by_commodity_with_style_grouping(input_file, selected_style.get(), sorting_option.get())

    confirm_button = Button(root, text="OK", command=on_confirm)
    confirm_button.pack()

    root.mainloop()

def main():
    # Create a simple GUI window for file selection
    root = Tk()
    root.withdraw()  # Hide the root window

    # Open file dialog for input
    browse_file()
    

# Run the GUI application
if __name__ == "__main__":
    main()