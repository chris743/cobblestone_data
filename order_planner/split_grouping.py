import pandas as pd
import os
import subprocess
from tkinter import Tk, filedialog, messagebox, StringVar, Label, OptionMenu, Button, Radiobutton
from find_size_pair import find_size_and_qty


COLUMNS_TO_REMOVE = [
    'sizename1', 'qnt1', 'sizename2', 'qnt2', 'sizename3', 'qnt3', 'sizename4', 'qnt4', 
    'sizename5', 'qnt5', 'sizename6', 'qnt6', 'sizename7', 'qnt7', 'sizename8', 'sizename9', 'sizename10', 'sizename11', 'sizename12', 
    'qnt8', 'qnt9', 'qnt10', 'qnt', 'shipstylecolor', 'reserveqnt', 'curinventory', 
    'ordercount', 'qnttype', 'ascompanyname', 'astitle', 'asreportdate', 'totalqnt'
]

def split_by_commodity_with_style_grouping(input_file, selected_style, sorting_option):
    # Load the Excel file
    df = pd.read_excel(input_file)  # Update 'test' to your actual sheet name

    # Create new columns 'size' and 'qty' by applying the find_size_and_qty function
    df['size'], df['qty'] = zip(*df.apply(find_size_and_qty, axis=1))

    # Remove the specified columns
    df = df.drop(columns=COLUMNS_TO_REMOVE, errors='ignore')

    # Get distinct commodities
    commodities = df['commodity'].unique()

    # Create a writer to output into a new workbook
    output_file = "output_split_commodities_grouped.xlsx"
    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
        for commodity in commodities:
            # Filter for each commodity
            commodity_data = df[df['commodity'] == commodity]

            # If a style is selected, filter by it, excluding "All"
            if selected_style != "All":
                commodity_data = commodity_data[commodity_data['style'].str.contains(selected_style, case=False, na=False)]
            
            # Separate into BAGS (contains 'GIRO', 'FOX', 'VEX') and CARTONS (doesn't contain them)
            bags_data = commodity_data[commodity_data['style'].str.contains('GIRO|FOX|VEX', case=False, na=False)]
            cartons_data = commodity_data[~commodity_data['style'].str.contains('GIRO|FOX|VEX', case=False, na=False)]

            if not bags_data.empty:
                write_grouped_data(writer, bags_data, f"{commodity} - BAGS", sorting_option)

            if not cartons_data.empty:
                write_grouped_data(writer, cartons_data, f"{commodity} - CARTONS", sorting_option)

    # Notify the user and open the output file
    messagebox.showinfo("Success", f"Data has been successfully split and saved to '{output_file}'.")
    open_file(output_file)

def open_file(filepath):
    # Automatically open the output file depending on the OS
    if os.name == 'nt':  # For Windows
        os.startfile(filepath)
    elif os.name == 'posix':  # For MacOS and Linux
        subprocess.call(('open', filepath))


def write_grouped_data(writer, data, sheet_name, sorting_option):
    # Sort the data based on the selected sorting option
    if sorting_option == "Style":
        data = data.sort_values(by='style')
        group_column = 'style'
    elif sorting_option == "Size and Grade":
        data = data.sort_values(by=['size', 'grade'])
        group_column = 'size'  # Primary group column

    # Get distinct groups based on the selected option
    distinct_groups = data[group_column].unique()

    # Create a list to hold rows for final output
    output_rows = []
    
    for group in distinct_groups:
        # Filter data by each group
        if sorting_option == "Style":
            group_data = data[data['style'] == group]
        else:  # Size and Grade
            group_data = data[data['size'] == group]

            # Sort within this group by style
            group_data = group_data.sort_values(by='style')

        # Append the data for the group to the output
        output_rows.append(group_data)

        # Append a blank row after each group (empty DataFrame)
        blank_row = pd.DataFrame([[""] * len(group_data.columns)], columns=group_data.columns)
        output_rows.append(blank_row)

    # Concatenate all rows together
    final_data = pd.concat(output_rows)

    # Write to Excel sheet
    final_data.to_excel(writer, sheet_name=sheet_name, index=False)

