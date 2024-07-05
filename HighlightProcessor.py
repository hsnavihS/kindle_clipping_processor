import os
import json
import time
import math
import random
import requests
import threading

class HighlightProcessor:

    def __init__(self, filename: str, mode: str):
        self.filename = filename
        self.mode = mode
        self.lines = []
        self.linecount = 0
        self.words = {}
        self.total_words = 0
        self.sentences = {}
        self.dictionary_api_url = "https://api.dictionaryapi.dev/api/v2/entries/en/"
        self.kindle_word_separator = "=========="
        self.total_threads = 1

    def get_or_create_output_dir() -> str:
        base_dir = os.getcwd()
        output_dir = f"{base_dir}/output"
        if not os.path.exists(output_dir):
            os.mkdir(output_dir)
        return output_dir

    def write_to_files(self) -> None:
        output_dir = HighlightProcessor.get_or_create_output_dir()

        with open(f"{output_dir}/words.json", "w") as file:
            json.dump(self.words, file, indent=2)
            file.close()

        with open(f"{output_dir}/sentences.json", "w") as file:
            json.dump(self.sentences, file, indent=2)
            file.close()

    def clean_book_name(self, book_name: str) -> str:
        """ Remove the invisible <feff> character at the beginning. """
        if book_name[0] == '\ufeff':
            book_name = book_name[1:]
        return book_name

    def process_file(self) -> None:
        try:
            with open(self.filename, encoding='utf-8-sig') as file:
                self.lines = file.readlines()
                self.lines = [line.strip() for line in self.lines]
                self.linecount = len(self.lines)
                file.close()
        except Exception as e:
            print("HighlightProcessor::process_file() - Error: ", e)

        book_name = self.lines[0]
        for i in range(self.linecount):
            if i + 1 < self.linecount and self.lines[i + 1] == self.kindle_word_separator:
                self.process_highlight(self.lines[i], book_name)
                book_name = self.lines[i + 2] if i + 2 < self.linecount else book_name

        self.process_word_meanings_threaded()
        self.write_to_files()

    def print_progress_bar(self, progress: int, book: str, total_words: int = -1) -> None:
        if total_words == -1:
            total_words = self.total_words
        factor = 50 / total_words
        completed = factor * progress if progress != total_words else 50
        completed = math.ceil(completed)
        remaining = 50 - completed
        print((f"[{"#" * completed + "-" * remaining}] - {progress}/{total_words}"
            f"- {book} - Thread: {threading.current_thread().name}/{self.total_threads}"))

    def get_word_meaning_delegate(self, book: str, book_words: list) -> None:
        processed_words = 0
        num_words = len(book_words)

        for word in book_words:
            if self.words[book][word] is None:
                max_retries = 3
                meaning_response = self.get_word_meaning(word, self.mode)

                # The free API doesn't support many concurrent calls
                # In case of a 429, retry for a maximum of 3 times
                while meaning_response[0] == 429 and max_retries > 0:
                    time.sleep(6)
                    meaning_response = self.get_word_meaning(word, self.mode)
                    max_retries -= 1
                    if max_retries == 0 and meaning_response[0] == 429:
                        print(("HighlightProcessor::get_word_meaning_delegate()"
                            "- FAILURE: Max retries reached for word: ", word))
                        return

                if meaning_response[0] == 404:
                    meaning_response = "Definition not found"

                self.words[book][word] = meaning_response
                processed_words += 1
                self.print_progress_bar(processed_words, book, num_words)

    def process_word_meanings_threaded(self) -> None:
        threads = []
        for book in self.words:
            temp_words = []
            for word in self.words[book]:
                temp_words.append(word)
                if len(temp_words) == 60 or word == list(self.words[book].keys())[-1]:
                    thread = threading.Thread(target=self.get_word_meaning_delegate,
                                              args=(book, temp_words),
                                              name=str(self.total_threads))
                    threads.append(thread)
                    self.total_threads += 1
                    temp_words = []

        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()

    def process_word_meanings(self) -> None:
        processed_words = 0
        for book in self.words:
            for word in self.words[book]:
                if self.words[book][word] is None:
                    self.words[book][word] = self.get_word_meaning(word)
                    processed_words += 1
                    self.print_progress_bar(processed_words, book)


    def process_highlight(self, highlight: str, book_name: str) -> None:
        book_name = self.clean_book_name(book_name)

        if highlight.find(" ") == -1:
            self.total_words += 1
            word = self.clean_word(highlight)
            if self.words.get(book_name) is None:
                self.words[book_name] = {}
            self.words[book_name][word] = None
        else:
            if self.sentences.get(book_name) is None:
                self.sentences[book_name] = []
            self.sentences[book_name].append(highlight.capitalize())

    def clean_word(self, word: str) -> str:
        """Remove any non-alphanumeric characters from the word."""

        clean_word = ""
        for letter in word:
            if letter.isalnum():
                clean_word += letter

        return clean_word.capitalize()

    def print_words(self) -> None:
        for book in self.words:
            print(book, ":")
            for word in self.words[book]:
                if self.words[book].get(word) is not None:
                    print((f"-> {word} - "
                        f"{self.words[book][word][0]["definitions"][0]["definition"]}"))
                else:
                    print(f"-> {word} - No definition found")
            print()

    def print_sentences(self) -> None:
        for book in self.sentences:
            print(book, ":")
            for sentence in self.sentences[book]:
                print(f"-> {sentence}")
            print()

    def get_word_meaning(self, word: str, mode: str = "test") -> list:
        url = self.dictionary_api_url + word

        if self.mode == "test":
            time.sleep(0.1 * random.randint(1, 3))
            return url

        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()
            return data[0]["meanings"][0]["definitions"][0]["definition"]
            # return data[0]["meanings"]
        elif response.status_code == 429:
            print(("HighlightProcessor::get_word_meaning() - "
                  "6 second sleep due to server overload"))
            return [429,]
        else:
            print("HighlightProcessor::get_word_meaning() - Error: ",
                  response.status_code, "for word: ", word)
            return [response.status_code,]
