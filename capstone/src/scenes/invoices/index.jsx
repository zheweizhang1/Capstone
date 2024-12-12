import {
  Box,
  TextField,
  IconButton,
  List,
  ListItem,
  ListItemText,
} from "@mui/material";
import { useTheme } from "@mui/material/styles";
import Header from "../../components/Header";
import { useState, useRef } from "react";
import MicIcon from '@mui/icons-material/Mic';
import StopIcon from '@mui/icons-material/Stop';
import PlayArrowOutlinedIcon from '@mui/icons-material/PlayArrowOutlined';

import { getLastnameAPI, uploadAudioAPI, sendMessageAPI, getTodaysMessagesAPI } from '../../api';
import { useUser } from '../../UserContext';
import { useEffect } from "react";
import axios from 'axios';


const Recording = () => {
  const theme = useTheme();
  const [inputValue, setInputValue] = useState("");
  const [isRecording, setIsRecording] = useState(false);
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);

  const isDarkMode = theme.palette.mode === "dark"; // Check if dark mode is enabled
  const [chatMessages, setChatMessages] = useState([]); // Chat messages state

  const { user } = useUser(); // Access loginUser from UserContext
  const isTodaysMessagesFetched = useRef(false);

  /*
  // Simulate API response with fake data
  const fakeApiResponse = (userMessage) => {
    if (userMessage.toLowerCase().includes("hello")) {
      return "Hi there! How can I assist you today?";
    } else if (userMessage.toLowerCase().includes("recording")) {
      return "Recording functionality is enabled. Go ahead!";
    } else {
      return "Sorry, I didn’t quite get that. Can you please rephrase?";
    }
  };
  */

  // Handle sending user messages
  const handleSubmit = async () => {
    if (inputValue.trim() === "") return;

    // Add user message to chat
    setChatMessages((prev) => [
      ...prev,
      { sender: "user", text: inputValue },
    ]);

    //----------
    const formData = new FormData();
    formData.append("username", user.username);
    formData.append("message", inputValue);
    const response = await sendMessageAPI(formData);
    console.log('Sending the message. Response: ', response);
    //----------

    // Simulated API response
    /*
    const fakeResponse = fakeApiResponse(inputValue); // Remove this when API is working
    const responseMessage = fakeResponse; // Replace this with the actual response data
    */

    // Add bot response to chat
    setTimeout(() => {
      setChatMessages((prev) => [
        ...prev,
        { sender: "bot", text: response.assistant_response }, // Use actual API response here
      ]);
    }, 1000);

    // Clear input
    setInputValue("");
  };

  const startRecording = () => {
    navigator.mediaDevices.getUserMedia({ audio: true })
      .then(stream => {
        const mediaRecorder = new MediaRecorder(stream);
        mediaRecorderRef.current = mediaRecorder;
        audioChunksRef.current = [];
  
        mediaRecorder.ondataavailable = (event) => {
          audioChunksRef.current.push(event.data);
        };
  
        mediaRecorder.onstop = async () => {
          const audioBlob = new Blob(audioChunksRef.current, { type: "audio/wav" });
          const audioUrl = URL.createObjectURL(audioBlob);
          console.log("Recording saved:", audioUrl);
  
          const formData = new FormData();
          formData.append("username", user.username);
          formData.append("audio", audioBlob, "recording.wav");
          console.log(formData);
  
          const response = await uploadAudioAPI(formData);
          console.log('Sending the recording. Response: ', response);

          setChatMessages((prev) => [
            ...prev,
            { sender: "user", text: response.user_message },
          ]);
          setChatMessages((prev) => [
            ...prev,
            { sender: "bot", text: response.assistant_response },
          ]);
        };
  
        mediaRecorder.start();
        setIsRecording(true);
      })
      .catch(error => console.error("Error accessing microphone:", error));
  };
  

  const stopRecording = () => {
    mediaRecorderRef.current.stop();
    setIsRecording(false);
  };

  useEffect(() => {
    const console_log_lastname = async (e) => {
      console.log("Trying to get user's {" + user.username + "} last name");
      try {
        const response = await getLastnameAPI(user.username)
        if (response.lastname) {
          console.log("Logged user's last name is", response.lastname);
        } else {
          // Fallback to guest last name
          console.log("Using default guest last name:", user.lastname);
        }
      } catch (error) {
        console.error("Error at console_log_lastname:", error);
        // Fallback to guest last name
        console.log("Using default guest last name:", user.lastname);
      }
    }
    console_log_lastname();
  }, []);

  let fetched = false;
  useEffect(() => {
    const fetchTodaysMessages = async () => {
      if (isTodaysMessagesFetched.current) {
        return;
      }
      isTodaysMessagesFetched.current = true
      console.log('i fire once');
      console.log(`Trying to get today's messages for user: ${user.username}`);
      try {
        const response = await getTodaysMessagesAPI(user.username); // Replace with your API function
        if (response.length > 0) {
          console.log(`Retrieved ${response.length} messages for today.`);
          // Iterate through the response and update chat messages
          response.forEach((message) => {
            setChatMessages((prev) => [
              ...prev,
              { sender: "user", text: message.user_message },
              { sender: "bot", text: message.assistant_response },
            ]);
          });
        } else {
          console.log("No messages found for today.");
        }
      } catch (error) {
        console.error("Error fetching today's messages:", error);
      }
    }
    fetchTodaysMessages();
  }, []);

  return (
    <Box m="20px">
      <Header title="Recording" subtitle="Record your message here" />

      {/* Mic Icon button */}
      <Box display="flex" justifyContent="center" mt="20px">
        <IconButton
          onClick={isRecording ? stopRecording : startRecording}
          size="large"
          sx={{
            backgroundColor: isRecording ? theme.palette.error.main : theme.palette.primary.main,
            color: theme.palette.common.white,
            '&:hover': {
              backgroundColor: isRecording ? theme.palette.error.dark : theme.palette.primary.dark,
            },
          }}
        >
          {isRecording ? <StopIcon sx={{ fontSize: 40 }} /> : <MicIcon sx={{ fontSize: 40 }} />}
        </IconButton>
      </Box>

      {/* Text input with Play button */}
      <Box mt="20px" display="flex" alignItems="center" gap="10px">
        <TextField
          variant="outlined"
          placeholder="Type here"
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          sx={{ flexGrow: 1 }}
        />
        <IconButton
          onClick={handleSubmit}
          size="large"
          sx={{
            backgroundColor: theme.palette.primary.main,
            color: theme.palette.common.white,
            "&:hover": {
              backgroundColor: theme.palette.primary.dark,
            },
          }}
        >
          <PlayArrowOutlinedIcon sx={{ fontSize: 40 }} />
        </IconButton>
      </Box>

      {/* Chatbox */}
      <Box
        mt="20px"
        p="10px"
        borderRadius="10px"
        border={`1px solid ${theme.palette.divider}`}
        maxHeight="400px"
        overflow="auto"
      >
        <List>
          {chatMessages.map((message, index) => (
            <ListItem
              key={index}
              sx={{
                justifyContent:
                  message.sender === "user" ? "flex-end" : "flex-start",
              }}
            >
              <ListItemText
                primary={message.text}
                sx={{
                  textAlign: message.sender === "user" ? "right" : "left",
                  backgroundColor:
                    message.sender === "user"
                      ? theme.palette.primary.light
                      : theme.palette.grey[200],
                  color:
                    message.sender === "user"
                      ? theme.palette.common.white
                      : message.sender === "bot" && isDarkMode
                      ? "#3d3d3d" 
                      : theme.palette.text.primary, 
                  borderRadius: "10px",
                  padding: "10px",
                  maxWidth: "70%",
                }}
              />
            </ListItem>
          ))}
        </List>
      </Box>
    </Box>
  );
};

export default Recording;
