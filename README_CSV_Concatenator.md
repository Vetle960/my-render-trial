# CSV File Concatenator

A Python GUI application that allows you to select multiple CSV files from a folder, concatenate them while maintaining data types, and save the result as both an Excel file and a CSV file to a location of your choice.

## Features

- **File Selection**: Browse and select multiple CSV files from any folder
- **Data Type Preservation**: Maintains original data types during concatenation
- **Dual Output**: Saves results as both CSV and Excel formats
- **Progress Tracking**: Real-time progress bar and status updates
- **Error Handling**: Comprehensive error handling with user-friendly messages
- **Results Display**: Shows detailed information about the concatenated data
- **Logging**: Built-in logging for debugging and monitoring

## Requirements

- Python 3.7+
- pandas
- openpyxl (for Excel support)
- tkinter (usually comes with Python)

## Installation

1. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the application:
   ```bash
   python csv_concat_app.py
   ```

## Usage

### Step 1: Select CSV Files
1. Click "Browse Files" to open the file selection dialog
2. Navigate to your folder containing CSV files
3. Select multiple CSV files (hold Ctrl/Cmd to select multiple)
4. Selected files will appear in the list

### Step 2: Select Output Directory
1. Click "Browse Output Directory" to choose where to save the results
2. Navigate to your desired output folder
3. Click "Select Folder"

### Step 3: Concatenate Files
1. Once both files and output directory are selected, the "Concatenate Files" button will be enabled
2. Click "Concatenate Files" to start the process
3. Monitor progress through the progress bar and status updates
4. Results will be displayed in the results section

## Output Files

The application generates two output files with timestamps:
- `concatenated_YYYYMMDD_HHMMSS.csv` - CSV format
- `concatenated_YYYYMMDD_HHMMSS.xlsx` - Excel format

## Data Type Handling

- The application automatically infers data types from each CSV file
- Data types are preserved during concatenation
- Uses pandas' `pd.concat()` with `ignore_index=True` for optimal performance

## Error Handling

- Invalid CSV files are caught and reported
- File reading errors are displayed with specific error messages
- The application continues gracefully even if some files fail

## Tips

- Ensure all CSV files have compatible column structures
- Large files may take longer to process
- The application shows real-time progress for better user experience
- Check the results section for detailed information about the concatenated data

## Troubleshooting

- **"No module named 'openpyxl'"**: Install openpyxl: `pip install openpyxl`
- **"Permission denied"**: Ensure you have write access to the output directory
- **"Invalid CSV format"**: Check that your CSV files are properly formatted

## Example Use Cases

- Combining monthly sales reports
- Merging survey data from multiple sources
- Consolidating log files
- Combining data exports from different systems
- Merging research datasets

## Technical Details

- Built with tkinter for cross-platform compatibility
- Uses pandas for efficient data manipulation
- Implements proper memory management for large files
- Includes comprehensive logging for debugging
- Follows Python best practices and PEP 8 guidelines 