import { useState } from "react";
import { BsArrowThroughHeartFill, BsArrowThroughHeart } from "react-icons/bs";

interface Props {
  onClick: () => void;
}

const IconicHeart = ({ onClick }: Props) => {
  const [iconic, setIconic] = useState(false);

  const toggle = () => {
    setIconic(!iconic);
    onClick();
  };

  if (iconic)
    return (
      <BsArrowThroughHeartFill color="#ff6b81" size={20} onClick={toggle} />
    );
  return <BsArrowThroughHeart size={20} onClick={onClick} />;
};

export default IconicHeart;
