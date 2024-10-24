import React, { createContext, useState, useContext } from 'react';

const UserContext = createContext();

export const UserProvider = ({ children }) => {
  const [user, setUser] = useState(null);

  const loginUser = (userData) => {
    setUser(userData);  // Updates the user data with logged-in user's details
  };

  const logoutUser = () => {
    setUser(null);  // Clears user data upon logout
  };

  return (
    <UserContext.Provider value={{ user, loginUser, logoutUser }}>
      {children}
    </UserContext.Provider>
  );
};

export const useUser = () => {
    return useContext(UserContext); // Custom hook to use user context
  };