import json

from typing import List
from LocalFilePicker import LocalFilePicker
from models import Book

def fetch_or_create_book(book_name: str, books: List[Book]) -> Book:
    for book in books:
        if book.title == book_name:
            return book
    book = Book(book_name)
    books.append(book)
    return book

def process_words(books: List[Book], output_dir: str) -> None:
    with open(f"{output_dir}/words.json", "r") as file:
        content = json.load(file)
        for book_name in content:
            book = fetch_or_create_book(book_name, books)
            for word in content[book_name]:
                meaning = content[book_name][word]
                book.add_word(word, meaning)

def process_sentences(books: List[Book], output_dir: str) -> None:
    with open(f"{output_dir}/sentences.json", "r") as file:
        content = json.load(file)
        for book_name in content:
            book = fetch_or_create_book(book_name, books)
            for sentence in content[book_name]:
                book.sentences.append(sentence)
