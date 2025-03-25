import { useState, useEffect, useContext } from "react";
import { UserContext } from './UserContext.js';

import commonStyles from "./CommonStyles.module.css";
import styles from "./VotingView.module.css";


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
    <div className={styles.componentItem}>
      <h3 className={styles.componentTitle}>Movie: {data.name}</h3>
      <p className={styles.componentDescription}>Submitted by: {data.submitting_user.name}</p>

      <button onClick={addVote} className={commonStyles.button}>Add Vote</button>
    </div>
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
    <p className={commonStyles.description}>Vote for the movie which you think fits the prompt best (you cannot vote for your own movie).</p>
    <div className={commonStyles.componentList}>
      {submissions.map((sub, i) => <SingleSubmission key={i} data={sub} setGameState={setGameState} />)}
    </div>
  </>);
}