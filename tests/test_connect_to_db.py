"""
커넥션을 맺는 전 과정을 한번 테스트하며, 각 단계에서 시간이 얼마 걸리는지를 확인해보자
"""
import logging
import time


async def test_measure_elapsed_time_per_step(test_engine):
    start_time = time.perf_counter()
    logging.info("쿼리 시작하기 >>>")
    async with test_engine.connect() as conn:
        """이게 커넥션 맺은 것음"""
        elapsed_time = time.perf_counter() - start_time
        logging.info(f"f(1) 데이터베이스 연결에 걸린 시간: {elapsed_time:.4f}s")
