from sqlmodel import Field, SQLModel, Relationship


class RoundBase(SQLModel):
    prompt: str


class Round(RoundBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    submissions: list["Submission"] = Relationship(back_populates="round")


class RoundPublic(RoundBase):
    id: int


class RoundPublicWithSubmissions(RoundPublic):
    submissions: list["SubmissionPublic"] = []


class MovieBase(SQLModel):
    name: str


class Movie(MovieBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    submissions: list["Submission"] = Relationship(back_populates="movie")


class MoviePublic(MovieBase):
    id: int


class SubmissionBase(SQLModel):
    round_id: int | None = Field(default=None, foreign_key="round.id")
    movie_id: int | None = Field(default=None, foreign_key="movie.id")


class Submission(SubmissionBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    round: Round = Relationship(back_populates="submissions")
    submitting_user: "User" = Relationship(
        back_populates="submitted_submission",
        sa_relationship_kwargs={"foreign_keys": "User.submitted_submission_id"},
    )
    voting_users: list["User"] = Relationship(
        back_populates="voted_submission",
        sa_relationship_kwargs={"foreign_keys": "User.voted_submission_id"},
    )
    movie: Movie = Relationship(back_populates="submissions")


class SubmissionPublic(SubmissionBase):
    id: int
    submitting_user: "UserPublic"
    voting_users: list["UserPublic"]
    movie: MoviePublic


class SubmissionCreate(SubmissionBase):
    name: str
    user: str | None = None


class UserBase(SQLModel):
    name: str

    submitted_submission_id: int | None = Field(
        default=None, foreign_key="submission.id"
    )
    voted_submission_id: int | None = Field(default=None, foreign_key="submission.id")


class User(UserBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    submitted_submission: Submission | None = Relationship(
        back_populates="submitting_user",
        sa_relationship_kwargs={"foreign_keys": "User.submitted_submission_id"},
    )
    voted_submission: Submission | None = Relationship(
        back_populates="voting_users",
        sa_relationship_kwargs={"foreign_keys": "User.voted_submission_id"},
    )


class UserPublic(UserBase):
    id: int


class UserCreate(UserBase):
    pass


class VoteCreate(SQLModel):
    submission_id: int
    voting_user_name: str | None = None


class CurrentState(SQLModel):
    state: str
