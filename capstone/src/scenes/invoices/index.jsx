import { Box, TextField, IconButton } from "@mui/material";
import { useTheme } from "@mui/material/styles";
import Header from "../../components/Header";
import { useState, useRef } from "react";
import MicIcon from '@mui/icons-material/Mic';
import StopIcon from '@mui/icons-material/Stop';
import PlayArrowOutlinedIcon from '@mui/icons-material/PlayArrowOutlined';

import { getLastnameAPI, uploadAudioAPI, sendMessageAPI } from '../../api';
import { useUser } from '../../UserContext';
import { useEffect } from "react";
import axios from 'axios';


const Recording = () => {
  const theme = useTheme();
  const [inputValue, setInputValue] = useState("");
  const [isRecording, setIsRecording] = useState(false);
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);

  const handleSubmit = async () => {
    console.log(inputValue);
    const formData = new FormData();
    formData.append("username", user.username);
    formData.append("message", inputValue);
    const response = await sendMessageAPI(formData);
    console.log('Sending the message. Response: ', response);
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

  const { user } = useUser(); // Access loginUser from UserContext
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
            '&:hover': {
              backgroundColor: theme.palette.primary.dark,
            },
          }}
        >
          <PlayArrowOutlinedIcon sx={{ fontSize: 40 }} />
        </IconButton>
      </Box>
    </Box>
  );
};

export default Recording;
