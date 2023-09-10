import React from "react";
import FaveHeart from "./FaveHeart";
import TrashIcon from "./TrashIcon";

// props interface
interface GifCardProps {
  gifURL: string;
  gifKey: string;
}

// Functional component that displays an image based on the provided URL
const GifCard: React.FC<GifCardProps> = ({ gifURL, gifKey }) => {
  return (
    <div className="card card-compact glass">
      <img src={gifURL} alt={gifKey} className="gif-item" loading="lazy" />
      <div className="card-body items-center text-center">
        <h2 className="card-title">{gifKey}</h2>
        <div style={{ display: "flex", gap: "10px" }}>
          <TrashIcon s3_key={gifKey}></TrashIcon>
          <FaveHeart s3_key={gifKey}></FaveHeart>
        </div>
      </div>
    </div>
  );
};

export default GifCard;
