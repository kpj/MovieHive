import { useState, useEffect, useContext } from "react";
import { UserContext } from './UserContext.js';

import commonStyles from "./CommonStyles.module.css";
import styles from "./VotingView.module.css";


function SingleSubmission({ data, setGameState }) {
  const userInfo = useContext(UserContext);

  const addVote = () => {
    const foo = async () => {
      try {
        const response = await fetch(`http://localhost:8000/vote/`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "Authorization": `Bearer ${userInfo.token.access_token}`,
          },
          body: JSON.stringify({
            submission_id: data.id,
          })
        })
        const result = await response.json();
        setGameState(result.state);
      } catch (error) {
        console.error("Error:", error);
      }
    }
    foo()
  }

  return (
    <div className={styles.componentItem}>
      <h3 className={styles.componentTitle}>Movie: {data.movie.name}</h3>
      <p className={styles.componentDescription}>Submitted by: {data.submitting_user.name}</p>

      <button onClick={addVote} className={commonStyles.button}>Add Vote</button>
    </div>
  );
}

export default function VotingView({ setGameState }) {
  const userInfo = useContext(UserContext);
  const [submissions, setSubmissions] = useState([]);

  useEffect(() => {
    const loadState = async () => {
      try {
        const response = await fetch("http://localhost:8000/round/", {
          method: "GET",
          headers: {
            "Authorization": `Bearer ${userInfo.token.access_token}`,
          },
        })
        const result = await response.json();
        setSubmissions(result.submissions)
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