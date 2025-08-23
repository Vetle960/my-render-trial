import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import pandas as pd
import os
from pathlib import Path
import logging
import subprocess
import threading
import webbrowser
import time

class CSVConcatenatorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("CSV File Concatenator & Dashboard Launcher")
        self.root.geometry("900x700")
        
        # Configure logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # Store selected files and output directory
        self.selected_files = []
        self.output_directory = ""
        
        # Dashboard process tracking
        self.dashboard_process = None
        self.dashboard_running = False
        
        self.setup_ui()
        
        # Start dashboard status monitoring
        self.check_dashboard_status()
        
    def setup_ui(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="CSV File Concatenator & Dashboard Launcher", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # File selection section
        ttk.Label(main_frame, text="Step 1: Select CSV Files", 
                 font=("Arial", 12, "bold")).grid(row=1, column=0, columnspan=3, 
                                                 sticky=tk.W, pady=(0, 10))
        
        # Select files button
        self.select_files_btn = ttk.Button(main_frame, text="Browse Files", 
                                         command=self.select_files)
        self.select_files_btn.grid(row=2, column=0, sticky=tk.W, pady=(0, 10))
        
        # Selected files listbox
        ttk.Label(main_frame, text="Selected Files:").grid(row=3, column=0, 
                                                          sticky=tk.W)
        self.files_listbox = tk.Listbox(main_frame, height=6, width=70)
        self.files_listbox.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), 
                               pady=(0, 10))
        
        # Scrollbar for files listbox
        files_scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, 
                                       command=self.files_listbox.yview)
        files_scrollbar.grid(row=4, column=3, sticky=(tk.N, tk.S))
        self.files_listbox.configure(yscrollcommand=files_scrollbar.set)
        
        # Clear files button
        self.clear_files_btn = ttk.Button(main_frame, text="Clear Files", 
                                        command=self.clear_files)
        self.clear_files_btn.grid(row=5, column=0, sticky=tk.W, pady=(0, 20))
        
        # Output directory section
        ttk.Label(main_frame, text="Step 2: Select Output Directory", 
                 font=("Arial", 12, "bold")).grid(row=6, column=0, columnspan=3, 
                                                 sticky=tk.W, pady=(0, 10))
        
        # Select output directory button
        self.select_output_btn = ttk.Button(main_frame, text="Browse Output Directory", 
                                          command=self.select_output_directory)
        self.select_output_btn.grid(row=7, column=0, sticky=tk.W, pady=(0, 10))
        
        # Output directory label
        self.output_dir_label = ttk.Label(main_frame, text="No output directory selected", 
                                         foreground="gray")
        self.output_dir_label.grid(row=8, column=0, columnspan=3, sticky=tk.W, 
                                  pady=(0, 20))
        
        # Concatenate button
        self.concat_btn = ttk.Button(main_frame, text="Concatenate Files", 
                                   command=self.concatenate_files, state=tk.DISABLED)
        self.concat_btn.grid(row=9, column=0, columnspan=3, pady=(0, 20))
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(main_frame, variable=self.progress_var, 
                                           maximum=100)
        self.progress_bar.grid(row=10, column=0, columnspan=3, sticky=(tk.W, tk.E), 
                              pady=(0, 10))
        
        # Status label
        self.status_label = ttk.Label(main_frame, text="Ready to start", 
                                     foreground="blue")
        self.status_label.grid(row=11, column=0, columnspan=3, sticky=tk.W)
        
        # Dashboard section
        ttk.Label(main_frame, text="Step 3: Launch 3D Visualization Dashboard", 
                 font=("Arial", 12, "bold")).grid(row=12, column=0, columnspan=3, 
                                                 sticky=tk.W, pady=(20, 10))
        
        # Dashboard description
        dashboard_desc = ttk.Label(main_frame, 
                                 text="Launch the 3D biosignal visualization dashboard (app.py)",
                                 foreground="gray")
        dashboard_desc.grid(row=13, column=0, columnspan=3, sticky=tk.W, pady=(0, 10))
        
        # Dashboard control frame
        dashboard_frame = ttk.Frame(main_frame)
        dashboard_frame.grid(row=14, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 20))
        
        # Launch dashboard button
        self.launch_dashboard_btn = ttk.Button(dashboard_frame, text="Launch Dashboard", 
                                             command=self.launch_dashboard)
        self.launch_dashboard_btn.grid(row=0, column=0, padx=(0, 10))
        
        # Stop dashboard button
        self.stop_dashboard_btn = ttk.Button(dashboard_frame, text="Stop Dashboard", 
                                           command=self.stop_dashboard, state=tk.DISABLED)
        self.stop_dashboard_btn.grid(row=0, column=1, padx=(0, 10))
        
        # Test connection button
        self.test_connection_btn = ttk.Button(dashboard_frame, text="Test Connection", 
                                            command=self.test_connection_clicked, 
                                            state=tk.DISABLED)
        self.test_connection_btn.grid(row=0, column=2, padx=(0, 10))
        
        # Refresh status button
        self.refresh_status_btn = ttk.Button(dashboard_frame, text="Refresh Status", 
                                           command=self.refresh_dashboard_status)
        self.refresh_status_btn.grid(row=0, column=3, padx=(0, 10))
        
        # Open in browser button
        self.open_browser_btn = ttk.Button(dashboard_frame, text="Open in Browser", 
                                         command=self.open_dashboard_in_browser, 
                                         state=tk.DISABLED)
        self.open_browser_btn.grid(row=0, column=4)
        
        # Dashboard status
        self.dashboard_status_label = ttk.Label(main_frame, text="Dashboard: Not running", 
                                              foreground="red")
        self.dashboard_status_label.grid(row=15, column=0, columnspan=3, sticky=tk.W, pady=(0, 20))
        
        # Results section
        ttk.Label(main_frame, text="Results", font=("Arial", 12, "bold")).grid(row=16, column=0, 
                                                                              sticky=tk.W, pady=(20, 10))
        
        # Results text
        self.results_text = tk.Text(main_frame, height=8, width=70)
        self.results_text.grid(row=17, column=0, columnspan=3, sticky=(tk.W, tk.E), 
                              pady=(0, 10))
        
        # Scrollbar for results
        results_scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, 
                                         command=self.results_text.yview)
        results_scrollbar.grid(row=17, column=3, sticky=(tk.N, tk.S))
        self.results_text.configure(yscrollcommand=results_scrollbar.set)
        
    def select_files(self):
        """Open file dialog to select multiple CSV files"""
        files = filedialog.askopenfilenames(
            title="Select CSV Files",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        
        if files:
            self.selected_files = list(files)
            self.update_files_listbox()
            self.update_concatenate_button()
            self.logger.info(f"Selected {len(self.selected_files)} files")
            
    def select_output_directory(self):
        """Open directory dialog to select output location"""
        directory = filedialog.askdirectory(title="Select Output Directory")
        
        if directory:
            self.output_directory = directory
            self.output_dir_label.config(text=f"Output: {directory}", foreground="black")
            self.update_concatenate_button()
            self.logger.info(f"Selected output directory: {directory}")
            
    def update_files_listbox(self):
        """Update the files listbox with selected files"""
        self.files_listbox.delete(0, tk.END)
        for file_path in self.selected_files:
            filename = os.path.basename(file_path)
            self.files_listbox.insert(tk.END, filename)
            
    def clear_files(self):
        """Clear all selected files"""
        self.selected_files = []
        self.files_listbox.delete(0, tk.END)
        self.update_concatenate_button()
        self.logger.info("Cleared all selected files")
        
    def update_concatenate_button(self):
        """Enable/disable concatenate button based on selections"""
        if self.selected_files and self.output_directory:
            self.concat_btn.config(state=tk.NORMAL)
        else:
            self.concat_btn.config(state=tk.DISABLED)
            
    def concatenate_files(self):
        """Concatenate the selected CSV files"""
        if not self.selected_files or not self.output_directory:
            messagebox.showerror("Error", "Please select files and output directory")
            return
            
        try:
            self.status_label.config(text="Starting concatenation...", foreground="blue")
            self.progress_var.set(0)
            self.root.update()
            
            # Read and concatenate files
            dataframes = []
            total_files = len(self.selected_files)
            baseline_columns = None
            
            for i, file_path in enumerate(self.selected_files):
                self.status_label.config(text=f"Reading file {i+1}/{total_files}: {os.path.basename(file_path)}")
                self.progress_var.set((i / total_files) * 50)  # First 50% for reading
                self.root.update()
                
                try:
                    # Read CSV with automatic data type inference
                    df = pd.read_csv(file_path, low_memory=False)

                    # Validate columns against baseline
                    if baseline_columns is None:
                        baseline_columns = df.columns.tolist()
                    else:
                        current_columns = df.columns.tolist()
                        if set(current_columns) != set(baseline_columns):
                            missing_in_current = [c for c in baseline_columns if c not in current_columns]
                            extra_in_current = [c for c in current_columns if c not in baseline_columns]
                            self.logger.error(
                                f"Column mismatch in {os.path.basename(file_path)}. "
                                f"Missing: {missing_in_current}; Extra: {extra_in_current}"
                            )
                            messagebox.showerror(
                                "Column Mismatch",
                                "Columns do not match across selected files.\n\n"
                                f"File: {os.path.basename(file_path)}\n"
                                f"Missing columns: {missing_in_current}\n"
                                f"Unexpected columns: {extra_in_current}"
                            )
                            return

                    # Ensure consistent column order
                    df = df.reindex(columns=baseline_columns)

                    dataframes.append(df)
                    self.logger.info(f"Successfully read {file_path}: {df.shape}")
                except Exception as e:
                    self.logger.error(f"Error reading {file_path}: {str(e)}")
                    messagebox.showerror("Error", f"Failed to read {os.path.basename(file_path)}: {str(e)}")
                    return
                    
            if not dataframes:
                messagebox.showerror("Error", "No valid CSV files to concatenate")
                return
                
            # Concatenate dataframes
            self.status_label.config(text="Concatenating dataframes...")
            self.progress_var.set(50)
            self.root.update()
            
            # Use concat with ignore_index to maintain data types
            concatenated_df = pd.concat(dataframes, ignore_index=True, sort=False)
            concatenated_df = concatenated_df.reindex(columns=baseline_columns)
            
            self.logger.info(f"Concatenated dataframe shape: {concatenated_df.shape}")
            
            # Save files
            self.status_label.config(text="Saving files...")
            self.progress_var.set(75)
            self.root.update()
            
            # Generate output filenames
            timestamp = pd.Timestamp.now().strftime("%Y%m%d_%H%M%S")
            csv_filename = f"concatenated_{timestamp}.csv"
            excel_filename = f"concatenated_{timestamp}.xlsx"
            
            csv_path = os.path.join(self.output_directory, csv_filename)
            excel_path = os.path.join(self.output_directory, excel_filename)
            
            # Save as CSV
            concatenated_df.to_csv(csv_path, index=False)
            self.logger.info(f"Saved CSV to: {csv_path}")
            
            # Save as Excel
            with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
                concatenated_df.to_excel(writer, sheet_name='Data', index=False)
            self.logger.info(f"Saved Excel to: {excel_path}")
            
            # Update progress and status
            self.progress_var.set(100)
            self.status_label.config(text="Concatenation completed successfully!", foreground="green")
            
            # Display results
            self.display_results(concatenated_df, csv_path, excel_path)
            
            messagebox.showinfo("Success", 
                              f"Files concatenated successfully!\n\n"
                              f"CSV saved to: {csv_filename}\n"
                              f"Excel saved to: {excel_filename}\n\n"
                              f"Total rows: {len(concatenated_df)}\n"
                              f"Total columns: {len(concatenated_df.columns)}")
                              
        except Exception as e:
            self.logger.error(f"Error during concatenation: {str(e)}")
            self.status_label.config(text=f"Error: {str(e)}", foreground="red")
            messagebox.showerror("Error", f"Concatenation failed: {str(e)}")
            
    def display_results(self, df, csv_path, excel_path):
        """Display concatenation results in the results text area"""
        self.results_text.delete(1.0, tk.END)
        
        results = f"CONCATENATION RESULTS\n"
        results += f"=" * 50 + "\n\n"
        
        results += f"Total rows: {len(df)}\n"
        results += f"Total columns: {len(df.columns)}\n\n"
        
        results += f"Column names:\n"
        for i, col in enumerate(df.columns):
            results += f"  {i+1}. {col}\n"
            
        results += f"\nData types:\n"
        for col, dtype in df.dtypes.items():
            results += f"  {col}: {dtype}\n"
            
        results += f"\nOutput files:\n"
        results += f"  CSV: {os.path.basename(csv_path)}\n"
        results += f"  Excel: {os.path.basename(excel_path)}\n"
        
        results += f"\nOutput directory:\n"
        results += f"  {self.output_directory}\n"
        
        self.results_text.insert(1.0, results)

    def launch_dashboard(self):
        """Launch the 3D visualization dashboard (app.py)"""
        if self.dashboard_running:
            messagebox.showwarning("Warning", "Dashboard is already running.")
            return

        try:
            self.dashboard_status_label.config(text="Dashboard: Launching...", foreground="orange")
            self.root.update()

            # Try to find app.py in the src directory
            app_path = "src/app.py"
            if not os.path.exists(app_path):
                app_path = "app.py"  # Fallback to current directory
            
            if not os.path.exists(app_path):
                messagebox.showerror("Error", "app.py not found. Please ensure it's in the src/ directory or current directory.")
                self.dashboard_status_label.config(text="Dashboard: Not found", foreground="red")
                return

            # Start the dashboard process - use shell=True to prevent immediate termination
            if os.name == 'nt':  # Windows
                self.dashboard_process = subprocess.Popen(
                    f'python "{app_path}"',
                    shell=True,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    creationflags=subprocess.CREATE_NEW_CONSOLE
                )
            else:  # Unix/Linux/Mac
                self.dashboard_process = subprocess.Popen(
                    ["python", app_path],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
            
            # Give the process more time to start
            time.sleep(3)
            
            # Check if the process started successfully
            if self.dashboard_process.poll() is not None:
                # Process terminated immediately
                error_msg = f"Dashboard failed to start. Process terminated with code: {self.dashboard_process.poll()}"
                self.logger.error(error_msg)
                messagebox.showerror("Dashboard Launch Failed", 
                                   f"{error_msg}\n\nThis usually means there's an error in app.py or missing dependencies.")
                self.dashboard_status_label.config(text="Dashboard: Failed to start", foreground="red")
                return
            
            self.dashboard_running = True
            self.launch_dashboard_btn.config(state=tk.DISABLED)
            self.stop_dashboard_btn.config(state=tk.NORMAL)
            self.open_browser_btn.config(state=tk.NORMAL)
            self.test_connection_btn.config(state=tk.NORMAL)
            self.dashboard_status_label.config(text="Dashboard: Running", foreground="green")
            self.logger.info(f"Dashboard launched successfully from {app_path}")

            # Open in browser after a longer delay to ensure server is ready
            threading.Thread(target=self.open_dashboard_in_browser_thread, daemon=True).start()

        except Exception as e:
            self.logger.error(f"Error launching dashboard: {str(e)}")
            self.dashboard_status_label.config(text=f"Dashboard: Error ({str(e)})", foreground="red")
            self.dashboard_running = False
            self.launch_dashboard_btn.config(state=tk.NORMAL)
            self.stop_dashboard_btn.config(state=tk.DISABLED)
            self.open_browser_btn.config(state=tk.DISABLED)
            self.test_connection_btn.config(state=tk.DISABLED)
            self.refresh_status_btn.config(state=tk.NORMAL)

    def stop_dashboard(self):
        """Stop the currently running dashboard process"""
        if self.dashboard_process and self.dashboard_running:
            try:
                # On Windows, we need to handle console processes differently
                if os.name == 'nt':
                    # Use taskkill to terminate the process tree
                    subprocess.run(['taskkill', '/F', '/T', '/PID', str(self.dashboard_process.pid)], 
                                 capture_output=True, timeout=10)
                else:
                    self.dashboard_process.terminate()
                    self.dashboard_process.wait(timeout=5)
                
                self.dashboard_running = False
                self.launch_dashboard_btn.config(state=tk.NORMAL)
                self.stop_dashboard_btn.config(state=tk.DISABLED)
                self.open_browser_btn.config(state=tk.NORMAL)
                self.test_connection_btn.config(state=tk.DISABLED)
                self.refresh_status_btn.config(state=tk.NORMAL)
                self.dashboard_status_label.config(text="Dashboard: Stopped", foreground="red")
                self.logger.info("Dashboard stopped successfully.")
                
            except subprocess.TimeoutExpired:
                if os.name == 'nt':
                    # Force kill on Windows
                    subprocess.run(['taskkill', '/F', '/PID', str(self.dashboard_process.pid)], 
                                 capture_output=True)
                else:
                    self.dashboard_process.kill()
                    self.dashboard_process.wait(timeout=5)
                
                self.dashboard_running = False
                self.launch_dashboard_btn.config(state=tk.NORMAL)
                self.stop_dashboard_btn.config(state=tk.DISABLED)
                self.open_browser_btn.config(state=tk.NORMAL)
                self.test_connection_btn.config(state=tk.DISABLED)
                self.refresh_status_btn.config(state=tk.NORMAL)
                self.dashboard_status_label.config(text="Dashboard: Stopped (force)", foreground="red")
                self.logger.warning("Dashboard stopped forcefully.")
            except Exception as e:
                self.logger.error(f"Error stopping dashboard: {str(e)}")
                self.dashboard_status_label.config(text=f"Dashboard: Error ({str(e)})", foreground="red")
                self.dashboard_running = False
                self.launch_dashboard_btn.config(state=tk.NORMAL)
                self.stop_dashboard_btn.config(state=tk.DISABLED)
                self.open_browser_btn.config(state=tk.NORMAL)
                self.test_connection_btn.config(state=tk.DISABLED)
                self.refresh_status_btn.config(state=tk.NORMAL)
        else:
            messagebox.showwarning("Warning", "Dashboard is not running.")

    def open_dashboard_in_browser(self):
        """Open the dashboard URL in the default web browser"""
        if self.dashboard_running:
            try:
                # app.py runs on port 8050 by default
                urls_to_try = [
                    "http://localhost:8050",  # Default Dash port (what app.py uses)
                    "http://127.0.0.1:8050",  # Alternative localhost
                    "http://localhost:5000",  # Fallback port
                    "http://127.0.0.1:5000"   # Fallback port
                ]
                
                for url in urls_to_try:
                    try:
                        webbrowser.open(url)
                        self.logger.info(f"Opened dashboard in browser at {url}")
                        return
                    except:
                        continue
                
                # If none of the common URLs work, show a message
                messagebox.showinfo("Dashboard URL", 
                                  "Dashboard launched! Please check your browser or manually navigate to:\n"
                                  "http://localhost:8050 (most likely)\n"
                                  "http://localhost:5000")
                
            except Exception as e:
                messagebox.showerror("Error", f"Could not open dashboard in browser: {str(e)}")
                self.logger.error(f"Failed to open dashboard in browser: {str(e)}")
        else:
            messagebox.showwarning("Warning", "Dashboard is not running. Cannot open in browser.")

    def open_dashboard_in_browser_thread(self):
        """Thread to open the dashboard URL in the browser"""
        time.sleep(5)  # Give the app more time to start up
        self.open_dashboard_in_browser()

    def check_dashboard_status(self):
        """Check if the dashboard process is still running"""
        if self.dashboard_process and self.dashboard_running:
            # On Windows, console processes behave differently
            if os.name == 'nt':
                # For Windows console processes, poll() might not work reliably
                # Instead, check if we can still connect to the dashboard
                if not self.test_connection():
                    # If we can't connect, the dashboard might have stopped
                    # But don't immediately assume it's dead - give it more time
                    pass
            else:
                # On Unix systems, check process status normally
                if self.dashboard_process.poll() is not None:
                    # Process has terminated
                    self.dashboard_running = False
                    self.launch_dashboard_btn.config(state=tk.NORMAL)
                    self.stop_dashboard_btn.config(state=tk.DISABLED)
                    self.open_browser_btn.config(state=tk.NORMAL)
                    self.test_connection_btn.config(state=tk.DISABLED)
                    self.refresh_status_btn.config(state=tk.NORMAL)
                    self.dashboard_status_label.config(text="Dashboard: Stopped unexpectedly", foreground="red")
                    self.logger.info("Dashboard process terminated unexpectedly")
        
        # Schedule the next check
        self.root.after(5000, self.check_dashboard_status)  # Check every 5 seconds instead of 2

    def test_connection(self):
        """Test if the dashboard is actually accessible"""
        import urllib.request
        import urllib.error
        
        if not self.dashboard_running:
            return False
            
        urls_to_test = [
            "http://localhost:8050",  # Primary port (what app.py uses)
            "http://127.0.0.1:8050",  # Alternative localhost
            "http://localhost:5000",  # Fallback port
            "http://127.0.0.1:5000"   # Fallback port
        ]
        
        for url in urls_to_test:
            try:
                response = urllib.request.urlopen(url, timeout=2)
                if response.getcode() == 200:
                    self.logger.info(f"Dashboard accessible at {url}")
                    return True
            except (urllib.error.URLError, urllib.error.HTTPError, Exception):
                continue
        
        return False

    def test_connection_clicked(self):
        """Wrapper for the test_connection method to update button state"""
        if self.test_connection():
            messagebox.showinfo("Connection Successful", "Dashboard is accessible at http://localhost:8050 (most likely).")
        else:
            messagebox.showwarning("Connection Failed", "Dashboard is not accessible at http://localhost:8050 (most likely). Please check if the dashboard is running and accessible.")

    def check_dashboard_process_status(self):
        """Check the detailed status of the dashboard process"""
        if not self.dashboard_process:
            return "No dashboard process found"
        
        try:
            # Check if process is still running
            if self.dashboard_process.poll() is None:
                return f"Process running (PID: {self.dashboard_process.pid})"
            else:
                returncode = self.dashboard_process.poll()
                return f"Process terminated with code: {returncode}"
        except Exception as e:
            return f"Error checking process: {str(e)}"

    def is_dashboard_healthy(self):
        """Check if the dashboard is healthy by testing connection and process"""
        if not self.dashboard_running:
            return False, "Dashboard not running"
        
        # Test connection first
        if self.test_connection():
            return True, "Dashboard accessible and responding"
        
        # If connection fails, check process status
        if self.dashboard_process and self.dashboard_process.poll() is None:
            return False, "Dashboard process running but not responding"
        else:
            return False, "Dashboard process not running"

    def refresh_dashboard_status(self):
        """Refresh the dashboard status label with detailed information"""
        healthy, status_msg = self.is_dashboard_healthy()
        if healthy:
            self.dashboard_status_label.config(text=f"Dashboard: Healthy ({status_msg})", foreground="green")
        else:
            self.dashboard_status_label.config(text=f"Dashboard: Unhealthy ({status_msg})", foreground="red")
        self.logger.info(f"Dashboard status refreshed: {status_msg}")

    def cleanup(self):
        """Clean up resources when closing the application"""
        if self.dashboard_process and self.dashboard_running:
            try:
                self.dashboard_process.terminate()
                self.dashboard_process.wait(timeout=3)
            except:
                if self.dashboard_process.poll() is None:
                    self.dashboard_process.kill()
            self.logger.info("Dashboard process cleaned up")

def main():
    """Main function to run the application"""
    root = tk.Tk()
    app = CSVConcatenatorApp(root)
    
    # Bind cleanup to window close event
    root.protocol("WM_DELETE_WINDOW", lambda: [app.cleanup(), root.destroy()])
    
    # Center the window
    root.update_idletasks()
    x = (root.winfo_screenwidth() // 2) - (root.winfo_width() // 2)
    y = (root.winfo_screenheight() // 2) - (root.winfo_height() // 2)
    root.geometry(f"+{x}+{y}")
    
    root.mainloop()

if __name__ == "__main__":
    main() 