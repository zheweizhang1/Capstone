import { Box, IconButton, useTheme, Menu, MenuItem } from "@mui/material";
import { useState, useContext } from "react";
import { useNavigate } from "react-router-dom"; // For navigation
import { ColorModeContext, tokens } from "../../theme";
import InputBase from "@mui/material/InputBase";
import LightModeOutlinedIcon from "@mui/icons-material/LightModeOutlined";
import DarkModeOutlinedIcon from "@mui/icons-material/DarkModeOutlined";
import NotificationsOutlinedIcon from "@mui/icons-material/NotificationsOutlined";
import SettingsOutlinedIcon from "@mui/icons-material/SettingsOutlined";
import PersonOutlinedIcon from "@mui/icons-material/PersonOutlined";
import SearchIcon from "@mui/icons-material/Search";

import { logoutAPI } from '../../api';

const Topbar = () => {
  const theme = useTheme();
  const colors = tokens(theme.palette.mode);
  const colorMode = useContext(ColorModeContext);
  const navigate = useNavigate(); // For navigation

  // State for managing the dropdown
  const [anchorEl, setAnchorEl] = useState(null);

  // Open the dropdown menu
  const handleMenuOpen = (event) => {
    setAnchorEl(event.currentTarget);
  };

  // Close the dropdown menu
  const handleMenuClose = () => {
    setAnchorEl(null);
  };

  // Handle logout
  const handleLogout = async (e) => {
    e.preventDefault();
    const response = await logoutAPI();
    console.log('Response:', response);

    handleMenuClose(); // Close the menu before redirecting
    navigate("/"); // Redirect to home
  };

  return (
    <Box display="flex" justifyContent="space-between" p={2}>
      {/* SEARCH BAR */}
      <Box
        display="flex"
        backgroundColor={colors.primary[400]}
        borderRadius="3px"
      >
        <InputBase sx={{ ml: 2, flex: 1 }} placeholder="Search" />
        <IconButton type="button" sx={{ p: 1 }}>
          <SearchIcon />
        </IconButton>
      </Box>

      {/* ICONS */}
      <Box display="flex">
        <IconButton onClick={colorMode.toggleColorMode}>
          {theme.palette.mode === "dark" ? (
            <DarkModeOutlinedIcon />
          ) : (
            <LightModeOutlinedIcon />
          )}
        </IconButton>
        <IconButton>
          <NotificationsOutlinedIcon />
        </IconButton>
        <IconButton>
          <SettingsOutlinedIcon />
        </IconButton>
        <IconButton onClick={handleMenuOpen}>
          <PersonOutlinedIcon />
        </IconButton>
        {/* Dropdown menu for the profile icon */}
        <Menu
          anchorEl={anchorEl}
          open={Boolean(anchorEl)}
          onClose={handleMenuClose}
        >
          <MenuItem onClick={handleLogout}>Logout</MenuItem>
        </Menu>
      </Box>
    </Box>
  );
};

export default Topbar;
