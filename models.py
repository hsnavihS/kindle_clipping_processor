from typing import List
from dataclasses import dataclass, field

@dataclass
class Word:
    word: str
    definition: str

@dataclass
class Book:
    title: str
    words: List[Word] = field(default_factory=list)
    sentences: List[str] = field(default_factory=list)

    def add_word(self, word: str, meaning: str) -> None:
        self.words.append(Word(word, meaning))

    def remove_word(self, word: Word) -> None:
        self.words.remove(item)

    def __eq__(self, other) -> bool:
        return self.title == other.title
