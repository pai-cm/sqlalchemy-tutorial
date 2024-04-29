"""
ORM
Users: id, name, age
Posts: id, title, auth_id (users.id)
Replys: id, reply, post_id (posts.id)

class UserEntity:
    id: int
    name: str
    age: int
    posts: list[PostEntity]

class PostEntity:
    id: int
    title: str
    auth_id: int
    user: UserEntity
    reply: List[ReplyEntity]

class ReplyEntity:
    id: int
    reply: str
    post_id: int

user = UserEntity(id=1, name='John', age=20)
user.posts (점 찍고 posts 를 했을 때, posts의 데이터를 들고온다)

post = PostEntity(id=1, title='My first post', auth_id=1, user=user)
post.user
"""
from sqlalchemy import select
from sqlalchemy.orm import selectinload, joinedload

from src.models import UserEntity, PostEntity
import logging


async def test_select_with_relationship(test_scoped_session):
    """
    """
    # given case
    async with test_scoped_session() as session:
        entity = UserEntity(id=None, name="test0")
        session.add(entity)
        await session.commit()
        await session.refresh(entity)
        user0_id = entity.id

        session.add(PostEntity(id=None, user_id=user0_id, title="title0"))
        session.add(PostEntity(id=None, user_id=user0_id, title="title1"))
        session.add(PostEntity(id=None, user_id=user0_id, title="title2"))
        await session.commit()

        entity = UserEntity(id=None, name="test1")
        session.add(entity)
        await session.commit()
        await session.refresh(entity)
        user1_id = entity.id

        session.add(PostEntity(id=None, user_id=user1_id, title="title3"))
        session.add(PostEntity(id=None, user_id=user1_id, title="title4"))
        session.add(PostEntity(id=None, user_id=user1_id, title="title5"))
        await session.commit()

    logging.info("\nwithout eager loading >>>")
    """ n + 1 문제 """
    async with test_scoped_session() as session:
        logging.info("\ncreate stmt >>>")
        stmt = select(UserEntity)
        logging.info("\nsession execute >>>")
        result = await session.execute(stmt)
        user_entities = result.scalars().all()

        logging.info("\nget post >>>")
        # 이때 하나씩 쿼리를 또 날림
        for user_entity in user_entities:
            logging.info(f"\n  -get post(user_id:{user_entity.id}) >>>")
            post_entities = await user_entity.awaitable_attrs.posts

    logging.info("\nwith eager loading >>>")
    async with test_scoped_session() as session:
        logging.info("\ncreate stmt >>>")
        # posts 를 가져왔으면 좋겠어 해서 가져오는 것.
        # selectinload 쿼리가 두번 날라가는 것 만약 사용자가 만명이라면 In query 가 엄청 길어져서 배치로 보내줘야하는 단점 있음
        # joinedload 는 쿼리가 하나 날라가지만 중복이 발생해서 유니크 처리 해줘야함 -> 1 대 1 인 조인이 편함
        stmt = select(UserEntity).options(selectinload(UserEntity.posts))
        logging.info("\nsession execute >>>")
        result = await session.execute(stmt)
        user_entities = result.scalars().all()

        logging.info("\nget posts >>>")
        for user_entity in user_entities:
            logging.info(f"\n  -get post(user_id:{user_entity.id}) >>>")
            post_entities = user_entity.posts

    logging.info("\nwith eager joinedload loading >>>")
    async with test_scoped_session() as session:
        logging.info("\ncreate stmt >>>")
        stmt = select(UserEntity).options(joinedload(UserEntity.posts))
        logging.info("\nsession execute >>>")
        result = await session.execute(stmt)
        # user_entities = result.scalars().all()  # 터짐 !!!
        user_entities = result.scalars().unique().all()

        logging.info("\nget posts >>>")
        for user_entity in user_entities:
            logging.info(f"\n  -get post(user_id:{user_entity.id}) >>>")
            post_entities = user_entity.posts
