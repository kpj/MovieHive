import { useRef, useState, useEffect, useContext } from 'react';
import { UserContext } from './UserContext.js';

function RecordItem({ record }) {
  return (
    <div>
      <h3>{record.movie}</h3>
      <p>{record.comment}</p>
    </div>
  )
}

function SubmissionView({ setGameState }) {
  const [prompt, setPrompt] = useState([])
  const inputRefs = useRef({});
  const user = useContext(UserContext);

  useEffect(() => {
    const loadState = async () => {
      try {
        const response = await fetch("http://localhost:8000/round/", {
          method: "GET",
        })
        const result = await response.json();
        setPrompt(result.prompt)
      } catch (error) {
        console.error("Error game state:", error);
      }
    }
    loadState()
  }, []);

  const sendSubmission = async () => {
    const data = {
      name: inputRefs.current.movie.value,
      user: user,
    };
    console.log(data)

    try {
      const response = await fetch("http://localhost:8000/movies/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify(data)
      });
      const result = await response.json();
      console.log("State", result.state);
      setGameState(result.state);
    } catch (error) {
      console.error("Error sending submission:", error);
    }
  };

  return (
    <>
      <h1>{prompt}</h1>
      <input
        type="text"
        placeholder="Movie"
        ref={(el) => (inputRefs.current.movie = el)}
      />
      <button onClick={sendSubmission}>Submit</button>
    </>
  );
}

function SingleSubmission({ data, setGameState }) {
  const user = useContext(UserContext);

  const addVote = () => {
    console.log(user)
    const foo = async () => {
      try {
        const response = await fetch(`http://localhost:8000/vote/`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json"
          },
          body: JSON.stringify({
            movie_id: data.id,
            voting_user_id: user,
          })
        })
        const result = await response.json();
        console.log("State", result.state);
        setGameState(result.state);
      } catch (error) {
        console.error("Error:", error);
      }
    }
    foo()
  }

  return (
    <>
      Movie: {data.name},
      Submitted by: {data.submitting_user.name}<br />
      <button onClick={addVote}>Add Vote</button>
      <br /><br />
    </>
  );
}

function VotingView({ setGameState }) {
  const [submissions, setSubmissions] = useState([]);

  useEffect(() => {
    const loadState = async () => {
      try {
        const response = await fetch("http://localhost:8000/round/", {
          method: "GET",
        })
        const result = await response.json();
        setSubmissions(result.movies)
      } catch (error) {
        console.error("Error submissions:", error);
      }
    }
    loadState()
  }, []);

  return (<>
    {submissions.map((sub, i) => <SingleSubmission key={i} data={sub} setGameState={setGameState} />)}
  </>);
}

function SingleResult({ data, setGameState }) {
  const user = useContext(UserContext);

  return (
    <>
      {data.name} ({data.submitting_user.name}): {data.voting_users.length}
      <br />
    </>
  );
}

function ResultView({ setGameState }) {
  const [results, setResults] = useState({ movies: [] });

  useEffect(() => {
    const loadState = async () => {
      try {
        const response = await fetch("http://localhost:8000/round/", {
          method: "GET",
        })
        const result = await response.json();
        console.log(result)
        setResults(result)
      } catch (error) {
        console.error("Error submissions:", error);
      }
    }
    loadState()
  }, []);

  return (<>
    {results.movies.map((data, i) => <SingleResult key={i} data={data} setGameState={setGameState} />)}
  </>);
}

function App() {
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

export default App;
