import { useRef, useState, useEffect, useContext } from "react";
import { UserContext } from "./UserContext.js";
import SubmissionView from "./SubmissionView.jsx";
import VotingView from "./VotingView.jsx";
import ResultView from "./ResultView.jsx";


export default function App() {
  const [gameState, setGameState] = useState([]);
  const [user, setUser] = useState([]);

  const hasPrompted = useRef(false); // Fix for double prompt on startup in react dev mode (components are rendered twice to detect side-effects)

  const setupGame = async (username) => {
    await fetch(`http://localhost:8000/users/`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        name: username,
      })
    })

    try {
      const response = await fetch("http://localhost:8000/state/", {
        method: "GET",
      })
      const result = await response.json();
      setGameState(result.state)
    } catch (error) {
      console.error("Error game state:", error);
    }
  }

  // Call this once after page has loaded
  useEffect(() => {
    let username = null;
    if (!hasPrompted.current) {
      username = prompt("Enter your username");
      setUser(username);
      hasPrompted.current = true;
      setupGame(username)
    }
  }, []);

  let container = (
    <h1>
      Oops
    </h1>
  );

  if (gameState == "SubmissionState") {
    container = (<SubmissionView setGameState={setGameState} />);
  } else if (gameState == "VotingState") {
    container = (<VotingView setGameState={setGameState} />);
  } else if (gameState == "ResultState") {
    container = (<ResultView setGameState={setGameState} />);
  }
  return <UserContext.Provider value={user}>{container}</UserContext.Provider>
}