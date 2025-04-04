import { useState, useEffect, useContext } from "react";
import { UserContext } from './UserContext.js';

import MovieCard from "./MovieCard.jsx";

import commonStyles from "./CommonStyles.module.css";
import containerStyles from "./Container.module.css";
import styles from "./ResultView.module.css";


function SingleResult({ data, setGameState }) {
  const userInfo = useContext(UserContext);

  return (
    <div className={commonStyles.submissionItem}>
      <MovieCard movieData={data.movie} />
      <p className={commonStyles.submissionDescription}>Submitted by: {data.submitting_user.name}</p>

      <div className={styles.entry}>
        <span className={styles.entryTitle}>Score:</span>
        <span className={styles.score}>{data.voting_users.length}</span>
      </div>

      <div className={styles.entry}>
        <span className={styles.entryTitle}>Voted for by:</span>
        <span className={styles.players}>{data.voting_users.map(data => data.name).join(", ")}</span>
      </div>

      <div className={styles.entry}>
        <span className={styles.entryTitle}>Comments:</span>
        <span className={styles.commentsEntry}>{data.comments.map(data => `${data.author.name}: ${data.text}`).join(", ")}</span>
      </div>
    </div>
  );
}

export default function ResultView({ singleRoundData, setGameState }) {
  return (<>
    <h2 className={containerStyles.title}><span className={containerStyles.promptPrefix}>Prompt:</span> "{singleRoundData.prompt}"</h2>
    <p className={commonStyles.description}>The final ranking is in.</p>
    <div className={commonStyles.submissionList}>
      {singleRoundData.submissions.slice().sort((a, b) => b.voting_users.length - a.voting_users.length).map((data, i) => <SingleResult key={i} data={data} setGameState={setGameState} />)}
    </div>
  </>);
}