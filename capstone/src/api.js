import axios from 'axios';

const API_URL = 'http://localhost:5000/api/'; // Flask backend API

export const logInAPI = async (userData) => {
  try {
    const response = await axios.post(`${API_URL}login`, userData);
    return response.data; // Return the user data
  } catch (error) {
    console.error("Error at logInAPI", error);
    throw error; // Rethrow the error for handling in the component
  }
};


export const signUpAPI = async (userData) => {
  try {
    const response = await axios.post(`${API_URL}signup`, userData);
    return response.data; // Return the created user data
  } catch (error) {
    console.error("Error at signUpAPI", error);
    throw error; // Rethrow the error for handling in the component
  }
};


export const fetchUserData = async (userData) => {
  try {
    const response = await axios.post(`${API_URL}login`, userData);
    return response.data; // Return the user data
  } catch (error) {
    console.error("Error at logInAPI", error);
    throw error; // Rethrow the error for handling in the component
  }
};