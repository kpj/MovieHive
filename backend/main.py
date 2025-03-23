import abc
from typing import Annotated
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Field, Session, SQLModel, create_engine, select, Relationship


class RoundBase(SQLModel):
    prompt: str


class Round(RoundBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    movies: list["Movie"] = Relationship(back_populates="round")


class RoundPublic(RoundBase):
    id: int


class RoundPublicWithMovies(RoundPublic):
    movies: list["MoviePublic"] = []


class MovieBase(SQLModel):
    round_id: int | None = Field(default=None, foreign_key="round.id")
    name: str


class Movie(MovieBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    round: Round = Relationship(back_populates="movies")
    submitting_user: "User" = Relationship(
        back_populates="submitted_movie",
        sa_relationship_kwargs={"foreign_keys": "User.submitted_movie_id"},
    )
    voting_users: list["User"] = Relationship(
        back_populates="voted_movie",
        sa_relationship_kwargs={"foreign_keys": "User.voted_movie_id"},
    )


class MoviePublic(MovieBase):
    id: int
    submitting_user: "UserPublic"
    voting_users: list["UserPublic"]


class MovieCreate(MovieBase):
    name: str
    user: str


class UserBase(SQLModel):
    name: str

    submitted_movie_id: int | None = Field(default=None, foreign_key="movie.id")
    voted_movie_id: int | None = Field(default=None, foreign_key="movie.id")


class User(UserBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    submitted_movie: Movie | None = Relationship(
        back_populates="submitting_user",
        sa_relationship_kwargs={"foreign_keys": "User.submitted_movie_id"},
    )
    voted_movie: Movie | None = Relationship(
        back_populates="voting_users",
        sa_relationship_kwargs={"foreign_keys": "User.voted_movie_id"},
    )


class UserPublic(UserBase):
    id: int


class UserCreate(UserBase):
    pass


class VoteCreate(SQLModel):
    movie_id: int
    voting_user_id: str  # TODO: make int


class GameState(abc.ABC):
    @abc.abstractmethod
    def enter(self):
        pass

    @abc.abstractmethod
    def exit(self):
        pass

    @abc.abstractmethod
    def update(self):
        pass


class ResultState(abc.ABC):
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
        with Session(engine) as session:
            voted_movie_ids = [
                user.voted_movie_id for user in session.exec(select(User))
            ]

            # CHeck if everyone has voted
            if None not in voted_movie_ids:
                transition_to_state(ResultState)


class SubmissionState(GameState):
    def enter(self):
        pass

    def exit(self):
        pass

    def update(self):
        print("Checking if we are done with submission state")

        with Session(engine) as session:
            users = set(sub.submitting_user.name for sub in session.exec(select(Movie)))

        if set(PLAYER_LIST) <= users:
            print("Advance to next stage!")
            transition_to_state(VotingState)
        else:
            print("some players are still missing")


CURRENT_STATE = SubmissionState()
# CURRENT_STATE = ResultState()
PLAYER_LIST = []
PROMPT = "Movies that had a big impact on you while growing up."


class CurrentState(SQLModel):
    state: str


def transition_to_state(new_state):
    global CURRENT_STATE
    print(f"Transitioning to {new_state}")

    if CURRENT_STATE is not None:
        CURRENT_STATE.exit()

    CURRENT_STATE = new_state()
    CURRENT_STATE.enter()


sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, connect_args=connect_args)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        round = Round(prompt="Movies that had a big impact on you while growing up.")

        session.add(round)
        session.commit()


def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield


app = FastAPI(lifespan=lifespan)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/state")
def get_state() -> CurrentState:
    return CurrentState(state=CURRENT_STATE.__class__.__name__)


@app.get("/round")
def get_round(session: Session = Depends(get_session)) -> RoundPublicWithMovies:
    return session.exec(select(Round)).first()


@app.post("/movies/")
def add_movie(
    *, session: Session = Depends(get_session), movie: MovieCreate
) -> CurrentState:
    if not isinstance(CURRENT_STATE, SubmissionState):
        raise HTTPException(status_code=500, detail="Not in submission state")

    db_movie = Movie(
        round=session.exec(select(Round)).first(),
        name=movie.name,
        submitting_user=User(name=movie.user),
    )
    session.add(db_movie)
    session.commit()

    CURRENT_STATE.update()
    return CurrentState(state=CURRENT_STATE.__class__.__name__)


@app.post("/vote/")
def add_vote(
    *, session: Session = Depends(get_session), vote: VoteCreate
) -> CurrentState:
    if not isinstance(CURRENT_STATE, VotingState):
        raise HTTPException(status_code=500, detail="Not in voting state")

    # user = session.get(User, vote.voting_user_id)
    user = session.exec(
        select(User).where(User.name == vote.voting_user_id)
    ).first()  # TODO: actually use user id instead of name
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    print(vote)
    print(f"Voting user: {user}")

    user.voted_movie_id = vote.movie_id

    session.add(user)
    session.commit()
    session.refresh(user)

    CURRENT_STATE.update()
    return CurrentState(state=CURRENT_STATE.__class__.__name__)


@app.post("/users/")
def add_user(*, session: Session = Depends(get_session), user: UserCreate):
    print(user)
    if user.name not in PLAYER_LIST:
        PLAYER_LIST.append(user.name)
