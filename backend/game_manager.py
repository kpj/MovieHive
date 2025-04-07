import abc
import contextlib
from typing import Generator

from fastapi import HTTPException, status
from sqlmodel import Session, SQLModel, create_engine, select

from imdbmovies import IMDB

from . import models


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


class OverviewState(GameState):
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
            self.manager.transition_to_state(OverviewState)


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
        self._state = (initial_state or OverviewState)(self)

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

    def create_new_round(self, round: models.RoundCreate):
        with self.sql_session() as session:
            db_round = models.Round.model_validate(round)
            session.add(db_round)
            session.commit()
            session.refresh(db_round)

        self.transition_to_state(SubmissionState)

    def get_all_rounds(self) -> list[models.Round]:
        with self.sql_session() as session:
            return session.exec(
                select(models.Round).order_by(models.Round.id.desc())
            ).all()

    def get_current_round(self) -> models.Round:
        with self.sql_session() as session:
            return session.exec(
                select(models.Round).order_by(models.Round.id.desc()).limit(1)
            ).first()

    def add_submission(self, username: str, submission: models.SubmissionCreate):
        with self.sql_session() as session:
            # Get current round.
            round = self.get_current_round()

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
                movie = self.load_movie_object(submission.name)
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

            # Assign comments.
            for submission_id, comment_text in vote.all_comments.items():
                comment = models.Comment(
                    submission_id=submission_id,
                    author_id=user.id,
                    text=comment_text,
                )
                session.add(comment)
                session.commit()
                session.refresh(comment)

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

    def user_has_submitted(self, username: str) -> bool:
        with self.sql_session() as session:
            return username in set(
                sub.submitting_user.name
                for sub in session.exec(select(models.Submission))
            )

    def all_players_voted(self) -> bool:
        with self.sql_session() as session:
            voted_submission_ids = [
                user.voted_submission_id for user in session.exec(select(models.User))
            ]

        return None not in voted_submission_ids

    def user_has_voted(self, username: str) -> bool:
        with self.sql_session() as session:
            return username in [
                user.name
                for user in session.exec(
                    select(models.User).where(
                        models.User.voted_submission_id.is_not(None)
                    )
                )
            ]

    def get_current_state_message(self, username) -> models.CurrentState:
        state_message = models.CurrentState(state=self._state.__class__.__name__)

        if self.is_in_state(SubmissionState):
            state_message.player_state = (
                "closed" if self.user_has_submitted(username) else "open"
            )
        elif self.is_in_state(VotingState):
            state_message.player_state = (
                "closed" if self.user_has_voted(username) else "open"
            )

        return state_message

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

    @contextlib.contextmanager
    def sql_session(self) -> Generator[Session, None, None]:
        yield Session(self.engine)

    def load_movie_object(self, name: str) -> models.Movie:
        imdb = IMDB()

        movie_data = imdb.get_by_name(name)

        actor_data_subset = []
        for actor in movie_data["actor"]:
            _, actor_id, _ = actor["url"].rsplit("/", 2)
            actor_data = imdb.person_by_id(actor_id)
            actor_data_subset.append(f"{actor_data['name']},{actor_data.get('image')}")

        used_directors = []  # Directors and creators can be redundant.
        director_data_subset = []
        for director in movie_data["director"] + movie_data["creator"]:
            _, director_id, _ = director["url"].rsplit("/", 2)
            if director_id in used_directors:
                continue
            director_data = imdb.person_by_id(director_id)
            director_data_subset.append(
                f"{director_data['name']},{director_data.get('image')}"
            )
            used_directors.append(director_id)

        return models.Movie(
            name=movie_data["name"],
            requested_name=name,
            poster_url=movie_data["poster"],
            description=movie_data["description"],
            genre=";".join(movie_data["genre"]),
            release_date=movie_data["datePublished"],
            actors=";".join(actor_data_subset),
            directors=";".join(director_data_subset),
        )
