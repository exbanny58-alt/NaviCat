import os
import tkinter as tk
from tkinter import filedialog

def select_folder_dialog():
    """Открыть диалог выбора папки через tkinter"""
    try:
        root = tk.Tk()
        root.withdraw()
        root.attributes('-topmost', True)
        
        folder_path = filedialog.askdirectory(
            title="Выберите папку",
            initialdir=os.path.expanduser("~")
        )
        
        root.destroy()
        return folder_path
    except Exception as e:
        print(f'❌ Ошибка tkinter: {e}')
        return None

def select_file_dialog():
    """Открыть диалог выбора файла через tkinter"""
    try:
        root = tk.Tk()
        root.withdraw()
        root.attributes('-topmost', True)
        
        file_path = filedialog.askopenfilename(
            title="Выберите файл",
            initialdir=os.path.expanduser("~"),
            filetypes=[
                ("Исполняемые файлы", "*.exe"),
                ("Все файлы", "*.*")
            ]
        )
        
        root.destroy()
        return file_path
    except Exception as e:
        print(f'❌ Ошибка tkinter: {e}')
        return None