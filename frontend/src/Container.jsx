import { useRef, useState, useEffect, useContext } from 'react';
import { UserContext } from './UserContext.js';

import styles from "./Container.module.css";


export default function Container({ children }) {
  const [prompt, setPrompt] = useState([])
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

  return (

    <div className={styles.container}>
      <div className={styles.floatingBox}>Logged in user: {user}</div>

      <div className={styles.card}>
        <h2 className={styles.title}>Prompt: "{prompt}"</h2>

        <hr className={styles.divider} />

        {children}
      </div>
    </div>
  );
}