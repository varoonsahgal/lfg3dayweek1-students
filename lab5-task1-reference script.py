from sqlalchemy.orm import Session

from app.db import engine
from app.repository import (
    create_project,
    create_task,
    get_task,
    update_task,
    delete_task,
)


def main():
    # ------------------------------------------------------------
    # CREATE
    # ------------------------------------------------------------
    with Session(engine) as session:
        project = create_project(session, "Website Redesign")

        task = create_task(
            session=session,
            title="Draft spec",
            project_id=project.id,
            priority="medium",
        )

        task_id = task.id

        print("Created:", task)

    # ------------------------------------------------------------
    # GET FROM A FRESH SESSION
    # ------------------------------------------------------------
    with Session(engine) as session:
        refetched = get_task(session, task_id)

        print("Refetched in new session:", refetched)

    # ------------------------------------------------------------
    # UPDATE
    # ------------------------------------------------------------
    with Session(engine) as session:
        updated = update_task(
            session=session,
            task_id=task_id,
            priority="high",
            done=True,
        )

        print("Updated:", updated)

    # ------------------------------------------------------------
    # CONFIRM UPDATE FROM A FRESH SESSION
    # ------------------------------------------------------------
    with Session(engine) as session:
        refetched_after_update = get_task(session, task_id)

        print("Refetched after update:", refetched_after_update)

    # ------------------------------------------------------------
    # DELETE
    # ------------------------------------------------------------
    with Session(engine) as session:
        delete_task(session, task_id)

        print("Deleted task id:", task_id)

    # ------------------------------------------------------------
    # CONFIRM DELETE FROM A FRESH SESSION
    # ------------------------------------------------------------
    with Session(engine) as session:
        missing = get_task(session, task_id)

        print("After delete:", missing)


if __name__ == "__main__":
    main()
