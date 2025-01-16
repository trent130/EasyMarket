import { useState } from 'react';

const useVisibility = () => {
  const [isVisible, setIsVisible] = useState<boolean>(false);
  const toggleVisibility = () => setIsVisible((prevState) => !prevState);
  return { isVisible, toggleVisibility };
};

export default useVisibility;