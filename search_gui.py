import os
import threading
import subprocess
import sys
from tkinter import *
from tkinter import ttk, filedialog, messagebox

class SearchApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Поиск текста в файлах")
        self.root.geometry("800x800")

        self.dir_path = StringVar()
        self.search_text = StringVar()
        self.extensions = StringVar(value=".txt")

        self.stop_search = False

        self.create_widgets()

    def create_widgets(self):
        frame_top = ttk.Frame(self.root, padding="5")
        frame_top.pack(fill=X)

        #dirs
        ttk.Label(frame_top, text="Каталог:").grid(row=0, column=0, sticky=W, padx=5, pady=5)
        ttk.Entry(frame_top, textvariable=self.dir_path, width=50).grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(frame_top, text="Обзор", command=self.browse_folder).grid(row=0, column=2, padx=5, pady=5)

        #Текст для поиска
        ttk.Label(frame_top, text="Искать").grid(row=1, column=0, sticky=W, padx=5, pady=5)
        ttk.Entry(frame_top, textvariable=self.search_text, width=50).grid(row=1, column=1, padx=5, pady=5)

        # extensions
        ttk.Label(frame_top, text="Расширение (через запятую):").grid(row=2, column=0, sticky=W, padx=5, pady=5)
        ttk.Entry(frame_top, textvariable=self.extensions, width=50).grid(row=2, column=1, padx=5, pady=5)

        # Кнопка поиска и прогресс
        self.btn_search = ttk.Button(frame_top, text="Найти", command=self.start_search)
        self.btn_search.grid(row=3, column=1, pady=10)

        self.btn_stop = ttk.Button(frame_top, text="Остановить", command=self.stop_searching, state=DISABLED)
        self.btn_stop.grid(row=3, column=2, pady=10)

        # Результат
        frame_result = ttk.Frame(self.root, padding="5")
        frame_result.pack(fill=BOTH, expand=True)

        columns = ("file", "line", "content")
        self.tree = ttk.Treeview(frame_result, columns=columns, show="headings")
        self.tree.heading("file", text="Файл")
        self.tree.heading("line", text="Строка")
        self.tree.heading("content", text="Содержимое")
        self.tree.column("file", width=300)
        self.tree.column("line", width=60, anchor=CENTER)
        self.tree.column("content", width=400)

        # Scrollbar
        vsb = ttk.Scrollbar(frame_result, orient=VERTICAL, command=self.tree.yview)
        hsb = ttk.Scrollbar(frame_result, orient=HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        self.tree.grid(row=0, column=0, sticky=NSEW)
        vsb.grid(row=0, column=1, sticky=NS)
        hsb.grid(row=1, column=0, sticky=EW)
        
        frame_result.grid_rowconfigure(0, weight=1)
        frame_result.grid_columnconfigure(0, weight=1)

        # double click - open file
        self.tree.bind("<Double-1>", self.open_file)

        self.status = ttk.Label(self.root, text="Готов", relief=SUNKEN, anchor=W)
        self.status.pack(side=BOTTOM, fill=X)

    def browse_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.dir_path.set(folder)

    def start_search(self):
        dir = self.dir_path.get().strip()
        text = self.search_text.get().strip()
        exts = self.extensions.get().strip()

        if not dir:
            messagebox.showerror("Ошибка", "Укажите папку для поиска")
            return
        if not os.path.isdir(dir):
            messagebox.showerror("Ошибка", "Указанная папка не существует")
            return
        if not text:
            messagebox.showerror("Ошибка", "Укажите текст для поиска")
            return

        for item in self.tree.get_children():
            self.tree.delete(item)
        
        extensions = [ext.strip().lower() for ext in exts.split(",") if ext.strip()]
        if not extensions:
            extensions = None

        self.btn_search.config(state=DISABLED)
        self.btn_stop.config(state=NORMAL)
        self.stop_search = False

        self.status.config(text="Поиск...")

        thread = threading.Thread(target=self.search_thread, args=(dir, text, extensions))
        thread.daemon = True
        thread.start()

    def search_thread(self, dir, search_text, exts):
        total = 0
        try:
            for root, dirs, files in os.walk(dir):
                if self.stop_search:
                    break
                for file in files:
                    if self.stop_search:
                        break
                    filepath = os.path.join(root, file)
                    if exts:
                        ext = os.path.splitext(file)[1].lower()
                        if ext not in exts:
                            continue

                    try:
                        with open(filepath, 'r', encoding='utf-8') as f:
                            for line_num, line in enumerate(f, start=1):
                                if self.stop_search:
                                    break
                                if search_text in line:
                                    self.root.after(0, self.add_result, filepath, line_num, line.rstrip())
                                    total+=1
                    except (UnicodeDecodeError, PermissionError, OSError):
                        continue
        except Exception as e:
            self.root.after(0, messagebox.showerror, "Ошибка", str(e))
        finally:
            self.root.after(0, self.search_finished, total)

    def add_result(self, filepath, line_num, line_content):
        self.tree.insert("", END, values=(filepath, line_num, line_content))

    
    def search_finished(self, total):
        self.btn_search.config(state=NORMAL)
        self.btn_stop.config(state=DISABLED)
        self.stop_search = False
        self.status.config(text=f"Поиск завершен. Найдено вхождений: {total}")

    def stop_searching(self):
        self.stop_search = True
        self.status.config(text="Останавливаю...")
        self.btn_stop.config(state="DISABLED")

    def open_file(self, event):
        selection = self.tree.selection()
        if not selection:
            return
        
        item = self.tree.item(selection[0])
        filepath = item['values'][0]
        line_num = item['values'][1]

        try:
            if sys.platform.startswith('win'):
                os.startfile(filepath)
            elif sys.platform.startswith('darwin'):
                subprocess.run(['open', filepath])
            else:
                subprocess.run(['xdg-open', filepath])
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось открыть файл: {e}")

def main():
    root = Tk()
    app = SearchApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()



