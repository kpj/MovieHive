from collections.abc import Mapping

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


class RoundCreate(RoundBase):
    pass


class MovieBase(SQLModel):
    name: str
    requested_name: str
    poster_url: str
    description: str
    genre: str
    release_date: str
    actors: str
    directors: str


class Movie(MovieBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    submissions: list["Submission"] = Relationship(back_populates="movie")


class MoviePublic(MovieBase):
    id: int


class SubmissionBase(SQLModel):
    round_id: int | None = Field(default=None, foreign_key="round.id")
    movie_id: int | None = Field(default=None, foreign_key="movie.id")
    submitting_user_id: int | None = Field(default=None, foreign_key="user.id")


class Submission(SubmissionBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    round: Round = Relationship(back_populates="submissions")
    submitting_user: "User" = Relationship(
        back_populates="submitted_submission",
        sa_relationship_kwargs={"foreign_keys": "Submission.submitting_user_id"},
    )
    voting_users: list["User"] = Relationship(
        back_populates="voted_submission",
        sa_relationship_kwargs={"foreign_keys": "User.voted_submission_id"},
    )
    movie: Movie = Relationship(back_populates="submissions")
    comments: list["Comment"] = Relationship(back_populates="submission")


class SubmissionPublic(SubmissionBase):
    id: int
    submitting_user: "UserPublic"
    voting_users: list["UserPublic"]
    movie: MoviePublic
    comments: list["CommentPublic"]


class SubmissionCreate(SubmissionBase):
    name: str
    comment: str | None = None


class CommentBase(SQLModel):
    submission_id: int | None = Field(default=None, foreign_key="submission.id")
    author_id: int | None = Field(default=None, foreign_key="user.id")
    text: str


class Comment(CommentBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    submission: Submission = Relationship(back_populates="comments")
    author: "User" = Relationship(back_populates="comments")


class CommentPublic(CommentBase):
    author: "UserPublic"


class CommentCreate(CommentBase):
    pass


class UserBase(SQLModel):
    name: str
    voted_submission_id: int | None = Field(default=None, foreign_key="submission.id")


class User(UserBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    submitted_submission: Submission | None = Relationship(
        back_populates="submitting_user",
        sa_relationship_kwargs={"foreign_keys": "Submission.submitting_user_id"},
    )
    voted_submission: Submission | None = Relationship(
        back_populates="voting_users",
        sa_relationship_kwargs={"foreign_keys": "User.voted_submission_id"},
    )
    comments: list["Comment"] = Relationship(back_populates="author")


class UserPublic(UserBase):
    id: int


class UserCreate(UserBase):
    pass


class VoteCreate(SQLModel):
    submission_id: int
    all_comments: Mapping[int, str]


class CurrentState(SQLModel):
    state: str
    player_state: str | None = None
