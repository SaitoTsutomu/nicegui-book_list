"""Book List Application"""

from pathlib import Path

from nicegui import app, ui
from tortoise import Tortoise

from .ui import AuthorList, BookList


async def init_db() -> None:
    """DB初期化"""
    db_path = (Path(__file__).parent / "db").resolve()
    db_path.mkdir(exist_ok=True)
    await Tortoise.init(db_url=f"sqlite://{db_path}/db.sqlite3", modules={"models": ["nicegui_book_list.models"]})
    await Tortoise.generate_schemas()


async def close_db() -> None:
    """DB後処理"""
    await Tortoise.close_connections()


@ui.page("/")
async def index() -> None:
    """Top page"""
    book_list = BookList()
    await AuthorList(book_list).build()
    await book_list.build()


def main(*, reload: bool = False, port: int = 8106) -> None:
    """アプリケーション実行"""
    app.on_startup(init_db)
    app.on_shutdown(close_db)
    ui.run(title="Book List", reload=reload, port=port)
