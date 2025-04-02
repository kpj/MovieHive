import { useState, useEffect, useContext, useRef } from "react";
import { UserContext } from './UserContext.js';

import MovieCard from "./MovieCard.jsx";

import commonStyles from "./CommonStyles.module.css";


function SingleSubmission({ data, setGameState, inputRefs }) {
  const userInfo = useContext(UserContext);

  const addVote = () => {
    const foo = async () => {
      let commentData = {};
      for (let key of Object.keys(inputRefs.current.comments)) {
        const value = inputRefs.current.comments[key];
        if (value.length > 0) {
          commentData[key] = value;
        }
      }

      try {
        const response = await fetch(`http://localhost:8000/vote/`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "Authorization": `Bearer ${userInfo.token.access_token}`,
          },
          body: JSON.stringify({
            submission_id: data.id,
            all_comments: commentData,
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
    <div className={commonStyles.submissionItem}>
      <MovieCard movieData={data.movie} />
      <p className={commonStyles.submission}>Submitted by: {data.submitting_user.name}</p>

      <input
        type="text"
        placeholder="Comment"
        onChange={(e) => { inputRefs.current.comments[data.id] = e.target.value }}
        className={commonStyles.input}
      />

      <button onClick={addVote} className={commonStyles.button}>Add Vote</button>
    </div >
  );
}

export default function VotingView({ setGameState }) {
  const userInfo = useContext(UserContext);
  const [submissions, setSubmissions] = useState([]);
  const inputRefs = useRef({ comments: {} });

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
    <p className={commonStyles.description}>Write comments wherever you feel like it and then vote for the movie which you think fits the prompt best (you cannot vote for your own movie).</p>
    <div className={commonStyles.submissionList}>
      {submissions.map((sub, i) => <SingleSubmission key={i} data={sub} setGameState={setGameState} inputRefs={inputRefs} />)}
    </div>
  </>);
}