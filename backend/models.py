from sqlmodel import Field, SQLModel, Relationship


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
    user: str | None = None


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


class CurrentState(SQLModel):
    state: str
