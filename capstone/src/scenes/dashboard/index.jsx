import { Box, Button, IconButton, Typography, useTheme } from "@mui/material";
import { tokens } from "../../theme";
import { mockTransactions } from "../../data/mockData";
import DownloadOutlinedIcon from "@mui/icons-material/DownloadOutlined";
import EmailIcon from "@mui/icons-material/Email";
import PointOfSaleIcon from "@mui/icons-material/PointOfSale";
import PersonAddIcon from "@mui/icons-material/PersonAdd";
import TrafficIcon from "@mui/icons-material/Traffic";
import Header from "../../components/Header";
import LineChart from "../../components/LineChart";
import GeographyChart from "../../components/GeographyChart";
import BarChart from "../../components/BarChart";
import StatBox from "../../components/StatBox";
import ProgressCircle from "../../components/ProgressCircle";

import { getTotalMessagesOfUserAPI, getAnalyticsAPI } from "../../api";
import { useUser } from "../../UserContext";
import { useState, useEffect } from "react";
import PieChart from "../../components/PieChart";

import { useRef } from "react";

/* 
  TO DO
  Total users count
  Messages processedd count
  Most dominating emotion

*/
const Dashboard = () => {
  const theme = useTheme();
  const colors = tokens(theme.palette.mode);

  const [totalMessages, setTotalMessages] = useState(0);
  const [emotionLast1Day, setEmotionLast1Day] = useState(0);
  const [emotionLast7Day, setEmotionLast7Day] = useState(0);
  const [emotionLast30Day, setEmotionLast30Day] = useState(0);

  const isAnalyticsFetched = useRef({
    last1Day: false,
    last7Day: false,
    last30Day: false,
  });


  const { user } = useUser();
  useEffect(() => {
    const fetchTotalMessages = async () => {
      console.log("Trying to get user's {" + user.username + "} total message count");
      try {
        const response = await fetch(`http://127.0.0.1:5000/api/get_total_messages?username=${user.username}`);
        const data = await response.json();

        if (response.ok) {
          console.log("Fetched total message count: ", data);
          setTotalMessages(data.totalMessages); // Assuming you store this in state
        } else {
          console.error("Failed to fetch total message count: ", data);
        }
      } catch (error) {
        console.error("Error fetching total message count: ", error);
      }
    };
    fetchTotalMessages();
  }, [user.username]);

  useEffect(() => {
    const fetchAnalytics = async (days, setEmotionState, flagKey) => {
      if (isAnalyticsFetched.current[flagKey]) {
        return;
      }
    
      isAnalyticsFetched.current[flagKey] = true;  // Mark as fetched
      console.log(`Trying to get user's analytics for the last ${days} days`);
    
      try {
        const data = await getAnalyticsAPI(days);  // Fetch data using the API function
        console.log(`Fetched analytics for ${days} days: `, data);
        setEmotionState(data.most_common_emotion);  // Update state with the fetched emotion
      } catch (error) {
        console.error("Error fetching analytics:", error);
      }
    }
  
    fetchAnalytics(1, setEmotionLast1Day, 'last1Day');
    fetchAnalytics(7, setEmotionLast7Day, 'last7Day');
    fetchAnalytics(30, setEmotionLast30Day, 'last30Day');
  }, []);

  return (
    <Box m="20px">
      {/* HEADER */}
      <Box display="flex" justifyContent="space-between" alignItems="center">
        <Header title="DASHBOARD" subtitle="Welcome to your dashboard" />

        <Box>
          <Button
            sx={{
              backgroundColor: colors.blueAccent[700],
              color: colors.grey[100],
              fontSize: "14px",
              fontWeight: "bold",
              padding: "10px 20px",
            }}
          >
            <DownloadOutlinedIcon sx={{ mr: "10px" }} />
            Download Reports
          </Button>
        </Box>
      </Box>
      
      {/* GRID & CHARTS */}
      <Box
        display="grid"
        gridTemplateColumns="repeat(12, 1fr)"
        gridAutoRows="200px"
        gap="20px"
      >
        {/* ROW 1 */}
        <Box
          gridColumn="span 4"
          backgroundColor={colors.primary[400]}
          display="flex"
          alignItems="center"
          justifyContent="center"
        >
          {/* TODO: Display some useful information */}
          <StatBox
            title={emotionLast1Day}
            subtitle="Your most common emotion today"
            progress="0.75"
            increase="+14%"
            icon={
              <EmailIcon
                sx={{ color: colors.greenAccent[600], fontSize: "26px" }}
              />
            }
          />
        </Box>
        <Box
          gridColumn="span 4"
          backgroundColor={colors.primary[400]}
          display="flex"
          alignItems="center"
          justifyContent="center"
        >
          {/* TODO: Display some useful information */}
          <StatBox
            title={emotionLast7Day}
            subtitle="Your most common emotion last 7 days"
            progress="0.50"
            increase="+21%"
            icon={
              <PointOfSaleIcon
                sx={{ color: colors.greenAccent[600], fontSize: "26px" }}
              />
            }
          />
        </Box>
        <Box
          gridColumn="span 4"
          backgroundColor={colors.primary[400]}
          display="flex"
          alignItems="center"
          justifyContent="center"
        >
          {/* TODO: Display some useful information */}
          <StatBox
            title={emotionLast30Day}
            subtitle="Your most common emotion last 30 days"
            progress="0.30"
            increase="+5%"
            icon={
              <PersonAddIcon
                sx={{ color: colors.greenAccent[600], fontSize: "26px" }}
              />
            }
          />
        </Box>
        {/*
        <Box
          gridColumn="span 3"
          backgroundColor={colors.primary[400]}
          display="flex"
          alignItems="center"
          justifyContent="center"
        >
          <StatBox
            title="BOX 4.1"
            subtitle="BOX 4.2"
            progress="0.80"
            increase="+43%"
            icon={
              <TrafficIcon
                sx={{ color: colors.greenAccent[600], fontSize: "26px" }}
              />
            }
          />
        </Box>
        */}
        {/* ROW 2 */}
        <Box
          gridColumn="span 8"
          gridRow="span 2"
          backgroundColor={colors.primary[400]}
        >
          <Box
            mt="25px"
            p="0 30px"
            display="flex "
            justifyContent="space-between"
            alignItems="center"
          >
            <Box>
              <Typography
                variant="h5"
                fontWeight="600"
                color={colors.grey[100]}
              >
                Total messages
              </Typography>
              <Typography
                variant="h3"
                fontWeight="bold"
                color={colors.greenAccent[500]}
              >
                {totalMessages}
              </Typography>
            </Box>
            <Box>
              <IconButton>
                <DownloadOutlinedIcon
                  sx={{ fontSize: "26px", color: colors.greenAccent[500] }}
                />
              </IconButton>
            </Box>
          </Box>
          <Box height="250px" m="-20px 0 0 0">
            <LineChart isDashboard={true} />
          </Box>
        </Box>
        <Box
          gridColumn="span 4"
          gridRow="span 2"
          backgroundColor={colors.primary[400]}
          overflow="auto"
        >
          <Box
            display="flex"
            justifyContent="space-between"
            alignItems="center"
            borderBottom={`4px solid ${colors.primary[500]}`}
            colors={colors.grey[100]}
            p="15px"
          >
            <Typography color={colors.grey[100]} variant="h5" fontWeight="600">
              Emotion Pie Chart
            </Typography>
          </Box>
            <Box height="28vh">
             <PieChart />  {/* This will render the PieChart */}
            </Box>
          </Box>
        {/*
        <Box
          gridColumn="span 4"
          gridRow="span 2"
          backgroundColor={colors.primary[400]}
          p="30px"
        >
          <Typography variant="h5" fontWeight="600">
            Campaign
          </Typography>
          <Box
            display="flex"
            flexDirection="column"
            alignItems="center"
            mt="25px"
          >
            <ProgressCircle size="125" />
            <Typography
              variant="h5"
              color={colors.greenAccent[500]}
              sx={{ mt: "15px" }}
            >
              $48,352 revenue generated
            </Typography>
            <Typography>Includes extra misc expenditures and costs</Typography>
          </Box>
        </Box>
        <Box
          gridColumn="span 4"
          gridRow="span 2"
          backgroundColor={colors.primary[400]}
        >
          <Typography
            variant="h5"
            fontWeight="600"
            sx={{ padding: "30px 30px 0 30px" }}
          >
            Sales Quantity
          </Typography>
          <Box height="250px" mt="-20px">
            <BarChart isDashboard={true} />
          </Box>
        </Box>
        <Box
          gridColumn="span 4"
          gridRow="span 2"
          backgroundColor={colors.primary[400]}
          padding="30px"
        >
          <Typography
            variant="h5"
            fontWeight="600"
            sx={{ marginBottom: "15px" }}
          >
            Geography Based Traffic
          </Typography>
          <Box height="200px">
            <GeographyChart isDashboard={true} />
          </Box>
        </Box>
        */}
      </Box>
    </Box>
  );
};

export default Dashboard;
