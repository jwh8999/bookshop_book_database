# This program requires the following packages:
# fuzzywuzzy
# python-Levenshtein
# tabulate
# To install:
# pip install fuzzywuzzy
# pip install python-Levenshtein
# pip install tabulate

# Needed for database
import sqlite3
# Needed for displaying tables in an attractive format
from tabulate import tabulate
# Needed for the search function
from fuzzywuzzy import fuzz, process


# ---Functions---

def add_book(title, author, quantity):
    '''
    This function will add a new book to the database using a SQL statement.
    
    :param: title : str : The title of the new book.
    :param: author : str : The author of the new book.
    :param: quantity : int : The number of copies of the new book.    
    '''
    
    with sqlite3.connect('bookshop_database') as book_db:
        cursor = book_db.cursor()
        cursor.execute('''INSERT INTO book(title,author,quantity) VALUES(?,?,?)''', (title,author,qty))
        book_db.commit()
    
    

def update_book_qty(new_qty, book_id):
    '''
    This function will update the values of a book in the database using a SQL statement.
    
    :param: new_qty : int : The number of copies of the book.
    :param: book_id : int : The id of the book to be updated. 
    '''
    with sqlite3.connect('bookshop_database') as book_db:
        cursor = book_db.cursor()
        cursor.execute(f'UPDATE book SET Quantity = {new_qty} WHERE id = {book_id}')
                       
    
def edit_book(book_id, new_title, author_or_title):
    '''
    This function will edit a field in the table based on the user's selected book and new title or author value.
    
    :param: book_id : int : The ID of the book to update
    :param: new_title : str : The new title or author name
    :param: author_or_title : str : a string 'author' or 'title'. 
    This is inserted in the SQL statement to update either the author or title field for that book.    
    '''
    with sqlite3.connect('bookshop_database') as book_db:
        cursor = book_db.cursor()
        cursor.execute(f'UPDATE book SET {author_or_title} = "{new_title}" WHERE id = {book_id}')
        
        
def delete_book(delete_id):
    '''
    This function will delete a book in the database using a SQL statement.
    
    :param: delete_id : int : The id of the book to delete.
    '''
    with sqlite3.connect('bookshop_database') as book_db:
        cursor = book_db.cursor()
        cursor.execute('''DELETE FROM book WHERE id = ?''', (delete_id,))
        book_db.commit()

def match_title_author(search_term):
    '''
    This function will search for a book in the database.
    
    :param: search_term : str : The user's query to search in the author or title fields of the table.
    :return: list : best_matches_id : A list containing the id of the best matching book for the user's search query.
    '''
    # Everything in the table is selected to be searched and stored as to_search
    with sqlite3.connect('bookshop_database') as book_db:
        cursor = book_db.cursor()
        cursor.execute('''SELECT id, title, author FROM book''')
        to_search = cursor.fetchall()
    
    to_search_list = []
    # to_search is converted into a list
    for row in to_search:
        to_search_list.append(row)
    
    # process.extract() is used to assign a number based on how much each item in the table matches the user's search term.
    matches = process.extract(search_term, to_search_list)
    best_matches = []
    # If the match was above 80 it's considered a match and the match is added to the best_matches list
    for result in matches:
        if result[1] >= 80:
            best_matches.append(result)
    best_matches_id = []
    # The id of each of the best matches is stored in a list
    for item in best_matches:
        best_matches_id.append(item[0][0])
    return best_matches_id
        

def return_books(id_list):
    '''
    Returns a list of the desired books in the database.
    
    :param: id_list : list, int or empty : The list of ids (or single book id) to return. 
    If it is empty it will return everything in the table.
    
    :return: selected_rows : list : The list of books selected by the user.
    '''
    with sqlite3.connect('bookshop_database') as book_db:
        cursor = book_db.cursor()
        # If the id_list is empty then everything will be returned
        if not id_list:
            cursor.execute('SELECT * FROM book')
            selected_rows = cursor.fetchall()
            return selected_rows
        # If the id_list type is an int then this SQL statement is correct for when the id is passed as an integer
        elif type(id_list) == int:
            cursor.execute(f'SELECT * FROM book WHERE id = {id_list}')
            selected_rows = cursor.fetchall()
            return selected_rows
        # Passes id_list to the SQL statement
        # The number of '?'s is calculated based on how many are needed for each id in the list.
        cursor.execute(f'SELECT * FROM book WHERE id IN ({",".join("?" * len(id_list))})', id_list)
        selected_rows = cursor.fetchall()
    return selected_rows
    
# ---Database Creation---

# If the table does not already exist then this code will create a new one
# It will contain:
# id : int : primary key : autoincrement (so that each primary key is unique)
# title : str
# author : str
# Quantity : int
with sqlite3.connect('bookshop_database') as book_db:
    cursor = book_db.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS book(id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, author TEXT, Quantity INTEGER)
        ''')
    book_db.commit()


# ---Command line user interface---

def cmd_search_book():
    '''
    This function is used to run the search function and print a table based on the result of the search.
    It is only needed for the command line user interface to make it easier for the user to see what the book id numbers are.
    '''
    search_term = input("Search: ")
    matching_ids = match_title_author(search_term)
    print(f"{len(matching_ids)} matches found.")
    print(tabulate(return_books(matching_ids), headers=['ID', 'Title', 'Author', 'Quantity'], tablefmt='fancy_grid'))

print("Welcome to the bookshop database manager!")

# Main menu
while True:
    menu_choice = input('''
Please choose from the following menu:

1. Add a new book
2. Change book quantity
3. Edit book title or author name
4. Delete a book
5. Search books
6. List all
0. Exit
''')
    
    # Adding a book
    if menu_choice == '1':
        # Infomation is taken from the user and then passed to the add_book() function
        print("Adding a new book:")
        title = input("Book title: ")
        author = input("Author: ")
        while True:
            try:
                qty = int(input("Quantity: "))
                break
            except ValueError:
                print("Please enter a number!")
        add_book(title, author, qty)
        print(f"\n{title} added successfully!")
    
    # Change book quantity
    elif menu_choice == '2':
        print("Change book quantity")
        cmd_search_book()
        # Information is taken from the user and then passed to the update_book_qty()
        while True:
            try:
                book_id = int(input("\nID of book to edit: "))
                break
            except ValueError:
                print("Invalid input! Please try again.")
        while True:
            try:
                new_qty = int(input("New quantity: "))
                break
            except ValueError:
                print("\nInvalid input! Please try again.\n")
        update_book_qty(new_qty, book_id)
        print(f"\nBook {book_id} updated a quantity of {new_qty}")

    # Edit title/author
    elif menu_choice == '3':
        print("Please search for the book you want to edit. (leave blank to show all)")
        cmd_search_book()
        while True:
            try:
                book_id = int(input("\nBook ID to edit: "))
                break
            except ValueError:
                print("Invalid input! Please try again.")

        while True:
            update_choice = input('''Please select the value you would like to update
            
1. Title
2. Author
''')
            # Title update
            if update_choice == '1':
                new_title = input("New title: ")
                edit_book(book_id, new_title, 'title')
                print("\nTitle updated sucessfully!")
                break

            
            # Author update
            elif update_choice == '2':
                new_author = input("New Author name: ")
                edit_book(book_id, new_author, 'author')
                print("\nAuthor updated sucessfully")
                break
                
            else:
                print("Invalid input! Please try again.")
        
    #Deleting a book
    elif menu_choice == '4':
        print("Please search for a book to delete. (leave blank to show all)")
        cmd_search_book()
        
        while True:
            try:
                delete_id = int(input("\nBook ID to delete: "))
                break
            except ValueError:
                print("Invalid input! Please try again.")
        if input("\nAre you sure you want to delete this book? (y/n)").lower() == 'y':
            delete_book(delete_id)
            print("Book deleted successfully.")
        else:
            print("Deletion cancelled.")
    
    #Searching books
    elif menu_choice == '5':
        cmd_search_book()
        input("Press enter to return to the main menu...")
        
    # List all
    elif menu_choice == '6':
        print(tabulate(return_books([]), headers=['ID', 'Title', 'Author', 'Quantity'], tablefmt='fancy_grid'))
        input("Press enter to return to the main menu...")
    
    # Exit
    elif menu_choice == '0':
        print("Exiting...")
        raise SystemExit
    
    # Invalid selection
    else:
        print("Invalid selection! Please try again.")
