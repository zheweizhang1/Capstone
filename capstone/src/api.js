import axios from 'axios';

const API_URL = 'http://127.0.0.1:5000/api/';
axios.defaults.withCredentials = true;

export const logInAPI = async (userData) => {
  try {
    const response = await axios.post(`${API_URL}login`, userData);
    return response.data;
  } catch (error) {
    console.error("Error at logInAPI", error);
    throw error;
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

export const fetchUserDataAPI = async (userData) => {
  try {
    const response = await axios.post(`${API_URL}login`, userData);
    return response.data; // Return the user data
  } catch (error) {
    console.error("Error at fetchUserDataAPI", error);
    throw error; // Rethrow the error for handling in the component
  }
};

export const getLastnameAPI = async (username) => {
  try {
    const response = await axios.get(`${API_URL}lastname`, {
      params: { username }  // Send username as a query parameter
    });
    return response.data;
  } catch (error) {
    console.error("Error at getLastnameAPI", error);
    throw error;
  }
};

export const getEventsAPI = async (username) => {
  try {
    const response = await axios.get(`${API_URL}events`, {
      params: { username }
    });
    return response.data;
  } catch (error) {
    console.error("Error at getEventsAPI", error);
    throw error;
  }
};

export const uploadAudioAPI = async (formData) => {
  try {
    const response = await axios.post(`${API_URL}handle_audio_message`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      },
      withCredentials: true
    });
    return response.data;
  } catch (error) {
    console.error("Error at uploadAudioAPI", error);
    throw error;
  }
};

export const sendMessageAPI = async (formData) => {
  try {
    const response = await axios.post(`${API_URL}handle_text_message`, formData, {
      /*
      headers: {
        'Content-Type': 'multipart/form-data'
      },
      withCredentials: true
      */
    });
    return response.data;
  } catch (error) {
    console.error("Error at sendMessageAPI", error);
    throw error;
  }
};

export const getEmotionCountsForPieChartAPI = async (username) => {
  try {
    const response = await axios.get(`${API_URL}get_emotion_counts_for_pie_chart`, {
      params: { username }  // Send username as a query parameter
    });
    return response.data;
  } catch (error) {
    console.error("Error at getEmotionCountsForPieChartAPI", error);
    throw error;
  }
};

export const getMessageCountsForLineChartAPI = async (username) => {
  try {
    const response = await axios.get(`${API_URL}get_messages_counts_for_line_chart`, {
      params: { username }  // Send username as a query parameter
    });
    return response.data;
  } catch (error) {
    console.error("Error at getMessagesCountsForLineChartAPI", error);
    throw error;
  }
};

export const getTotalMessagesOfUserAPI = async (username) => {
  try {
    const response = await axios.get(`${API_URL}get_total_messages`, {
      params: { username }  // Send username as a query parameter
    });
    return response.data;
  } catch (error) {
    console.error("Error at getTotalMessagesOfUserAPI", error);
    throw error;
  }
};