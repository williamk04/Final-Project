// src/components/CardStat.js

import { Card } from "react-bootstrap";

const CardStat = ({ title, value, color }) => {
  return (
    <Card className={`text-white mb-3`} style={{ backgroundColor: color }}>
      <Card.Body>
        <Card.Title>{title}</Card.Title>
        <Card.Text style={{ fontSize: "1.5rem", fontWeight: "bold" }}>
          {value}
        </Card.Text>
      </Card.Body>
    </Card>
  );
};

export default CardStat;
