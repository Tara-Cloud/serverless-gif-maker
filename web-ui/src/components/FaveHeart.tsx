import { AiFillHeart, AiOutlineHeart } from "react-icons/ai";
import { useState, useEffect } from "react";
import GifService from "../services/gif-service";

interface FaveHeartProps {
  s3_key: string;
}

const FaveHeart: React.FC<FaveHeartProps> = ({ s3_key }) => {
  const [faved, setFaved] = useState(false);

  const checkFave = async () => {
    const { request } = GifService.getTags(s3_key);
    const response = await request;
    const tags = response.data.Tags;
    if (tags) {
      for (let i = 0; i < tags.length; i++) {
        console.log(tags);
        if (tags[i] === "favorite") {
          setFaved(true);
          return;
        }
      }
    }
  };

  const handleFave = async () => {
    console.log("Favoriting " + s3_key);
    const tags = {
      Key: "favorite",
      Value: "true",
    };
    try {
      const { request } = GifService.tagGif(s3_key, tags);
      const response = await request;
      setFaved(true);
      return response;
    } catch (err: any) {
      console.log(err.message);
    }
  };

  const handleUnfave = () => {
    console.log("Unfavorited " + s3_key);
    setFaved(false);
  };

  useEffect(() => {
    checkFave();
  }, []);

  if (faved)
    return (
      <AiFillHeart color="#ff6b81" size={20} onClick={() => handleUnfave()} />
    );
  return <AiOutlineHeart size={20} onClick={() => handleFave()} />;
};

export default FaveHeart;
