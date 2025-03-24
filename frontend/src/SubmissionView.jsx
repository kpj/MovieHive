import { useRef, useState, useEffect, useContext } from 'react';
import { UserContext } from './UserContext.js';


export default function SubmissionView({ setGameState }) {
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