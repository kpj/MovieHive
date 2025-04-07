from fastapi import Request, APIRouter, HTTPException

from backend import models, game_manager
from backend.routes import login_system


router = APIRouter()


@router.get("/state")
def get_state(
    *,
    request: Request,
    current_user: login_system.AuthenticatedUser,
) -> models.CurrentState:
    return request.app.state.game_manager.get_current_state_message(
        current_user.username
    )


@router.get("/round")
def get_round(*, request: Request) -> models.RoundPublicWithSubmissions:
    return request.app.state.game_manager.get_current_round()


@router.post("/round")
def create_round(
    *,
    request: Request,
    current_user: login_system.AuthenticatedUser,
    round: models.RoundCreate,
) -> models.CurrentState:
    request.app.state.game_manager.create_new_round(round)

    return request.app.state.game_manager.get_current_state_message(
        current_user.username
    )


@router.get("/rounds")
def get_rounds(*, request: Request) -> list[models.RoundPublicWithSubmissions]:
    return request.app.state.game_manager.get_all_rounds()


@router.post("/submissions/")
def add_submission(
    *,
    request: Request,
    current_user: login_system.AuthenticatedUser,
    submission: models.SubmissionCreate,
) -> models.CurrentState:
    if not request.app.state.game_manager.is_in_state(game_manager.SubmissionState):
        raise HTTPException(status_code=500, detail="Not in submission state")

    request.app.state.game_manager.add_submission(current_user.username, submission)

    request.app.state.game_manager.update()
    return request.app.state.game_manager.get_current_state_message(
        current_user.username
    )


@router.post("/vote/")
def add_vote(
    *,
    request: Request,
    current_user: login_system.AuthenticatedUser,
    vote: models.VoteCreate,
) -> models.CurrentState:
    if not request.app.state.game_manager.is_in_state(game_manager.VotingState):
        raise HTTPException(status_code=500, detail="Not in voting state")

    request.app.state.game_manager.add_vote(current_user.username, vote)

    request.app.state.game_manager.update()
    return request.app.state.game_manager.get_current_state_message(
        current_user.username
    )


@router.post("/users/")
def add_user(
    *,
    request: Request,
    current_user: login_system.AuthenticatedUser,
    user: models.UserCreate,
):
    assert user.name == current_user.username, (user, current_user)
    request.app.state.game_manager.add_player(user)


@router.post("/comments/")
def add_comment(
    *,
    request: Request,
    current_user: login_system.AuthenticatedUser,
    comment: models.CommentCreate,
):
    request.app.state.game_manager.add_comment(current_user.username, comment)
