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
import MicIcon from "@mui/icons-material/Mic";
import StopIcon from "@mui/icons-material/Stop";
import PlayArrowOutlinedIcon from "@mui/icons-material/PlayArrowOutlined";

import { useUser } from "../../UserContext";

const Recording = () => {
  const theme = useTheme();
  const isDarkMode = theme.palette.mode === "dark"; // Check if dark mode is enabled
  const [inputValue, setInputValue] = useState("");
  const [isRecording, setIsRecording] = useState(false);
  const [chatMessages, setChatMessages] = useState([]); // Chat messages state
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);

  const { user } = useUser(); // Access loginUser from UserContext

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

  // Handle sending user messages
  const handleSubmit = async () => {
    if (inputValue.trim() === "") return;

    // Add user message to chat
    setChatMessages((prev) => [
      ...prev,
      { sender: "user", text: inputValue },
    ]);

    // Simulated API response
    const fakeResponse = fakeApiResponse(inputValue); // Remove this when API is working
    const responseMessage = fakeResponse; // Replace this with the actual response data

    // Add bot response to chat
    setTimeout(() => {
      setChatMessages((prev) => [
        ...prev,
        { sender: "bot", text: responseMessage }, // Use actual API response here
      ]);
    }, 1000);

    // Clear input
    setInputValue("");
  };

  return (
    <Box m="20px">
      <Header title="Recording" subtitle="Record your message here" />

      {/* Mic Icon button */}
      <Box display="flex" justifyContent="center" mt="20px">
        <IconButton
          onClick={() => {}}
          size="large"
          sx={{
            backgroundColor: isRecording
              ? theme.palette.error.main
              : theme.palette.primary.main,
            color: theme.palette.common.white,
            "&:hover": {
              backgroundColor: isRecording
                ? theme.palette.error.dark
                : theme.palette.primary.dark,
            },
          }}
        >
          {isRecording ? (
            <StopIcon sx={{ fontSize: 40 }} />
          ) : (
            <MicIcon sx={{ fontSize: 40 }} />
          )}
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
