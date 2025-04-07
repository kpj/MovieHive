import { useRef, useState, useEffect, useContext } from 'react';

import commonStyles from "./CommonStyles.module.css";


export default function WaitingView({ message }) {
  return (
    <>
      <p className={commonStyles.description}>{message}</p>
    </>
  );
}