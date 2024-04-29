"""
커넥션을 맺는 전 과정을 한번 테스트하며, 각 단계에서 시간이 얼마 걸리는지를 확인해보자
"""
import logging
import time

import sqlalchemy
from sqlalchemy.ext.asyncio import create_async_engine


async def test_measure_elapsed_time_per_step(test_engine):
    start_time = time.perf_counter()
    logging.info("쿼리 시작하기 >>>")
    async with test_engine.connect() as conn:
        """이게 커넥션 맺은 것음"""
        elapsed_time = time.perf_counter() - start_time
        logging.info(f"(1) 데이터베이스 연결에 걸린 시간: {elapsed_time:.4f}s")

    start_time = time.perf_counter()
    async with test_engine.connect() as conn:
        """
        test engine 이 커넥션 풀이다.
        두번째 커넥션에 연결하는건 엄청 빠르다
        첫번째 생성된 객체 그대로 사용 하는 것
        """
        elapsed_time = time.perf_counter() - start_time
        logging.info(f"(2) 두번째 데이터베이스 연결에 걸린 시간: {elapsed_time:.4f}s")


async def test_measure_elapsed_time_per_step2(test_engine):
    start_time = time.perf_counter()
    logging.info("쿼리 시작하기 >>>")
    async with test_engine.connect() as conn:
        """이게 커넥션 맺은 것음"""
        elapsed_time = time.perf_counter() - start_time
        logging.info(f"(1) 데이터베이스 연결에 걸린 시간: {elapsed_time:.4f}s")

        """커넥션을 맺는 것이 오래 걸린다라는 것을 보여줌"""
        start_time = time.perf_counter()
        await conn.execute(sqlalchemy.text("select 1;"))
        elapsed_time = time.perf_counter() - start_time
        logging.info(f"(2) select query 날리는데 걸린 시간: {elapsed_time:.4f}s")


async def test_pool_recycle(test_engine):
    test_engine = create_async_engine(
        'postgresql+asyncpg://user:password@localhost:5434/testdb',
        echo=True,
        pool_recycle=1,  # 오래된 거 안 먹어, 안써, 풀의 오래된 커넥션은 안쓸거야 라고 설정하는 것 (안쓴지 한시간 이라는 개념)
        pool_pre_ping=True,  # 매번 커넥션을 쓸 때마다 select 1 을 쓰기 때문에 헤비 트래픽일 때는 이것도 성능에 문제가 된다
    )

    start_time = time.perf_counter()
    async with test_engine.connect() as conn:
        """이게 커넥션 맺은 것음"""
        elapsed_time = time.perf_counter() - start_time
        logging.info(f"(1) 데이터베이스 연결에 걸린 시간: {elapsed_time:.4f}s")

        """커넥션을 맺는 것이 오래 걸린다라는 것을 보여줌"""
        start_time = time.perf_counter()
        await conn.execute(sqlalchemy.text("select 1;"))
        elapsed_time = time.perf_counter() - start_time
        logging.info(f"(2) select query 날리는데 걸린 시간: {elapsed_time:.4f}s")

    time.sleep(2)
    """
    being returned to pool
    reset, transaction already reset
    exceeded timeout; recycling
    Hard-closing connection
    """
    """새로운 커넥션을 맺을거니까, 아마 시간이 오래 걸려서 다른"""

    start_time = time.perf_counter()
    async with test_engine.connect() as conn:
        """이게 커넥션 맺은 것음"""
        elapsed_time = time.perf_counter() - start_time
        logging.info(f"(1) 데이터베이스 연결에 걸린 시간: {elapsed_time:.4f}s")

        """커넥션을 맺는 것이 오래 걸린다라는 것을 보여줌"""
        start_time = time.perf_counter()
        await conn.execute(sqlalchemy.text("select 1;"))
        elapsed_time = time.perf_counter() - start_time
        logging.info(f"(2) select query 날리는데 걸린 시간: {elapsed_time:.4f}s")


async def test_pool_size(test_engine):
    test_engine = create_async_engine(
        'postgresql+asyncpg://user:password@localhost:5434/testdb',
        echo=True,
        pool_size=10,
        max_overflow=0,
        pool_timeout=1,
    )

    conns = []
    for i in range(10):
        logging.info(f"{i}th connection 생성하기 >> \n")
        conns.append(await test_engine.connect())
    logging.info(conns)

    """반환을 안했기 때문에 터져야한다"""
    logging.info(f"11th connection 생성하기 >> \n")
    await test_engine.connect()


async def test_set_statement_timeout(test_engine):
    test_engine = create_async_engine(
        'postgresql+asyncpg://user:password@localhost:5434/testdb',
        echo=True,
        connect_args={'server_settings': {'statement_timeout': '1000'}}  # 밀리세컨즈라 1000은 1초
    )

    async with test_engine.connect() as conn:
        await conn.execute(sqlalchemy.text("SELECT pg_sleep(0.9)"))

    async with test_engine.connect() as conn:
        await conn.execute(sqlalchemy.text("SELECT pg_sleep(1.1)"))  # canceling statement due to statement
