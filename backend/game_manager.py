import abc
import contextlib
from typing import Generator

from fastapi import HTTPException, status
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

    def add_submission(self, username: str, submission: models.SubmissionCreate):
        with self.sql_session() as session:
            # Get current round.
            round = session.exec(
                select(models.Round).order_by(models.Round.id.desc()).limit(1)
            ).first()

            if not round:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="No rounds exist in the database.",
                )

            # Get submitting user.
            user = session.exec(
                select(models.User).where(models.User.name == username)
            ).first()

            if not user:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"User '{username}' not found.",
                )

            # Get or create movie.
            movie = session.exec(
                select(models.Movie).where(models.Movie.name == submission.name)
            ).first()

            if not movie:
                movie = models.Movie(name=submission.name)
                session.add(movie)
                session.commit()
                session.refresh(movie)

            # Create the new submission
            new_submission = models.Submission(
                round_id=round.id,
                movie_id=movie.id,
                submitting_user_id=user.id,
            )

            # Update database.
            session.add(new_submission)
            session.commit()
            session.refresh(new_submission)

            # Add comment if given.
            if submission.comment is not None:
                comment = models.Comment(
                    submission_id=new_submission.id,
                    author_id=user.id,
                    text=submission.comment,
                )
                session.add(comment)
                session.commit()

    def add_vote(self, username: str, vote: models.VoteCreate):
        with self.sql_session() as session:
            # Get voting user.
            user = session.exec(
                select(models.User).where(models.User.name == username)
            ).first()

            if not user:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"User '{username}' not found.",
                )

            # Assign vote.
            user.voted_submission_id = vote.submission_id

            # Update database.
            session.add(user)
            session.commit()
            session.refresh(user)

    def add_comment(self, username: str, comment: models.CommentCreate):
        with self.sql_session() as session:
            # Get commenting user.
            user = session.exec(
                select(models.User).where(models.User.name == username)
            ).first()

            if not user:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"User '{username}' not found.",
                )

            comment.author_id = user.id

            db_comment = models.Comment.model_validate(comment)
            session.add(db_comment)
            session.commit()
            session.refresh(db_comment)

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
