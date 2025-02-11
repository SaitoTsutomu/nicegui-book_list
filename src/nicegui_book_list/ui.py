"""GUI部品"""

from nicegui import ui
from tortoise.exceptions import DoesNotExist

from . import models


class BookList(ui.element):
    """書籍リストのGUI"""

    @ui.refreshable
    async def build(self) -> None:
        """GUI作成"""
        self.authors: list[models.Author] = await models.Author.all()
        self.books: list[models.Book] = await models.Book.all()
        with ui.column().classes("mx-auto"):
            ui.label("書籍リスト").classes("text-2xl")
            with ui.row().classes("w-full items-center px-4"):
                self.author = ui.select({author.id: author.name for author in self.authors}, label="Author")
                self.title = ui.input(label="Title")
                ui.button(on_click=self.create, icon="add").props("flat").classes("ml-auto")
            for book in reversed(self.books):
                author = await book.author
                with ui.card(), ui.row().classes("items-center"):
                    ui.label(author.name)
                    ui.input("Title", on_change=book.save).bind_value(book, "title").on("blur", self.build.refresh)
                    ui.button(icon="delete", on_click=lambda a=book: self.delete(a)).props("flat")

    def refresh(self) -> None:
        """最新化"""
        self.build.refresh()

    async def create(self) -> None:
        """追加"""
        if not self.title.value:
            ui.notify("Specify title")
            return
        try:
            author = await models.Author.get(id=self.author.value)
        except DoesNotExist:
            ui.notify("Select author")
            return
        await models.Book.create(author=author, title=self.title.value)
        self.refresh()

    async def delete(self, book: models.Book) -> None:
        """削除"""
        await book.delete()
        self.refresh()


class AuthorList(ui.element):
    """著者リストのGUI"""

    def __init__(self, book_list: BookList) -> None:
        """初期化"""
        super().__init__()
        self.book_list = book_list

    @ui.refreshable
    async def build(self) -> None:
        """GUI作成"""
        self.authors: list[models.Author] = await models.Author.all()
        with ui.column().classes("mx-auto"):
            ui.label("著者リスト").classes("text-2xl")
            with ui.row().classes("w-full items-center px-4"):
                self.name = ui.input(label="Name")
                ui.button(on_click=self.create, icon="add").props("flat").classes("ml-auto")
            for author in reversed(self.authors):
                with ui.card(), ui.row().classes("items-center"):
                    ui.input("Name", on_change=author.save).bind_value(author, "name").on("blur", self.build.refresh)
                    ui.button(icon="delete", on_click=lambda a=author: self.delete(a)).props("flat")

    def refresh(self) -> None:
        """最新化"""
        self.build.refresh()
        self.book_list.build.refresh()

    async def create(self) -> None:
        """追加"""
        if not self.name.value:
            ui.notify("Specify name")
            return
        await models.Author.create(name=self.name.value)
        self.refresh()

    async def delete(self, author: models.Author) -> None:
        """削除"""
        await author.delete()
        self.refresh()
