from fastapi import Request, APIRouter, HTTPException


from backend import models, game_manager
from backend.routes import login_system


router = APIRouter()


@router.get("/state")
def get_state(request: Request) -> models.CurrentState:
    return models.CurrentState(
        state=request.app.state.game_manager._state.__class__.__name__
    )


@router.get("/round")
def get_round(*, request: Request) -> models.RoundPublicWithMovies:
    return request.app.state.game_manager.get_current_round()


@router.post("/movies/")
def add_movie(
    *,
    request: Request,
    current_user: login_system.AuthenticatedUser,
    movie: models.MovieCreate
) -> models.CurrentState:
    if not request.app.state.game_manager.is_in_state(game_manager.SubmissionState):
        raise HTTPException(status_code=500, detail="Not in submission state")

    assert movie.user is None, movie
    movie.user = current_user.username
    request.app.state.game_manager.add_movie(movie)

    request.app.state.game_manager.update()
    return models.CurrentState(
        state=request.app.state.game_manager._state.__class__.__name__
    )


@router.post("/vote/")
def add_vote(*, request: Request, vote: models.VoteCreate) -> models.CurrentState:
    if not request.app.state.game_manager.is_in_state(game_manager.VotingState):
        raise HTTPException(status_code=500, detail="Not in voting state")

    request.app.state.game_manager.add_vote(vote)

    request.app.state.game_manager.update()
    return models.CurrentState(
        state=request.app.state.game_manager._state.__class__.__name__
    )


@router.post("/users/")
def add_user(
    *,
    request: Request,
    current_user: login_system.AuthenticatedUser,
    user: models.UserCreate
):
    assert user.name == current_user.username, (user, current_user)
    request.app.state.game_manager.add_player(user)
