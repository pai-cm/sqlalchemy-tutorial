import asyncio
import logging

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_scoped_session, async_sessionmaker, create_async_engine
from sqlalchemy.orm import sessionmaker, scoped_session


async def test_show_same_pid(test_engine):
    """세션을 만들어주는 것이다"""
    session_factory = sessionmaker(
        test_engine, class_=AsyncSession
    )
    ScopedSession = scoped_session(session_factory)
    """
    scoped session 은 세션을 딕셔너리로 관리해주는데,
    key 가 thread 이고 value 가 session
    
    세션 잡아줬을 때 세션을 하나 만들면
    쓰레드 별로 동일한 세션을 보장 해준다
    """

    async def call0_function():
        async with ScopedSession() as session:
            logging.info(f"call0_function session: {session}")
            result = await session.execute(text("SELECT pg_backend_pid()"))
            return result.scalar()

    async def call1_function():
        async with ScopedSession() as session:
            await asyncio.sleep(1)
            logging.info(f"call1_function session: {session}")
            result = await session.execute(text("SELECT pg_backend_pid()"))
            return result.scalar()

    task0 = asyncio.create_task(call0_function())
    task1 = asyncio.create_task(call1_function())

    output0, output1 = await asyncio.gather(task0, task1)
    assert output0 == output1


async def test_show_async_scoped_session(test_engine):
    """세션을 만들어주는 것이다"""
    session_factory = async_sessionmaker(test_engine)
    ScopedSession = async_scoped_session(session_factory, scopefunc=asyncio.current_task)
    # scopefunc 는 key 이다. current_task 로 key 를 설정 하겠다는 뜻. 기본값은 쓰레드

    async def call0_function():
        logging.info(f"call0_function task id: {asyncio.current_task()}")
        async with ScopedSession() as session:
            logging.info(f"call0_function session: {session}")
            result = await session.execute(text("SELECT pg_backend_pid()"))
            return result.scalar()

    async def call1_function():
        logging.info(f"call1_function task id: {asyncio.current_task()}")
        async with ScopedSession() as session:
            logging.info(f"call1_function session: {session}")
            result = await session.execute(text("SELECT pg_backend_pid()"))
            return result.scalar()

    """커넥션을 들고와서 사용 했는데, 돌려주지 않았기 때문에 call1 은 커넥션을 새로운 것을 만든 것"""

    task0 = asyncio.create_task(call0_function())
    task1 = asyncio.create_task(call1_function())

    output0, output1 = await asyncio.gather(task0, task1)
    assert output0 != output1


async def test_show_async_scoped_session2(test_engine):
    test_engine = create_async_engine(
        'postgresql+asyncpg://user:password@localhost:5434/testdb',
        echo=True,
        pool_size=1,
        max_overflow=0,
    )
    session_factory = async_sessionmaker(test_engine)
    ScopedSession = async_scoped_session(session_factory, scopefunc=asyncio.current_task)

    async def call0_function():
        logging.info(f"call0_function task id: {asyncio.current_task()}")
        async with ScopedSession() as session:
            logging.info(f"call0_function session: {session}")
            result = await session.execute(text("SELECT pg_backend_pid()"))
            logging.info(f"call0_function end")
            return result.scalar()

    async def call1_function():
        logging.info(f"call1_function task id: {asyncio.current_task()}")
        async with ScopedSession() as session:
            logging.info(f"call1_function session: {session}")
            result = await session.execute(text("SELECT pg_backend_pid()"))
            logging.info(f"call1_function end")
            return result.scalar()

    """pool_size=1, max_overflow=0 로 설정 해줬기 때문에 task1 이 끝날 때 까지 기다려줌"""

    task0 = asyncio.create_task(call0_function())
    task1 = asyncio.create_task(call1_function())

    output0, output1 = await asyncio.gather(task0, task1)
    assert output0 == output1


async def test_show_async_scoped_session3(test_engine):
    test_engine = create_async_engine(
        'postgresql+asyncpg://user:password@localhost:5434/testdb',
        echo=True,
        pool_size=2,
        max_overflow=0,
    )
    session_factory = async_sessionmaker(test_engine)
    ScopedSession = async_scoped_session(session_factory, scopefunc=asyncio.current_task)

    async def call0_function():
        logging.info(f"call0_function task id: {asyncio.current_task()}")
        async with ScopedSession() as session:
            logging.info(f"call0_function session: {session}")
            result = await session.execute(text("SELECT pg_backend_pid()"))
            logging.info(f"call0_function end")
            return result.scalar()

    async def call1_function():
        logging.info(f"call1_function task id: {asyncio.current_task()}")
        async with ScopedSession() as session:
            logging.info(f"call1_function session: {session}")
            result = await session.execute(text("SELECT pg_backend_pid()"))
            logging.info(f"call1_function end")
            return result.scalar()

    task0 = asyncio.create_task(call0_function())
    task1 = asyncio.create_task(call1_function())

    output0, output1 = await asyncio.gather(task0, task1)
    assert output0 != output1
