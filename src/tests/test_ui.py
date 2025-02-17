# flake8: noqa: S101
"""テスト"""

import asyncio
from collections.abc import Iterable

import pytest
from tortoise import Tortoise

from nicegui_book_list import Author, AuthorList, Book, BookList


@pytest.fixture(autouse=True)
def db() -> Iterable[None]:
    """DBの開始と終了"""
    asyncio.run(Tortoise.init(db_url="sqlite://:memory:", modules={"models": ["nicegui_book_list.models"]}))
    asyncio.run(Tortoise.generate_schemas())
    yield
    asyncio.run(Tortoise.close_connections())


def authors() -> list[dict]:
    """全Author"""

    async def _values():  # noqa: ANN202
        return await Author.all().values("name")

    return asyncio.run(_values())


def books() -> list[dict]:
    """全Book"""

    async def _values():  # noqa: ANN202
        return await Book.all().values("author_id", "title")

    return asyncio.run(_values())


def test_author_list_create() -> None:
    """AuthorListのcreateのテスト"""
    author_list = AuthorList(label="著者リスト")
    asyncio.run(author_list.build())
    author_list.name.value = "author1"
    asyncio.run(author_list.create())
    assert authors() == [{"name": "author1"}]


def test_book_list_create() -> None:
    """BookListのcreateのテスト"""
    author = asyncio.run(Author.create(name="author1"))
    book_list = BookList(label="書籍リスト")
    asyncio.run(book_list.build())
    book_list.author_id.value = author.id
    book_list.title.value = "title1"
    asyncio.run(book_list.create())
    assert books() == [{"author_id": author.id, "title": "title1"}]
