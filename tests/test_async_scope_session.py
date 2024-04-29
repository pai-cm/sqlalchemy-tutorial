import asyncio
import logging

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker, scoped_session


async def test_show_same_pid(test_engine):
    """세션을 만들어주는 것이다"""
    session_factory = sessionmaker(
        test_engine, class_=AsyncSession
    )
    ScopedSession = scoped_session(session_factory)

    """async 가 나왔다가 await 를 만나면 다음으로 넘겼다가"""
    async def call0_function():
        logging.info("call0_function 1 >>>")
        await asyncio.sleep(0.1)
        logging.info("call0_function 2 >>>")
        await asyncio.sleep(0.1)
        logging.info("call0_function 3 >>>")

        async with ScopedSession() as session:
            logging.info("call0_function >>>")
            result = await session.execute(text("SELECT pg_backend_pid()"))
            logging.info("call0_function end")
            return result.scalar()

    async def call1_function():
        logging.info("call1_function 1 >>>")
        await asyncio.sleep(0.1)
        logging.info("call1_function 2 >>>")
        await asyncio.sleep(0.1)
        logging.info("call1_function 3 >>>")

        await asyncio.sleep(0.2)
        async with ScopedSession() as session:
            logging.info("call1_function >>>")
            result = await session.execute(text("SELECT pg_backend_pid()"))
            logging.info("call1_function end")
            return result.scalar()

    logging.info("task0 start")
    task0 = asyncio.create_task(call0_function())
    logging.info("task1 start")
    task1 = asyncio.create_task(call1_function())

    logging.info("gather start >>>")
    output0, output1 = await asyncio.gather(task0, task1)
    assert output0 == output1
