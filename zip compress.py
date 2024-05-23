import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import zipfile
import os
import zlib

TARGET_SIZE_MB = 15
TARGET_SIZE_BYTES = TARGET_SIZE_MB * 1024 * 1024

def select_file():
    file_path = filedialog.askopenfilename(filetypes=[("ZIP files", "*.zip")])
    if file_path:
        entry_file_path.delete(0, tk.END)
        entry_file_path.insert(0, file_path)

def compress_zip():
    file_path = entry_file_path.get()
    if not file_path:
        messagebox.showerror("Error", "Please select a zip file to compress.")
        return

    output_path = file_path.replace(".zip", "_compressed.zip")
    compress_with_feedback(file_path, output_path)

def compress_with_feedback(file_path, output_path):
    with zipfile.ZipFile(file_path, 'r') as zip_ref:
        file_list = zip_ref.namelist()
        total_files = len(file_list)

        with zipfile.ZipFile(output_path, 'w', compression=zipfile.ZIP_DEFLATED) as new_zip_ref:
            for i, file_name in enumerate(file_list):
                with zip_ref.open(file_name) as original_file:
                    new_zip_ref.writestr(file_name, original_file.read())
                progress_var.set((i + 1) / total_files * 100)
                root.update_idletasks()

    final_size_mb = os.path.getsize(output_path) / (1024 * 1024)
    if final_size_mb <= TARGET_SIZE_MB:
        messagebox.showinfo("Success", f"File compressed successfully to {final_size_mb:.2f} MB and saved to {output_path}")
    else:
        retry = messagebox.askyesno("Warning", f"Compressed file is {final_size_mb:.2f} MB, which is larger than the target size of {TARGET_SIZE_MB} MB. Do you want to try further compression?")
        if retry:
            further_compress(output_path)

def further_compress(file_path):
    while True:
        temp_path = file_path.replace(".zip", "_temp.zip")
        with zipfile.ZipFile(file_path, 'r') as zip_ref:
            file_list = zip_ref.namelist()
            total_files = len(file_list)

            with zipfile.ZipFile(temp_path, 'w', compression=zipfile.ZIP_DEFLATED) as new_zip_ref:
                for i, file_name in enumerate(file_list):
                    with zip_ref.open(file_name) as original_file:
                        data = original_file.read()
                        compressed_data = zlib.compress(data, level=9)
                        new_zip_ref.writestr(file_name, compressed_data)
                    progress_var.set((i + 1) / total_files * 100)
                    root.update_idletasks()

        os.replace(temp_path, file_path)
        final_size_mb = os.path.getsize(file_path) / (1024 * 1024)
        if final_size_mb <= TARGET_SIZE_MB:
            messagebox.showinfo("Success", f"File further compressed successfully to {final_size_mb:.2f} MB and saved to {file_path}")
            break
        else:
            retry = messagebox.askyesno("Warning", f"Further compressed file is {final_size_mb:.2f} MB, which is still larger than the target size of {TARGET_SIZE_MB} MB. Do you want to try again?")
            if not retry:
                break

# Set up the GUI
root = tk.Tk()
root.title("ZIP Compressor")

# Create a frame for the file selection
frame = tk.Frame(root)
frame.pack(padx=10, pady=10)

# Add a label and entry for the file path
label_file_path = tk.Label(frame, text="ZIP File Path:")
label_file_path.grid(row=0, column=0, padx=5, pady=5)

entry_file_path = tk.Entry(frame, width=50)
entry_file_path.grid(row=0, column=1, padx=5, pady=5)

# Add a button to open the file dialog
button_browse = tk.Button(frame, text="Browse...", command=select_file)
button_browse.grid(row=0, column=2, padx=5, pady=5)

# Add a progress bar
progress_var = tk.DoubleVar()
progress_bar = ttk.Progressbar(root, variable=progress_var, maximum=100)
progress_bar.pack(padx=10, pady=10, fill=tk.X)

# Add a button to compress the zip file
button_compress = tk.Button(root, text="Compress", command=compress_zip)
button_compress.pack(padx=10, pady=10)

# Start the GUI event loop
root.mainloop()
