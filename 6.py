import tkinter as tk
from tkinter import messagebox, ttk
import json
import os
import subprocess

class BookTracker:
    def __init__(self, master):
        self.master = master
        master.title("Book Tracker")

        self.data_file = 'books.json'
        self.books = self.load_books()

        # --- Форма добавления книги ---
        self.form_frame = ttk.LabelFrame(master, text="Добавить книгу")
        self.form_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        ttk.Label(self.form_frame, text="Название:").grid(row=0, column=0, padx=5, pady=2, sticky="w")
        self.title_entry = ttk.Entry(self.form_frame, width=40)
        self.title_entry.grid(row=0, column=1, padx=5, pady=2, sticky="ew")

        ttk.Label(self.form_frame, text="Автор:").grid(row=1, column=0, padx=5, pady=2, sticky="w")
        self.author_entry = ttk.Entry(self.form_frame, width=40)
        self.author_entry.grid(row=1, column=1, padx=5, pady=2, sticky="ew")

        ttk.Label(self.form_frame, text="Жанр:").grid(row=2, column=0, padx=5, pady=2, sticky="w")
        self.genre_entry = ttk.Entry(self.form_frame, width=40)
        self.genre_entry.grid(row=2, column=1, padx=5, pady=2, sticky="ew")

        ttk.Label(self.form_frame, text="Кол-во страниц:").grid(row=3, column=0, padx=5, pady=2, sticky="w")
        self.pages_entry = ttk.Entry(self.form_frame, width=40)
        self.pages_entry.grid(row=3, column=1, padx=5, pady=2, sticky="ew")

        self.add_button = ttk.Button(self.form_frame, text="Добавить книгу", command=self.add_book)
        self.add_button.grid(row=4, column=0, columnspan=2, pady=10)

        # --- Таблица книг ---
        self.table_frame = ttk.LabelFrame(master, text="Список книг")
        self.table_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        self.tree = ttk.Treeview(self.table_frame, columns=("Title", "Author", "Genre", "Pages"), show="headings")
        self.tree.heading("Title", text="Название")
        self.tree.heading("Author", text="Автор")
        self.tree.heading("Genre", text="Жанр")
        self.tree.heading("Pages", text="Страницы")

        self.tree.column("Title", width=200)
        self.tree.column("Author", width=150)
        self.tree.column("Genre", width=100)
        self.tree.column("Pages", width=60, anchor="center")

        self.tree.grid(row=0, column=0, sticky="nsew")

        # --- Фильтрация ---
        self.filter_frame = ttk.LabelFrame(master, text="Фильтр")
        self.filter_frame.grid(row=0, column=1, rowspan=2, padx=10, pady=10, sticky="nsew")

        ttk.Label(self.filter_frame, text="Жанр:").grid(row=0, column=0, padx=5, pady=2, sticky="w")
        self.filter_genre_entry = ttk.Entry(self.filter_frame, width=20)
        self.filter_genre_entry.grid(row=0, column=1, padx=5, pady=2, sticky="ew")
        self.filter_genre_entry.bind("<KeyRelease>", self.apply_filters) # Фильтр по нажатию клавиши

        ttk.Label(self.filter_frame, text="Страниц >:").grid(row=1, column=0, padx=5, pady=2, sticky="w")
        self.filter_pages_entry = ttk.Entry(self.filter_frame, width=20)
        self.filter_pages_entry.grid(row=1, column=1, padx=5, pady=2, sticky="ew")
        self.filter_pages_entry.bind("<KeyRelease>", self.apply_filters)

        self.clear_filter_button = ttk.Button(self.filter_frame, text="Сбросить фильтр", command=self.clear_filters)
        self.clear_filter_button.grid(row=2, column=0, columnspan=2, pady=10)

        self.update_book_table() # Заполнение таблицы при старте

    def load_books(self):
        if os.path.exists(self.data_file):
            with open(self.data_file, 'r', encoding='utf-8') as f:
                try:
                    return json.load(f)
                except json.JSONDecodeError:
                    return []
        return []

    def save_books(self):
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(self.books, f, indent=4, ensure_ascii=False)

    def add_book(self):
        title = self.title_entry.get().strip()
        author = self.author_entry.get().strip()
        genre = self.genre_entry.get().strip()
        pages_str = self.pages_entry.get().strip()

        # Проверка ввода
        if not all([title, author, genre, pages_str]):
            messagebox.showwarning("Внимание", "Все поля должны быть заполнены.")
            return

        try:
            pages = int(pages_str)
            if pages <= 0:
                raise ValueError("Количество страниц должно быть положительным.")
        except ValueError as e:
            messagebox.showwarning("Внимание", f"Некорректное количество страниц: {e}")
            return

        new_book = {
            "title": title,
            "author": author,
            "genre": genre,
            "pages": pages
        }
        self.books.append(new_book)
        self.save_books()
        self.update_book_table()
        # Очистка полей ввода
        self.title_entry.delete(0, tk.END)
        self.author_entry.delete(0, tk.END)
        self.genre_entry.delete(0, tk.END)
        self.pages_entry.delete(0, tk.END)

    def update_book_table(self, data_to_display=None):
        # Очищаем таблицу
        for item in self.tree.get_children():
            self.tree.delete(item)

        books_to_show = data_to_display if data_to_display is not None else self.books
        for book in books_to_show:
            self.tree.insert("", tk.END, values=(
                book.get("title"), book.get("author"), book.get("genre"), book.get("pages")
            ))

    def apply_filters(self, event=None):
        filter_genre = self.filter_genre_entry.get().strip().lower()
        filter_pages_str = self.filter_pages_entry.get().strip()

        filtered_books = []
        try:
            filter_pages = int(filter_pages_str) if filter_pages_str else 0
        except ValueError:
            filter_pages = 0 # Если введено не число, игнорируем фильтр по страницам

        if not filter_genre and filter_pages == 0:
             self.update_book_table() # Показываем все, если фильтры пусты
             return

        for book in self.books:
            genre_match = not filter_genre or filter_genre in book.get("genre", "").lower()
            pages_match = not filter_pages_str or book.get("pages", 0) > filter_pages

            if genre_match and pages_match:
                filtered_books.append(book)

        self.update_book_table(filtered_books)

    def clear_filters(self):
        self.filter_genre_entry.delete(0, tk.END)
        self.filter_pages_entry.delete(0, tk.END)
        self.apply_filters() # Обновляем таблицу после очистки фильтров

# --- Функции Git ---
def setup_git_repo(repo_path="."):
    if not os.path.exists(os.path.join(repo_path, ".git")):
        subprocess.run(["git", "init"], cwd=repo_path, check=True)
        print("Git репозиторий инициализирован.")
    else:
        print("Git репозиторий уже существует.")

def create_gitignore(repo_path="."):
    gitignore_path = os.path.join(repo_path, ".gitignore")
    if not os.path.exists(gitignore_path):
        with open(gitignore_path, "w") as f:
            f.write("__pycache__/\n")
            f.write("*.pyc\n")
            f.write("books.json\n") # Не добавлять файл с данными в Git
        print(".gitignore создан.")

if __name__ == "__main__":
    setup_git_repo()
    create_gitignore()

    root = tk.Tk()
    app = BookTracker(root)
    root.mainloop()