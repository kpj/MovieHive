import abc
import contextlib
from typing import Generator

from fastapi import HTTPException
from sqlmodel import Session, SQLModel, create_engine, select

from backend import models


class GameState(abc.ABC):
    def __init__(self, manager: "GameManager"):
        self.manager = manager

    @abc.abstractmethod
    def enter(self):
        pass

    @abc.abstractmethod
    def exit(self):
        pass

    @abc.abstractmethod
    def update(self):
        pass


class ResultState(GameState):
    def enter(self):
        pass

    def exit(self):
        pass

    def update(self):
        pass


class VotingState(GameState):
    def enter(self):
        pass

    def exit(self):
        pass

    def update(self):
        if self.manager.all_players_voted():
            self.manager.transition_to_state(ResultState)


class SubmissionState(GameState):
    def enter(self):
        pass

    def exit(self):
        pass

    def update(self):
        if self.manager.all_players_submitted():
            self.manager.transition_to_state(VotingState)


class GameManager:
    def __init__(self, initial_state: GameState | None = None):
        self._state = (initial_state or SubmissionState)(self)

        self.engine = None

    def update(self):
        self._state.update()

    def is_in_state(self, state: GameState) -> bool:
        return isinstance(self._state, state)

    def add_player(self, user: models.UserCreate):
        if user.name not in self._players:
            with self.sql_session() as session:
                db_user = models.User.model_validate(user)
                session.add(db_user)
                session.commit()
                session.refresh(db_user)

    @property
    def _players(self):
        with self.sql_session() as session:
            return [user.name for user in session.exec(select(models.User))]

    def get_current_round(self) -> models.Round:
        with self.sql_session() as session:
            return session.exec(select(models.Round)).first()

    def add_submission(self, submission: models.Submission):
        with self.sql_session() as session:
            db_submission = models.Submission(
                round=session.exec(select(models.Round)).first(),
                submitting_user=models.User(name=submission.user),
                movie=models.Movie(name=submission.name),
            )
            session.add(db_submission)
            session.commit()
            session.refresh(db_submission)

    def add_vote(self, vote: models.VoteCreate):
        with self.sql_session() as session:
            user = session.exec(
                select(models.User).where(models.User.name == vote.voting_user_name)
            ).first()
            if not user:
                raise HTTPException(status_code=404, detail="User not found")

            user.voted_submission_id = vote.submission_id

            session.add(user)
            session.commit()
            session.refresh(user)

    def all_players_submitted(self) -> bool:
        with self.sql_session() as session:
            users = set(
                sub.submitting_user.name
                for sub in session.exec(select(models.Submission))
            )

        return set(self._players) <= users

    def all_players_voted(self) -> bool:
        with self.sql_session() as session:
            voted_submission_ids = [
                user.voted_submission_id for user in session.exec(select(models.User))
            ]

        return None not in voted_submission_ids

    def transition_to_state(self, new_state: GameState):
        print(f"Transitioning to {new_state}")

        if self._state is not None:
            self._state.exit()

        self._state = new_state(self)
        self._state.enter()

    def setup_database(self):
        sqlite_file_name = "database.db"
        sqlite_url = f"sqlite:///{sqlite_file_name}"

        connect_args = {"check_same_thread": False}
        self.engine = create_engine(sqlite_url, connect_args=connect_args)

        SQLModel.metadata.create_all(self.engine)

        with self.sql_session() as session:
            round = models.Round(
                prompt="Movies that had a big impact on you while growing up."
            )

            session.add(round)
            session.commit()

    @contextlib.contextmanager
    def sql_session(self) -> Generator[Session, None, None]:
        yield Session(self.engine)
