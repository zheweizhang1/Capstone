import { Box, useTheme } from "@mui/material";
import Header from "../../components/Header";
import Accordion from "@mui/material/Accordion";
import AccordionSummary from "@mui/material/AccordionSummary";
import AccordionDetails from "@mui/material/AccordionDetails";
import Typography from "@mui/material/Typography";
import ExpandMoreIcon from "@mui/icons-material/ExpandMore";
import { tokens } from "../../theme";

const FAQ = () => {
  const theme = useTheme();
  const colors = tokens(theme.palette.mode);
  return (
    <Box m="20px">
      <Header title="FAQ" subtitle="Frequently Asked Questions Page" />

      <Accordion defaultExpanded>
        <AccordionSummary expandIcon={<ExpandMoreIcon />}>
          <Typography color={colors.greenAccent[500]} variant="h5">
            What is the primary goal of this website?
          </Typography>
        </AccordionSummary>
        <AccordionDetails>
          <Typography>
            The goal is pretty simple. The website tracks your emotional state and helps
            you, the user, to be more mindful and aware of what made you happy that specific
            sunny day or sad in another.
          </Typography>
        </AccordionDetails>
      </Accordion>
      <Accordion defaultExpanded>
        <AccordionSummary expandIcon={<ExpandMoreIcon />}>
          <Typography color={colors.greenAccent[500]} variant="h5">
            How to get started?
          </Typography>
        </AccordionSummary>
        <AccordionDetails>
          <Typography>
            On the left, there's a "Recording" tab in which you can either record your voice
            or send a text message. Both options undergo sentiment analysis, however for the
            more accurate results, we encourage you to take voice recording route.
          </Typography>
        </AccordionDetails>
      </Accordion>
      <Accordion defaultExpanded>
        <AccordionSummary expandIcon={<ExpandMoreIcon />}>
          <Typography color={colors.greenAccent[500]} variant="h5">
            How do I track my emotional state?
          </Typography>
        </AccordionSummary>
        <AccordionDetails>
          <Typography>
            The sidebar includes a "Calendar". In there, you can see your individual data on
            what emotional state you were in that day. Later, we plan to add more functionality
            to the calendar, so you can leave pattern recognition of your emotions to us.
          </Typography>
        </AccordionDetails>
      </Accordion>
      <Accordion defaultExpanded>
        <AccordionSummary expandIcon={<ExpandMoreIcon />}>
          <Typography color={colors.greenAccent[500]} variant="h5">
            Do you have infographics?
          </Typography>
        </AccordionSummary>
        <AccordionDetails>
          <Typography>
            Yes. After you click on the "Pie Chart", you should see what emotions were the most and less
            prevalent, and everything in between, across all of our data on you.
          </Typography>
        </AccordionDetails>
      </Accordion>
    </Box>
  );
};

export default FAQ;
