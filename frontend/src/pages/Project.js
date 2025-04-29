import React from "react";
import { Link } from "react-router-dom";
import { Box, Typography, Paper, Grid, useTheme } from "@mui/material";
import { motion } from "framer-motion";

// 🔹 Карточка с анимацией
const MotionCard = ({ to, color, icon, label }) => (
  <Grid item xs={12} sm={6} md={4}>
    <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.98 }}>
      <Paper
        component={Link}
        to={to}
        elevation={5}
        sx={{
          textDecoration: "none",
          backgroundColor: color,
          p: 3,
          borderRadius: 4,
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          justifyContent: "center",
          height: "160px",
          color: "#fff",
          fontSize: "1.1rem",
          fontWeight: "bold",
          transition: "0.3s",
        }}
      >
        <Typography variant="h4" sx={{ mb: 1 }}>
          {icon}
        </Typography>
        {label}
      </Paper>
    </motion.div>
  </Grid>
);

const Project = () => {
  const theme = useTheme();

  return (
    <Box
      sx={{
        minHeight: "100vh",
        py: 6,
        px: 4,
        background: "linear-gradient(to right, #e1f5fe, #f3e5f5)",
        backgroundImage: "url(https://cdn.bim42.com/img/revit-bim.jpg)",
        backgroundSize: "cover",
        backgroundBlendMode: "overlay",
        backdropFilter: "blur(3px)",
      }}
    >
      <Box sx={{ backgroundColor: "rgba(255,255,255,0.85)", p: 4, borderRadius: 4 }}>
        <Typography
          variant="h3"
          align="center"
          fontWeight="bold"
          gutterBottom
          color={theme.palette.primary.main}
        >
          📁 Раздел "Project"
        </Typography>

        <Typography variant="h6" align="center" sx={{ mb: 4 }}>
          Здесь вы можете просматривать данные из моделей Revit, загруженные в BIM 360
        </Typography>

        <Grid container spacing={3} justifyContent="center">
          <MotionCard to="/project/map" color="#1976d2" icon="🗺" label="Карта проектов" />
          <MotionCard to="/project/projects" color="#2e7d32" icon="📋" label="Таблица проектов" />
          <MotionCard to="/project/guids" color="#f9a825" icon="📂" label="Таблица видов" />
          <MotionCard to="/project/elements" color="#6d4c41" icon="🧱" label="Таблица элементов" />
          <MotionCard to="/project/ai" color="#0288d1" icon="🤖" label="AI-ассистент" />
        </Grid>

        <Typography
          variant="body2"
          align="center"
          sx={{ mt: 6, color: "#666" }}
        >
          Управляйте данными, анализируйте модели, запускайте AI-ассистента и визуализируйте BIM-информацию прямо из облака.
        </Typography>
      </Box>
    </Box>
  );
};

export default Project;
