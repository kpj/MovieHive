import { useState, useEffect, useContext } from "react";

import styles from "./MovieCard.module.css";


function PersonCard({ personData }) {
  const [name, picture_url] = personData.split(",");

  return (
    <div className={styles.personCard}>
      <img className={styles.personPicture} src={picture_url} />
      {name}
    </div>
  );
}

export default function MovieCard({ movieData }) {
  return (<div className={styles.movieCard}>
    <img className={styles.moviePoster} src={movieData.poster_url} />
    <div className={styles.movieInfo}>
      <h3>{movieData.name}</h3>
      <span>{movieData.release_date.split("-")[0]} - {movieData.directors.split(";").map((data, i) => data.split(",")[0]).join(", ")}</span>

      <div className={styles.actorsList}>
        {movieData.actors.split(";").map((data, i) => <PersonCard key={i} personData={data} />)}
      </div>

      <p>{movieData.description}</p>
    </div>
  </div>);
}