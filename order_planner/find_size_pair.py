import pandas as pd
import os
import subprocess
from tkinter import Tk, filedialog, messagebox, StringVar, Label, OptionMenu, Button, Radiobutton

def find_size_and_qty(row):
    """ Function to find the non-zero qnt and the corresponding sizename. """
    # Loop through sizename and qnt pairs from 1 to 8
    for i in range(1, 20):  # Assuming sizename1-qnt1 up to sizename8-qnt8
        size_col = f'sizename{i}'
        qnt_col = f'qnt{i}'
        
        # Check if both columns exist and qnt is non-zero
        if size_col in row and qnt_col in row and row[qnt_col] != 0:
            return row[size_col], row[qnt_col]
    
    # If all quantities are zero, return None values
    return None, None


