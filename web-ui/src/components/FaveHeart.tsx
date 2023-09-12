import { AiFillHeart, AiOutlineHeart } from "react-icons/ai";
import { useState, useEffect } from "react";
import GifService from "../services/gif-service";

interface FaveHeartProps {
  s3_key: string;
}

const FaveHeart: React.FC<FaveHeartProps> = ({ s3_key }) => {
  const [faved, setFaved] = useState(false);
  const [hovered, setHovered] = useState(false);
  // create state variable for tags of type array of key value pairs
  const [tags, setTags] = useState<Array<{
    Key: string;
    Value: string;
  }> | null>(null); // ["favorite", "funny", "cute"]

  const checkTags = async () => {
    const { request } = GifService.getTags(s3_key);
    const response = await request;
    if (response.data.Tags) {
      setTags(response.data.Tags);
      const favoriteTag = response.data.Tags.find(
        (tag: { Key: string }) => tag.Key === "favorite"
      );
      if (favoriteTag) {
        setFaved(true);
      }
    }
  };

  const handleFave = async () => {
    const faveTag = {
      Key: "favorite",
      Value: "true",
    };
    if (tags) {
      tags.push(faveTag);
    } else {
      setTags([faveTag]);
      try {
        const { request } = GifService.tagGif(s3_key, tags);
        const response = await request;
        console.log(response.data);
        setFaved(true);
        console.log("Tags: " + tags);
        console.log("Favoriting " + s3_key);
        return response;
      } catch (err: any) {
        console.log(err.message);
      }
    }
  };

  const handleUnfave = async () => {
    const newTags = tags?.filter((tag) => tag.Key !== "favorite") || null;
    setTags(newTags);
    try {
      const { request } = GifService.tagGif(s3_key, newTags);
      const response = await request;
      console.log("Tags: " + tags);
      setFaved(false);
      console.log("Tags: " + tags);
      console.log("Unfavoriting " + s3_key);
      return response;
    } catch (err: any) {
      console.log(err.message);
    }
  };

  const getIconColor = () => {
    if (hovered) return "#570df8";
    else if (faved) return "#f000b8";
    else return "white";
  };

  useEffect(() => {
    checkTags();
  }, []);

  if (faved)
    return (
      <AiFillHeart
        size={20}
        onClick={() => handleUnfave()}
        style={{ color: getIconColor() }}
        onMouseEnter={() => setHovered(true)}
        onMouseLeave={() => setHovered(false)}
      />
    );
  return (
    <AiOutlineHeart
      size={20}
      onClick={() => handleFave()}
      style={{ color: getIconColor() }}
      onMouseEnter={() => setHovered(true)}
      onMouseLeave={() => setHovered(false)}
    />
  );
};

export default FaveHeart;
