import React, { createContext, useState, useContext } from 'react';

const UserContext = createContext();

export const UserProvider = ({ children }) => {
  const [user, setUser] = useState({
    username: "Guest",
    firstname: "Guest's firstname",
    lastname: "Guest's lastname"
  });

  const loginUser = (userData) => {
    setUser(userData);
  };

  const logoutUser = () => {
    setUser({ username: "Guest" }); // Reset to "Guest" on logout
  };

  return (
    <UserContext.Provider value={{ user, loginUser, logoutUser }}>
      {children}
    </UserContext.Provider>
  );
};

export const useUser = () => {
  return useContext(UserContext);
};
