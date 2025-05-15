from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from models import TaskQueue, TaskStatus


# pending 작업 조회
async def load_pending_tasks(session: AsyncSession):
    result = await session.execute(
        select(TaskQueue).where(TaskQueue.status == TaskStatus.pending)
    )
    tasks = result.scalars().all()
    return [{"id": t.id, "start": t.start} for t in tasks]


# 작업 성공 처리
async def mark_task_done(session: AsyncSession, task_id: int):
    await session.execute(
        update(TaskQueue)
        .where(TaskQueue.id == task_id)
        .values(status=TaskStatus.done)
    )
    await session.commit()


# 작업 실패 처리
async def mark_task_failed(session: AsyncSession, task_id: int):
    await session.execute(
        update(TaskQueue)
        .where(TaskQueue.id == task_id)
        .values(
            status=TaskStatus.fail,
            retries=TaskQueue.retries + 1
        )
    )
    await session.commit()
