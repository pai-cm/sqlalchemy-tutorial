"""
커넥션을 맺는 전 과정을 한번 테스트하며, 각 단계에서 시간이 얼마 걸리는지를 확인해보자
"""
import logging
import time

import sqlalchemy


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
