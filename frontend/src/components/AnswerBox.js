import React from "react";

const AnswerBox = ({ answer }) => {
  return (
    <div style={styles.answerSection}>
      <p style={styles.answerLabel}>Answer:</p>
      <p style={styles.answerText}>{answer}</p>
    </div>
  );
};

const styles = {
  answerSection: {
    marginTop: "30px"
  },
  answerLabel: {
    fontSize: "18px",
    fontWeight: "bold"
  },
  answerText: {
    marginTop: "10px",
    backgroundColor: "#2a2a2a",
    padding: "15px",
    borderRadius: "8px",
    whiteSpace: "pre-wrap"
  }
};

export default AnswerBox;
