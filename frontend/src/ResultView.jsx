import { useState, useEffect, useContext } from "react";
import { UserContext } from './UserContext.js';


function SingleResult({ data, setGameState }) {
  const user = useContext(UserContext);

  return (
    <>
      {data.name} ({data.submitting_user.name}): {data.voting_users.length}
      <br />
    </>
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
        console.log(result)
        setResults(result)
      } catch (error) {
        console.error("Error submissions:", error);
      }
    }
    loadState()
  }, []);

  return (<>
    {results.movies.map((data, i) => <SingleResult key={i} data={data} setGameState={setGameState} />)}
  </>);
}