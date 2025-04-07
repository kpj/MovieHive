import { useState, useEffect, useContext, useRef } from "react";

import ResultView from "./ResultView.jsx";
import { UserContext } from './UserContext.js';

import commonStyles from "./CommonStyles.module.css";
import containerStyles from "./Container.module.css";


function PromptSubmission({ setGameState }) {
  const [prompt, setPrompt] = useState([])
  const inputRefs = useRef({});
  const userInfo = useContext(UserContext);

  useEffect(() => {

  }, []);

  const sendPrompt = async () => {
    const data = {
      prompt: inputRefs.current.prompt.value,
    };

    try {
      const response = await fetch("http://localhost:8000/round/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${userInfo.token.access_token}`,
        },
        body: JSON.stringify(data)
      });
      const result = await response.json();
      setGameState(result);
    } catch (error) {
      console.error("Error sending submission:", error);
    }
  };

  return (
    <>
      <p className={containerStyles.title}>Enter a new prompt</p>
      <input
        type="text"
        placeholder="Prompt"
        ref={(el) => (inputRefs.current.prompt = el)}
        className={commonStyles.input}
        required
      />
      <button onClick={sendPrompt} className={commonStyles.button}>Submit</button>
    </>
  );
}

export default function OverView({ setGameState }) {
  const [results, setResults] = useState([]);
  const userInfo = useContext(UserContext);

  useEffect(() => {
    const loadState = async () => {
      try {
        const response = await fetch("http://localhost:8000/rounds/", {
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

  return (
    <div className={containerStyles.container}>
      <div className={containerStyles.floatingBox}>Logged in user: {userInfo.username}</div>

      <div className={containerStyles.card}>
        <PromptSubmission setGameState={setGameState} />
      </div>

      <hr />

      <div className={containerStyles.card}>
        {results.map(data => <div key={data.id} className={containerStyles.card}><ResultView singleRoundData={data} setGameState={setGameState} /></div>)}
        {results.length === 0 && "No previous rounds (yet)."}
      </div>
    </div>
  );
}