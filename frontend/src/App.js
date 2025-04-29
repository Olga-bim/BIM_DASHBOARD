import React, { useEffect } from "react";
import { BrowserRouter as Router, Routes, Route, Link } from "react-router-dom";
import Home from "./pages/Home";
import About from "./pages/About";
import Project from "./pages/Project";
import MapPage from "./pages/Project/Map";
import ProjectsTable from "./pages/Project/ProjectsTable";
import GuidsTable from "./pages/Project/GuidsTable";
import ElementsTable from "./pages/Project/ElementsTable";
import AiAssistant from "./pages/Project/AiAssistant";

import { AppBar, Toolbar, Typography, Box, Button } from "@mui/material";
import { motion } from "framer-motion";
import { FaHome, FaUserAlt, FaProjectDiagram } from "react-icons/fa";
import "./App.css"; // стили

function App() {
  useEffect(() => {
    const interval = setInterval(() => {
      const select = document.querySelector(".goog-te-combo");
      if (select && !document.getElementById("custom-lang-buttons")) {
        const container = document.createElement("div");
        container.id = "custom-lang-buttons";
        container.className = "lang-buttons text-center";
        container.innerHTML = `
          <button class='btn btn-sm btn-outline-dark mx-2' onclick="document.querySelector('.goog-te-combo').value='';document.querySelector('.goog-te-combo').dispatchEvent(new Event('change'));">🌐</button>
          <button class='btn btn-sm btn-outline-dark mx-2' onclick="document.querySelector('.goog-te-combo').value='en';document.querySelector('.goog-te-combo').dispatchEvent(new Event('change'));">EN</button>
          <button class='btn btn-sm btn-outline-dark mx-2' onclick="document.querySelector('.goog-te-combo').value='he';document.querySelector('.goog-te-combo').dispatchEvent(new Event('change'));">HE</button>
        `;
        const parent = document.getElementById("google_translate_element");
        if (parent) parent.appendChild(container);
      }
    }, 1000);
    return () => clearInterval(interval);
  }, []);

  return (
    <Router>
      {/* 🔹 Новый AppBar */}
      <AppBar position="sticky" sx={{ bgcolor: "#ffffff", boxShadow: "0 2px 6px rgba(0,0,0,0.05)" }}>
        <Toolbar sx={{ display: "flex", justifyContent: "space-between" }}>
        <Box sx={{ display: "flex", alignItems: "center", gap: 3 }}>
          <Typography
            component={Link}
            to="/"
            variant="h6"
            sx={{
              color: "#1976d2",
              textDecoration: "none",
              fontWeight: "bold",
              fontFamily: "monospace",
            }}
          >
            BIM Dashboard
          </Typography>

          <motion.div whileHover={{ scale: 1.05 }}>
            <Button component={Link} to="/" color="inherit" startIcon={<FaHome size={16} />}>
              Home
            </Button>
          </motion.div>

          <motion.div whileHover={{ scale: 1.05 }}>
            <Button component={Link} to="/about" color="inherit" startIcon={<FaUserAlt size={16} />}>
              About
            </Button>
          </motion.div>

          <motion.div whileHover={{ scale: 1.05 }}>
            <Button component={Link} to="/project" color="inherit" startIcon={<FaProjectDiagram size={16} />}>
              Project
            </Button>
          </motion.div>

          
        </Box>

          <div id="google_translate_element" />
        </Toolbar>
      </AppBar>

      {/* 🔹 Основной контент */}
      <Box sx={{ px: 3, pt: 5 }}>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/about" element={<About />} />
          <Route path="/project" element={<Project />} />
          <Route path="/project/map" element={<MapPage />} />
          <Route path="/project/projects" element={<ProjectsTable />} />
          <Route path="/project/guids" element={<GuidsTable />} />
          <Route path="/project/elements" element={<ElementsTable />} />
          <Route path="/project/ai" element={<AiAssistant />} />
        

        </Routes>
      </Box>
    </Router>
  );
}

export default App;
