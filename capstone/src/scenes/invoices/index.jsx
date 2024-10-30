import { Box, TextField, IconButton } from "@mui/material";
import { useTheme } from "@mui/material/styles";
import Header from "../../components/Header";
import { useState, useRef } from "react";
import MicIcon from '@mui/icons-material/Mic';
import StopIcon from '@mui/icons-material/Stop';
import PlayArrowOutlinedIcon from '@mui/icons-material/PlayArrowOutlined';

const Invoices = () => {
  const theme = useTheme();
  const [inputValue, setInputValue] = useState("");
  const [isRecording, setIsRecording] = useState(false);
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);

  const handleSubmit = () => {
    console.log(inputValue);
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

        mediaRecorder.onstop = () => {
          const audioBlob = new Blob(audioChunksRef.current, { type: "audio/wav" });
          const audioUrl = URL.createObjectURL(audioBlob);
          console.log("Recording saved:", audioUrl);
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
          <PlayArrowOutlinedIcon sx={{ fontSize: 40 }}/>
        </IconButton>
      </Box>
    </Box>
  );
};

export default Invoices;
