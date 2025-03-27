import { useRef, useState, useEffect, useContext } from "react";
import { UserContext } from "./UserContext.js";

import LoginScreen from "./LoginScreen.jsx";
import Container from "./Container.jsx";
import SubmissionView from "./SubmissionView.jsx";
import VotingView from "./VotingView.jsx";
import ResultView from "./ResultView.jsx";


export default function App() {
  const [gameState, setGameState] = useState(null);
  const [userInfo, setUserInfo] = useState(null);

  const setupGame = async (userInfo) => {
    await fetch(`http://localhost:8000/users/`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${userInfo.token.access_token}`,
      },
      body: JSON.stringify({
        name: userInfo.username,
      })
    })

    try {
      const response = await fetch("http://localhost:8000/state/", {
        method: "GET",
        headers: {
          "Authorization": `Bearer ${userInfo.token}`,
        },
      })
      const result = await response.json();
      setGameState(result.state)
    } catch (error) {
      console.error("Error game state:", error);
    }
  }

  const onLogin = async (userInfo) => {
    setUserInfo(userInfo);
    setupGame(userInfo);
  }

  if (userInfo === null) {
    return <LoginScreen onLogin={onLogin} />
  }

  let container = (
    <h1>
      Oops
    </h1>
  );

  if (gameState == "SubmissionState") {
    container = <SubmissionView setGameState={setGameState} />;
  } else if (gameState == "VotingState") {
    container = <VotingView setGameState={setGameState} />;
  } else if (gameState == "ResultState") {
    container = <ResultView setGameState={setGameState} />;
  }
  return <UserContext.Provider value={userInfo} ><Container>{container}</Container></UserContext.Provider >
}