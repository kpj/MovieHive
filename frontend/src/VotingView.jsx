import { useState, useEffect, useContext } from "react";
import { UserContext } from './UserContext.js';


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

export default function VotingView({ setGameState }) {
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