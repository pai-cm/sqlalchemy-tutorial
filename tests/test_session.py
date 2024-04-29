"""
entity status
1. Transient: 최초 상태 (세션에 추가되지 않은 상태)
2. Pending: 세션에 추가된 상태 (ORM 에서는 상태 관리가 들어간 상태) session.add(entity)
3. Persistent: 디비에 존재한 상태 session.flush -> send query
4. 디비가 확정적으로 박히는 session.commit()
5. Expired: commit 이 끝나고 refresh 하기 전인 상태 (왜냐면 DB와의 상태 같은지 보장을 못해서)
6. Detached: 세션 아웃되면 entity를 아예 사용 못함
"""
import asyncio

from sqlalchemy.ext.asyncio import async_sessionmaker, async_scoped_session
from sqlalchemy import inspect

from src.models import UserEntity
import logging


async def test_add_journey(test_engine, with_tables):
    """ add -> flush -> commit -> refresh 순으로 호출

    실제로 entity의 상태가 어떻게 변하는지 확인
    :param test_engine:
    :return:
    """
    async_session_factory = async_sessionmaker(test_engine)
    session_factory = async_scoped_session(async_session_factory, scopefunc=asyncio.current_task)

    logging.info("\ninitialize >>>")
    given_user0 = UserEntity(id=None, name="test0")
    show_entity_status(given_user0)

    async with session_factory() as session:
        logging.info("\nadd >>>")
        session.add(given_user0)
        show_entity_status(given_user0)

        logging.info("\nflush >>>")
        """flush 하면 auto increment id 값을 발번 받을 수 있다"""
        await session.flush([given_user0])
        show_entity_status(given_user0)

        logging.info("\ncommit >>>")
        await session.commit()
        show_entity_status(given_user0)
        # given_user0.name expired 된 entity 를 조회 하려고 하니, 에러가 난다.

        logging.info("\nrefresh >>>")
        await session.refresh(given_user0)
        show_entity_status(given_user0)

        logging.info("\nout >>>")
    logging.info("\nclosed >>>")
    show_entity_status(given_user0)


def show_entity_status(entity):
    inspector = inspect(entity)
    logging.info(f"- Transient:{inspector.transient}")
    logging.info(f"- Pending:{inspector.pending}")
    logging.info(f"- Persistent:{inspector.persistent}")
    logging.info(f"- Expired:{inspector.expired}")
    logging.info(f"- Detached:{inspector.detached}")
