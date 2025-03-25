import { useState, useEffect, useContext } from "react";
import { UserContext } from './UserContext.js';

import commonStyles from "./CommonStyles.module.css";
import styles from "./ResultView.module.css";


function SingleResult({ data, setGameState }) {
  const user = useContext(UserContext);

  return (
    <div className={styles.componentItem}>
      <h3 className={styles.componentTitle}>Movie: {data.name}</h3>
      <p className={styles.componentDescription}>Submitted by: {data.submitting_user.name}</p>

      <div className={styles.scoreContainer}>
        <span className={styles.sectionTitle}>Score:</span>
        <span className={styles.score}>{data.voting_users.length}</span>
      </div>

      <div className={styles.playersContainer}>
        <span className={styles.sectionTitle}>Voted for by:</span>
        <span className={styles.players}>{data.voting_users.map(data => data.name).join(", ")}</span>
      </div>
    </div>
  );
}

export default function ResultView({ setGameState }) {
  const [results, setResults] = useState({ movies: [] });

  useEffect(() => {
    const loadState = async () => {
      try {
        const response = await fetch("http://localhost:8000/round/", {
          method: "GET",
        })
        const result = await response.json();
        setResults(result);
      } catch (error) {
        console.error("Error submissions:", error);
      }
    }
    loadState()
  }, []);

  return (<>
    <p className={commonStyles.description}>The results are in.</p>
    <div className={commonStyles.componentList}>
      {results.movies.slice().sort((a, b) => b.voting_users.length - a.voting_users.length).map((data, i) => <SingleResult key={i} data={data} setGameState={setGameState} />)}
    </div>
  </>);
}