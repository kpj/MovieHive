import { useRef, useState, useEffect, useContext } from 'react';
import { UserContext } from './UserContext.js';

import commonStyles from "./CommonStyles.module.css";


export default function SubmissionView({ setGameState }) {
  const [prompt, setPrompt] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const inputRefs = useRef({});
  const userInfo = useContext(UserContext);

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
      comment: inputRefs.current.comment.value,
    };

    try {
      setIsLoading(true);
      const response = await fetch("http://localhost:8000/submissions/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${userInfo.token.access_token}`,
        },
        body: JSON.stringify(data)
      });
      const result = await response.json();
      setGameState(result.state);
    } catch (error) {
      console.error("Error sending submission:", error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <>
      <p className={commonStyles.description}>Submit the title of the movie which you think fits the prompt best.</p>
      <input
        type="text"
        placeholder="Movie"
        ref={(el) => (inputRefs.current.movie = el)}
        className={commonStyles.input}
        required
        disabled={isLoading}
      />
      <input
        type="text"
        placeholder="Comment"
        ref={(el) => (inputRefs.current.comment = el)}
        className={commonStyles.input}
        disabled={isLoading}
      />
      <button onClick={sendSubmission} className={commonStyles.button} disabled={isLoading}>{isLoading ? "Loading..." : "Submit"}</button>
    </>
  );
}