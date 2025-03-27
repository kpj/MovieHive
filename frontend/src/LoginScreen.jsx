import { useRef, useState, useEffect, useContext } from 'react';

import containerStyles from "./Container.module.css";
import commonStyles from "./CommonStyles.module.css";
import styles from "./LoginScreen.module.css";


export default function LoginScreen({ onLogin }) {
  const inputRefs = useRef({});

  const onClick = async () => {
    const username = inputRefs.current.username.value;

    let data = new URLSearchParams()
    data.append("username", username);
    data.append("password", inputRefs.current.password.value);

    try {
      const response = await fetch("http://localhost:8000/token/", {
        method: "POST",
        body: data,
      });
      const token = await response.json();

      if ("access_token" in token) {
        onLogin({
          "username": username,
          "token": token,
        });
      } else {
        alert(token["detail"])
      }
    } catch (error) {
      console.error("Error logging in:", error);
    }
  };

  return (
    <div className={containerStyles.container}>
      <div className={containerStyles.card}>
        <h2 className={containerStyles.title}>Login</h2>
        <hr className={containerStyles.divider} />

        <form className={styles.form}>
          <input
            type="text"
            placeholder="Username"
            ref={(el) => (inputRefs.current.username = el)}
            className={styles.input}
            required
          />
          <input
            type="password"
            placeholder="Password"
            ref={(el) => (inputRefs.current.password = el)}
            className={styles.input}
            required
          />
          <button type="button" className={commonStyles.button} onClick={onClick}>Login</button>
        </form>
      </div>
    </div>
  );
}