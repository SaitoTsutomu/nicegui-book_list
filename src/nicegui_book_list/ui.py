"""GUI部品"""

from abc import ABC, abstractmethod
from typing import ClassVar

from nicegui import events, ui
from tortoise.models import Model

from . import models


class ListBase(ABC, ui.element):
    """著者リストと書籍リストのGUIの基底クラス

    :ivar label: uiの見出し
    :ivar refs: 一緒にrefreshするもの
    :ivar fields: フィールドの集合
    :ivar list_ui: build時の一覧用のコンテナ
    :ivar add_ui: build時の追加入力用のコンテナ
    :cvar model: 対象モデル
    """

    label: str
    refs: set["ListBase"]
    fields: set[str]
    list_ui: ui.column
    add_ui: ui.row
    model: ClassVar[Model]

    def __init__(self, *, label: str, refs: set["ListBase"] | None = None) -> None:
        """初期化"""
        self.label = label
        self.refs = refs or set()
        self.fields: set[str] = self.model.all().fields - {"id"}

    @ui.refreshable
    def build(self) -> None:
        """GUI作成"""
        self.list_ui = ui.column().classes("mx-auto")
        with self.list_ui:
            ui.label(self.label).classes("text-2xl")
            with ui.row().classes("w-full items-center px-4"):
                self.add_ui = ui.row()
                ui.button(on_click=self.create, icon="add").props("flat").classes("ml-auto")

    def refresh(self) -> None:
        """最新化"""
        self.build.refresh()
        for ref in self.refs:
            ref.build.refresh()

    @abstractmethod
    async def check(self) -> bool:
        """入力チェック"""

    async def create(self) -> None:
        """追加"""
        if await self.check():
            await self.model.create(**{field: getattr(self, field).value for field in self.fields})
            self.refresh()

    async def keydown_enter(self, event: events.GenericEventArguments) -> None:
        """Enterキー押下"""
        if not event.args.get("isComposing"):  # IME変換でないとき
            await self.create()

    async def delete(self, record: Model) -> None:
        """削除"""
        await record.delete()
        self.refresh()


class BookList(ListBase):
    """書籍リストのGUI

    :ivar author_id: モデルのフィールド用
    :ivar title: モデルのフィールド用
    :cvar model: 対象モデル
    """

    author_id: ui.select
    title: ui.input
    model: ClassVar[Model] = models.Book

    @ui.refreshable
    async def build(self) -> None:
        """GUI作成"""
        super().build()
        authors: list[models.Author] = await models.Author.all()
        books: list[models.Book] = await models.Book.all()
        with self.list_ui:
            with self.add_ui:
                self.author_id = ui.select({author.id: author.name for author in authors}, label="Author")
                self.title = ui.input(label="Title").on("keydown.enter", self.keydown_enter)
            for book in reversed(books):
                author = await book.author
                with ui.card(), ui.row().classes("items-center"):
                    ui.label(author.name)
                    ui.input("Title", on_change=book.save).bind_value(book, "title").on("blur", self.build.refresh)
                    ui.button(icon="delete", on_click=lambda a=book: self.delete(a)).props("flat")

    async def check(self) -> bool:
        """入力チェック"""
        if not self.title.value:
            ui.notify("Specify title")
            return False
        if not await models.Author.exists(id=self.author_id.value):
            ui.notify("Select author")
            return False
        return True


class AuthorList(ListBase):
    """著者リストのGUI

    :ivar name: モデルのフィールド用
    :cvar model: 対象モデル
    """

    name: ui.input
    model: ClassVar[Model] = models.Author

    @ui.refreshable
    async def build(self) -> None:
        """GUI作成"""
        super().build()
        authors: list[models.Author] = await models.Author.all()
        with self.list_ui:
            with self.add_ui:
                self.name = ui.input(label="Name").on("keydown.enter", self.keydown_enter)
            for author in reversed(authors):
                with ui.card(), ui.row().classes("items-center"):
                    ui.input("Name", on_change=author.save).bind_value(author, "name").on("blur", self.build.refresh)
                    ui.button(icon="delete", on_click=lambda a=author: self.delete(a)).props("flat")

    async def check(self) -> bool:
        """入力チェック"""
        if not self.name.value:
            ui.notify("Specify name")
            return False
        return True
