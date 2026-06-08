import json
import os
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
from datetime import datetime



class BookModel:
   
    
    def __init__(self, filename="books_db.json"):
        self.filename = filename
        self.books = []
        self.backup_filename = "books_db_backup.json"
        self.load_data()
    
    def load_data(self):
      
        if os.path.exists(self.filename):
            try:
                with open(self.filename, 'r', encoding='utf-8') as f:
                    self.books = json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                print(f"Ошибка загрузки: {e}")
                self.books = []
        else:
            self.books = []
    
    def save_data(self):

        try:
            with open(self.filename, 'w', encoding='utf-8') as f:
                json.dump(self.books, f, ensure_ascii=False, indent=4)
            return True
        except IOError as e:
            print(f"Ошибка сохранения: {e}")
            return False
    
    def create_backup(self):
   
        try:
            with open(self.filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
            with open(self.backup_filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            return True
        except:
            return False
    
    def restore_backup(self):
    
        if os.path.exists(self.backup_filename):
            try:
                with open(self.backup_filename, 'r', encoding='utf-8') as f:
                    self.books = json.load(f)
                self.save_data()
                return True
            except:
                return False
        return False
    
    def add_book(self, title, genre, review, rating, author="", year=""):
     
        new_id = max([book['id'] for book in self.books], default=0) + 1
        book = {
            'id': new_id,
            'title': title.strip(),
            'genre': genre,
            'review': review.strip(),
            'rating': rating,
            'author': author.strip(),
            'year': year.strip(),
            'date_added': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'date_modified': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        self.books.append(book)
        self.save_data()
        return new_id
    
    def update_book(self, book_id, title, genre, review, rating, author="", year=""):
     
        for book in self.books:
            if book['id'] == book_id:
                book['title'] = title.strip()
                book['genre'] = genre
                book['review'] = review.strip()
                book['rating'] = rating
                book['author'] = author.strip()
                book['year'] = year.strip()
                book['date_modified'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                self.save_data()
                return True
        return False
    
    def delete_book(self, book_id):
      
        for i, book in enumerate(self.books):
            if book['id'] == book_id:
                del self.books[i]
                self.save_data()
                return True
        return False
    
    def get_all_books(self):
   
        return self.books.copy()
    
    def get_book_by_id(self, book_id):
       
        for book in self.books:
            if book['id'] == book_id:
                return book.copy()
        return None
    
    def search_books(self, keyword):
        
        keyword_lower = keyword.strip().lower()
        if not keyword_lower:
            return self.get_all_books()
        return [book for book in self.books if 
                keyword_lower in book['title'].lower() or
                keyword_lower in book.get('author', '').lower() or
                keyword_lower in book.get('genre', '').lower()]
    
    def export_to_json(self, filename):
   
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.books, f, ensure_ascii=False, indent=4)
            return True
        except:
            return False
    
    def import_from_json(self, filename):
     
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                imported_books = json.load(f)
            for book in imported_books:
                if 'id' not in book:
                    book['id'] = max([b['id'] for b in self.books], default=0) + 1
            self.books.extend(imported_books)
            self.save_data()
            return True
        except:
            return False



class BookApp:
  
    
  
    GENRES = [
        "Роман", "Детектив", "Фантастика", "Фэнтези", "Научная литература",
        "Биография", "Поэзия", "Драма", "Приключения", "Ужасы", "Триллер", "История",
        "Психология", "Философия", "Публицистика", "Сатира", "Комедия", "Трагедия"
    ]
    
    def __init__(self, root):
        self.root = root
        self.root.title("Мои любимые книги")
        self.root.geometry("1400x800")
        self.root.minsize(1200, 700)
        

        self.root.configure(bg="#1a0b2e")
        
        self.model = BookModel()
        self.current_book_id = None
        
        self.create_menu()
        self.create_widgets()
        self.create_status_bar()
        
        self.refresh_books_table()
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def create_menu(self):
     
        menubar = tk.Menu(self.root, bg="#1a0b2e", fg="white")
        self.root.config(menu=menubar)
        

        file_menu = tk.Menu(menubar, tearoff=0, bg="#1a0b2e", fg="white")
        menubar.add_cascade(label="Файл", menu=file_menu)
        file_menu.add_command(label="Экспорт в JSON", command=self.export_data)
        file_menu.add_command(label="Импорт из JSON", command=self.import_data)
        file_menu.add_separator()
        file_menu.add_command(label="Создать резервную копию", command=self.create_backup)
        file_menu.add_command(label="Восстановить из резервной копии", command=self.restore_backup)
        file_menu.add_separator()
        file_menu.add_command(label="Выход", command=self.on_closing)
        
      
     
    
    def create_widgets(self):
      
        main_paned = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        main_paned.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
      
        left_frame = ttk.LabelFrame(main_paned, text="Информация о книге", padding=10)
        main_paned.add(left_frame, weight=1)
        

        ttk.Label(left_frame, text="Название книги:", font=('Arial', 10, 'bold')).grid(row=0, column=0, sticky=tk.W, pady=5)
        self.title_entry = ttk.Entry(left_frame, width=45, font=('Arial', 10))
        self.title_entry.grid(row=0, column=1, pady=5, padx=5, sticky=tk.W)
        
      
        ttk.Label(left_frame, text="Автор:", font=('Arial', 10, 'bold')).grid(row=1, column=0, sticky=tk.W, pady=5)
        self.author_entry = ttk.Entry(left_frame, width=45, font=('Arial', 10))
        self.author_entry.grid(row=1, column=1, pady=5, padx=5, sticky=tk.W)
        
  
        ttk.Label(left_frame, text="Год издания:", font=('Arial', 10, 'bold')).grid(row=2, column=0, sticky=tk.W, pady=5)
        self.year_entry = ttk.Entry(left_frame, width=20, font=('Arial', 10))
        self.year_entry.grid(row=2, column=1, pady=5, padx=5, sticky=tk.W)
        
   
        ttk.Label(left_frame, text="Жанр:", font=('Arial', 10, 'bold')).grid(row=3, column=0, sticky=tk.W, pady=5)
        
      
        genre_frame = tk.Frame(left_frame, bg="#1a0b2e")
        genre_frame.grid(row=3, column=1, pady=5, padx=5, sticky=tk.W)
        
        self.genre_var = tk.StringVar()
        self.genre_combo = ttk.Combobox(genre_frame, textvariable=self.genre_var, 
                                        values=self.GENRES, width=35)
        self.genre_combo.pack(side=tk.LEFT)
        
     
        self.custom_genre_entry = tk.Entry(genre_frame, width=15, font=('Arial', 9), bg="#2d1b4e", fg="white", insertbackground="white")
        self.custom_genre_entry.pack(side=tk.LEFT, padx=5)
        self.custom_genre_entry.bind('<Return>', self.add_custom_genre)
        
        ttk.Button(genre_frame, text="Свой жанр", command=self.add_custom_genre, width=10).pack(side=tk.LEFT, padx=5)
        
        
        ttk.Label(left_frame, text="Оценка (1-5):", font=('Arial', 10, 'bold')).grid(row=4, column=0, sticky=tk.W, pady=10)
        
        rating_frame = tk.Frame(left_frame, bg="#1a0b2e")
        rating_frame.grid(row=4, column=1, sticky=tk.W, pady=5, padx=5)
        
        self.rating_var = tk.IntVar(value=5)
        self.star_buttons = []
        
        for i in range(1, 6):
            star_btn = tk.Button(rating_frame, text="★", font=('Arial', 18), 
                                command=lambda x=i: self.set_rating(x),
                                bg="gold", fg="darkorange", width=2)
            star_btn.pack(side=tk.LEFT, padx=2)
            self.star_buttons.append(star_btn)
        
        self.rating_label = tk.Label(rating_frame, text="Оценка: 5", font=('Arial', 10, 'bold'), bg="#1a0b2e", fg="white")
        self.rating_label.pack(side=tk.LEFT, padx=10)
        
  
        ttk.Label(left_frame, text="Моё мнение (можно писать много текста):", font=('Arial', 10, 'bold')).grid(row=5, column=0, sticky=tk.NW, pady=5)
        
       
        review_frame = tk.Frame(left_frame, bg="#1a0b2e")
        review_frame.grid(row=5, column=1, pady=5, padx=5, sticky=tk.W)
        
        self.review_text = tk.Text(review_frame, width=50, height=18, wrap=tk.WORD, 
                                   font=('Arial', 10), padx=5, pady=5, bg="#2d1b4e", fg="white", insertbackground="white")
        self.review_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        review_scrollbar = tk.Scrollbar(review_frame, command=self.review_text.yview, bg="#1a0b2e")
        review_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.review_text.config(yscrollcommand=review_scrollbar.set)
        
  
        tip_label = tk.Label(left_frame, text="💡 Совет: Нажимайте Enter для новых абзацев. Текст автоматически переносится.", 
                            font=('Arial', 8), fg="#ffd46b", bg="#1a0b2e", wraplength=300)
        tip_label.grid(row=6, column=1, sticky=tk.W, padx=5, pady=5)
        
      
        btn_frame = tk.Frame(left_frame, bg="#1a0b2e")
        btn_frame.grid(row=7, column=0, columnspan=2, pady=15)
        
        self.add_btn = tk.Button(btn_frame, text=" Добавить книгу", command=self.add_book, 
                                width=15, bg="lightgreen", font=('Arial', 9, 'bold'))
        self.add_btn.pack(side=tk.LEFT, padx=5)
        
        self.update_btn = tk.Button(btn_frame, text="Обновить", command=self.update_book, 
                                   state=tk.DISABLED, width=15, bg="lightblue", font=('Arial', 9, 'bold'))
        self.update_btn.pack(side=tk.LEFT, padx=5)
        
        self.cancel_btn = tk.Button(btn_frame, text="Отменить", command=self.cancel_edit, 
                                   state=tk.DISABLED, width=15, bg="lightgray", font=('Arial', 9, 'bold'))
        self.cancel_btn.pack(side=tk.LEFT, padx=5)
        
        self.clear_btn = tk.Button(btn_frame, text="Очистить", command=self.clear_form, 
                                  width=15, font=('Arial', 9, 'bold'))
        self.clear_btn.pack(side=tk.LEFT, padx=5)
        
       
        right_frame = ttk.LabelFrame(main_paned, text="Мои книги", padding=5)
        main_paned.add(right_frame, weight=2)
        
    
        search_frame = tk.Frame(right_frame, bg="#1a0b2e")
        search_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(search_frame, text=" Поиск:", font=('Arial', 9, 'bold'), bg="#1a0b2e", fg="white").pack(side=tk.LEFT, padx=5)
        self.search_entry = tk.Entry(search_frame, width=40, font=('Arial', 9), bg="#2d1b4e", fg="white", insertbackground="white")
        self.search_entry.pack(side=tk.LEFT, padx=5)
        self.search_entry.bind("<KeyRelease>", lambda e: self.search_books())
        
        tk.Button(search_frame, text="Искать", command=self.search_books, width=10, 
                 bg="lightblue").pack(side=tk.LEFT, padx=2)
        tk.Button(search_frame, text="Сброс", command=self.reset_search, width=10).pack(side=tk.LEFT, padx=2)
        
    
        columns = ("id", "title", "author", "genre", "rating", "year")
        self.tree = ttk.Treeview(right_frame, columns=columns, show="headings", height=25)
        
        self.tree.heading("id", text="ID")
        self.tree.heading("title", text="Название")
        self.tree.heading("author", text="Автор")
        self.tree.heading("genre", text="Жанр")
        self.tree.heading("rating", text="Оценка")
        self.tree.heading("year", text="Год")
        
        self.tree.column("id", width=50, anchor=tk.CENTER)
        self.tree.column("title", width=250)
        self.tree.column("author", width=180)
        self.tree.column("genre", width=150)
        self.tree.column("rating", width=100, anchor=tk.CENTER)
        self.tree.column("year", width=80, anchor=tk.CENTER)
        
  
        style = ttk.Style()
        style.configure("Treeview", background="#2d1b4e", foreground="white", fieldbackground="#2d1b4e")
        style.configure("Treeview.Heading", background="#1a0b2e", foreground="white")
        
        scrollbar_y = ttk.Scrollbar(right_frame, orient=tk.VERTICAL, command=self.tree.yview)
        scrollbar_x = ttk.Scrollbar(right_frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)
        
        self.tree.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
        scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)
        
       
        self.tree.bind("<<TreeviewSelect>>", self.on_select_book)
        self.tree.bind("<Double-1>", self.view_full_review)
        
    
        control_frame = tk.Frame(right_frame, bg="#1a0b2e")
        control_frame.pack(fill=tk.X, pady=5)
        
        tk.Button(control_frame, text="Редактировать", command=self.edit_selected, 
                bg="lightblue", width=14, font=('Arial', 9)).pack(side=tk.LEFT, padx=5)
        tk.Button(control_frame, text=" Удалить", command=self.delete_selected, 
                bg="lightcoral", width=14, font=('Arial', 9)).pack(side=tk.LEFT, padx=5)
        tk.Button(control_frame, text=" Обновить", command=self.refresh_books_table, 
                width=14, font=('Arial', 9)).pack(side=tk.LEFT, padx=5)
        tk.Button(control_frame, text=" Читать полное мнение", command=self.view_full_review, 
                width=20, font=('Arial', 9), bg="lightyellow").pack(side=tk.LEFT, padx=5)
    
    def add_custom_genre(self, event=None):

        custom_genre = self.custom_genre_entry.get().strip()
        if custom_genre:
            current_values = list(self.genre_combo['values'])
            if custom_genre not in current_values:
                current_values.append(custom_genre)
                current_values.sort()
                self.genre_combo['values'] = current_values
            self.genre_var.set(custom_genre)
            self.custom_genre_entry.delete(0, tk.END)
            self.update_status(f"Жанр '{custom_genre}' добавлен")
        else:
            messagebox.showwarning("Ошибка", "Введите название жанра!")
    
    def set_rating(self, value):
       
        self.rating_var.set(value)
        self.rating_label.config(text=f"Оценка: {value}")
        
        for i, btn in enumerate(self.star_buttons):
            if i < value:
                btn.config(text="★", bg="gold", fg="darkorange")
            else:
                btn.config(text="☆", bg="lightgray", fg="gray")
    
    def create_status_bar(self):
      
        self.status_bar = tk.Label(self.root, text="Готов к работе", relief=tk.SUNKEN, anchor=tk.W, 
                                   font=('Arial', 9), bg="#1a0b2e", fg="white")
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def update_status(self, message):
  
        self.status_bar.config(text=message)
        self.root.update_idletasks()
    
    def refresh_books_table(self, books_list=None):
      
        if books_list is None:
            books_list = self.model.get_all_books()
        
    
        for item in self.tree.get_children():
            self.tree.delete(item)
        
    
        for book in books_list:
          
            stars = "★" * book['rating'] + "☆" * (5 - book['rating'])
            
            self.tree.insert("", tk.END, values=(
                book['id'],
                book['title'],
                book.get('author', ''),
                book['genre'],
                stars,
                book.get('year', '')
            ), tags=(book['id'],))
        
        self.update_status(f"Загружено книг: {len(books_list)}")
    
    def search_books(self):
   
        keyword = self.search_entry.get()
        results = self.model.search_books(keyword)
        self.refresh_books_table(results)
        self.update_status(f"Найдено книг: {len(results)}")
    
    def reset_search(self):
    
        self.search_entry.delete(0, tk.END)
        self.refresh_books_table()
        self.update_status("Поиск сброшен")
    
    def clear_form(self):
  
        self.title_entry.delete(0, tk.END)
        self.author_entry.delete(0, tk.END)
        self.year_entry.delete(0, tk.END)
        self.genre_var.set("")
        self.custom_genre_entry.delete(0, tk.END)
        self.set_rating(5)
        self.review_text.delete(1.0, tk.END)
        self.current_book_id = None
        
        self.add_btn.config(state=tk.NORMAL)
        self.update_btn.config(state=tk.DISABLED)
        self.cancel_btn.config(state=tk.DISABLED)
        
        self.update_status("Форма очищена")
    
    def add_book(self):
      
        title = self.title_entry.get().strip()
        genre = self.genre_var.get().strip()
        review = self.review_text.get(1.0, tk.END).strip()
        rating = self.rating_var.get()
        author = self.author_entry.get().strip()
        year = self.year_entry.get().strip()
        
        if not title:
            messagebox.showwarning("Ошибка", "Название книги не может быть пустым!")
            return
        
        if not genre:
            genre = "Не указан"
        
        if not review:
            review = "Мнение не оставлено"
        
        if year and not year.isdigit():
            messagebox.showwarning("Ошибка", "Год издания должен быть числом!")
            return
        
   
        current_genres = list(self.genre_combo['values'])
        if genre not in current_genres:
            current_genres.append(genre)
            current_genres.sort()
            self.genre_combo['values'] = current_genres
        
        self.model.add_book(title, genre, review, rating, author, year)
        messagebox.showinfo("Успех", f"Книга '{title}' добавлена!")
        self.clear_form()
        self.refresh_books_table()
        self.reset_search()
        self.update_status(f"Книга '{title}' успешно добавлена")
    
    def on_select_book(self, event):
       
        selected = self.tree.selection()
        if not selected:
            return
        values = self.tree.item(selected[0], 'values')
        if values:
            self.selected_book_id = int(values[0])
    
    def view_full_review(self, event=None):
      
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Сначала выберите книгу!")
            return
        
        values = self.tree.item(selected[0], 'values')
        book_id = int(values[0])
        book = self.model.get_book_by_id(book_id)
        
        if book:
       
            review_window = tk.Toplevel(self.root)
            review_window.title(f"Мнение о книге: {book['title']}")
            review_window.geometry("700x600")
            review_window.configure(bg="#1a0b2e")
            
   
            main_frame = tk.Frame(review_window, bg="#1a0b2e")
            main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
          
            info_frame = tk.Frame(main_frame, bg="#2d1b4e", relief=tk.RAISED, bd=2)
            info_frame.pack(fill=tk.X, pady=(0, 10))
            
            stars = "★" * book['rating'] + "☆" * (5 - book['rating'])
            
            info_text = f" {book['title']}\n"
            if book.get('author'):
                info_text += f" {book['author']}\n"
            info_text += f" {book['genre']}  |  {stars} ({book['rating']}/5)"
            if book.get('year'):
                info_text += f"  | {book['year']}"
            
            info_label = tk.Label(info_frame, text=info_text, font=('Arial', 12, 'bold'), 
                                 bg="#2d1b4e", fg="#ff6b9d", pady=10)
            info_label.pack()
       
            tk.Label(main_frame, text="Моё мнение:", font=('Arial', 11, 'bold'), bg="#1a0b2e", fg="#6bff9d").pack(anchor=tk.W)
            
            text_frame = tk.Frame(main_frame, bg="#1a0b2e")
            text_frame.pack(fill=tk.BOTH, expand=True, pady=5)
            
            review_display = tk.Text(text_frame, wrap=tk.WORD, font=('Arial', 11), 
                                     padx=10, pady=10, bg="#2d1b4e", fg="white")
            review_display.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            
            scrollbar = tk.Scrollbar(text_frame, command=review_display.yview, bg="#1a0b2e")
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            review_display.config(yscrollcommand=scrollbar.set)
            
    
            review_display.insert(1.0, book['review'])
            review_display.config(state=tk.DISABLED)
            

            tk.Button(main_frame, text="Закрыть", command=review_window.destroy, 
                     width=15, bg="lightgray", font=('Arial', 9)).pack(pady=10)
    
    def edit_selected(self):
      
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Сначала выберите книгу для редактирования!")
            return
        
        values = self.tree.item(selected[0], 'values')
        book_id = int(values[0])
        book = self.model.get_book_by_id(book_id)
        
        if book:
            self.current_book_id = book['id']
            self.title_entry.delete(0, tk.END)
            self.title_entry.insert(0, book['title'])
            self.author_entry.delete(0, tk.END)
            self.author_entry.insert(0, book.get('author', ''))
            self.year_entry.delete(0, tk.END)
            self.year_entry.insert(0, book.get('year', ''))
            self.genre_var.set(book['genre'])
            self.set_rating(book['rating'])
            self.review_text.delete(1.0, tk.END)
            self.review_text.insert(1.0, book['review'])
            
            self.add_btn.config(state=tk.DISABLED)
            self.update_btn.config(state=tk.NORMAL)
            self.cancel_btn.config(state=tk.NORMAL)
            
            self.update_status(f"Редактирование книги: {book['title']}")
    
    def update_book(self):
   
        if self.current_book_id is None:
            return
        
        title = self.title_entry.get().strip()
        genre = self.genre_var.get().strip()
        review = self.review_text.get(1.0, tk.END).strip()
        rating = self.rating_var.get()
        author = self.author_entry.get().strip()
        year = self.year_entry.get().strip()
        
        if not title:
            messagebox.showwarning("Ошибка", "Название не может быть пустым!")
            return
        
        if not genre:
            genre = "Не указан"
        
        if not review:
            review = "Мнение не оставлено"
        
        if year and not year.isdigit():
            messagebox.showwarning("Ошибка", "Год издания должен быть числом!")
            return
        
        self.model.update_book(self.current_book_id, title, genre, review, rating, author, year)
        messagebox.showinfo("Успех", "Книга обновлена!")
        self.clear_form()
        self.refresh_books_table()
        self.reset_search()
        self.update_status("Книга успешно обновлена")
    
    def cancel_edit(self):
      
        self.clear_form()
    
    def delete_selected(self):
   
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите книгу для удаления!")
            return
        
        values = self.tree.item(selected[0], 'values')
        book_id = int(values[0])
        title = values[1]
        
        if messagebox.askyesno("Подтверждение", f"Удалить книгу '{title}'?"):
            self.model.delete_book(book_id)
            messagebox.showinfo("Успех", "Книга удалена!")
            self.refresh_books_table()
            self.reset_search()
            if self.current_book_id == book_id:
                self.clear_form()
            self.update_status(f"Книга '{title}' удалена")
    
    def export_data(self):
  
        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if filename:
            if self.model.export_to_json(filename):
                messagebox.showinfo("Успех", "Данные успешно экспортированы!")
                self.update_status(f"Данные экспортированы в {filename}")
            else:
                messagebox.showerror("Ошибка", "Не удалось экспортировать данные!")
    
    def import_data(self):
       
        filename = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if filename:
            if messagebox.askyesno("Подтверждение", "Импорт добавит книги к существующим. Продолжить?"):
                if self.model.import_from_json(filename):
                    messagebox.showinfo("Успех", "Данные успешно импортированы!")
                    self.refresh_books_table()
                    self.update_status(f"Данные импортированы из {filename}")
                else:
                    messagebox.showerror("Ошибка", "Не удалось импортировать данные!")
    
    def create_backup(self):
      
        if self.model.create_backup():
            messagebox.showinfo("Успех", "Резервная копия создана!")
            self.update_status("Резервная копия создана")
        else:
            messagebox.showerror("Ошибка", "Не удалось создать резервную копию!")
    
    def restore_backup(self):
     
        if messagebox.askyesno("Подтверждение", "Восстановление удалит текущие данные. Продолжить?"):
            if self.model.restore_backup():
                messagebox.showinfo("Успех", "Данные восстановлены из резервной копии!")
                self.refresh_books_table()
                self.update_status("Данные восстановлены из резервной копии")
            else:
                messagebox.showerror("Ошибка", "Не удалось восстановить данные!")
    
  
    
    def on_closing(self):
      
        if messagebox.askokcancel("Выход", "Закрыть программу?"):
            self.model.save_data()
            self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = BookApp(root)
    root.mainloop()