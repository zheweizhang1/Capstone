import axios from 'axios';

const API_URL = 'http://localhost:5000/api/user'; // Flask backend API

export const fetchUserData = async () => {
  try {
    const response = await axios.get(API_URL);
    return response.data; // Return the user data
  } catch (error) {
    console.error("Error fetching user data:", error);
    throw error; // Rethrow the error for handling in the component
  }
};


export const createUser = async (userData) => {
  try {
    const response = await axios.post(API_URL, userData);
    return response.data; // Return the created user data
  } catch (error) {
    console.error("Error creating user tehre:", error);
    throw error; // Rethrow the error for handling in the component
  }
};