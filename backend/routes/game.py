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
def get_round(*, request: Request) -> models.RoundPublicWithSubmissions:
    return request.app.state.game_manager.get_current_round()


@router.post("/submissions/")
def add_submission(
    *,
    request: Request,
    current_user: login_system.AuthenticatedUser,
    submission: models.SubmissionCreate
) -> models.CurrentState:
    if not request.app.state.game_manager.is_in_state(game_manager.SubmissionState):
        raise HTTPException(status_code=500, detail="Not in submission state")

    assert submission.user is None, submission
    submission.user = current_user.username
    request.app.state.game_manager.add_submission(submission)

    request.app.state.game_manager.update()
    return models.CurrentState(
        state=request.app.state.game_manager._state.__class__.__name__
    )


@router.post("/vote/")
def add_vote(
    *,
    request: Request,
    current_user: login_system.AuthenticatedUser,
    vote: models.VoteCreate
) -> models.CurrentState:
    if not request.app.state.game_manager.is_in_state(game_manager.VotingState):
        raise HTTPException(status_code=500, detail="Not in voting state")

    vote.voting_user_name = current_user.username
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
