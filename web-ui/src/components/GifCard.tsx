import React from "react";
import FaveHeart from "./FaveHeart";

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
        <FaveHeart s3_key={gifKey}></FaveHeart>
      </div>
    </div>
  );
};

export default GifCard;
