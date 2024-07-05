import os
import json

import utils
from time import sleep
from models import Word, Book
from typing import Callable, List
from dataclasses import dataclass, field
from LocalFilePicker import LocalFilePicker
from HighlightProcessor import HighlightProcessor

from nicegui import run, ui

async def upload_clippings() -> None:
    result = await LocalFilePicker('/home/shivansh/fun/kindle_clippings_processor/clippings', multiple=False)
    file_name = result[0] if result else None

    if file_name is None:
        ui.notify("No file selected")
    else:
        highlight_processor = HighlightProcessor(file_name, "test")
        ui.notify("Processing clippings")
        await run.cpu_bound(highlight_processor.process_file)
        ui.navigate.to('/home')

@ui.page('/home')
def home():
    output_dir = HighlightProcessor.get_or_create_output_dir()
    books: List[Book] = []
    utils.process_words(books, output_dir)
    utils.process_sentences(books, output_dir)

    ui.dark_mode().enable()

    if not books:
        ui.label('No books to display').classes('mx-auto')

    for book in books:
        ui.label(book.title).classes('text-bold text-2xl text-white')
        ui.separator()

        with ui.expansion('Words').classes('w-full'):
            ui.separator()
            with ui.grid(columns=2):
                for word in book.words:
                    ui.label(f"{word.word}")
                    ui.label(f"{word.definition}")

        if len(book.sentences) != 0:
            with ui.expansion('Quotes').classes('w-full'):
                ui.separator()
                for sentence in book.sentences:
                    ui.label(sentence)

        ui.separator()
        ui.separator()

ui.dark_mode().enable()

output_dir = HighlightProcessor.get_or_create_output_dir()
if os.path.exists(f"{output_dir}/words.json"):
    ui.label("Some clippings already exist, to view those, click the button below").classes('text-bold text-2xl text-white')
    ui.link("View existing", home)

ui.label("To upload a clippings file, click the button below").classes('text-bold text-2xl text-white')
ui.button('Upload clippings file', on_click=upload_clippings, icon='folder')

ui.run()
