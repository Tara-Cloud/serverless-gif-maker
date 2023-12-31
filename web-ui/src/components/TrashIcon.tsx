import { FaTrash } from "react-icons/Fa";
import { useState } from "react";
import GifService from "../services/gif-service";

interface TrashIconProps {
  s3_key: string;
}

const TrashIcon: React.FC<TrashIconProps> = ({ s3_key }) => {
  const [hovered, setHovered] = useState(false);

  const handleArchive = async () => {
    console.log("Archiving " + s3_key);

    try {
      const { request } = GifService.archiveGif(s3_key);
      const response = await request;
      return response;
    } catch (err: any) {
      console.log(err.message);
    }
  };

  return (
    <FaTrash
      size={20}
      onClick={() => handleArchive()}
      style={{ color: hovered ? "#570df8" : "white" }}
      onMouseEnter={() => setHovered(true)}
      onMouseLeave={() => setHovered(false)}
    />
  );
};

export default TrashIcon;
