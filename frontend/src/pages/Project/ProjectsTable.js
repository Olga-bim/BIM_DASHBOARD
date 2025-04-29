import React, { useEffect, useState } from "react";
import {
  Box,
  Typography,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Table,
  TableHead,
  TableBody,
  TableRow,
  TableCell,
  Paper,
  MenuItem,
  Select,
  InputLabel,
  FormControl,
} from "@mui/material";
import ExpandMoreIcon from "@mui/icons-material/ExpandMore";

export default function ProjectsTable() {
  const [data, setData] = useState([]);
  const [expandedProject, setExpandedProject] = useState(null);
  const [expandedFile, setExpandedFile] = useState({});
  const [selectedDiscipline, setSelectedDiscipline] = useState({});
  const [disciplines, setDisciplines] = useState({});

  useEffect(() => {
    fetch("http://localhost:8000/api/projects-table")
      .then(res => res.json())
      .then((raw) => {
        const grouped = {};
        const allDisciplines = {};
        raw.forEach(item => {
          if (!grouped[item.project]) grouped[item.project] = {};
          const disc = item.file_name.split("_")[1] || "Без дисциплины";
          if (!grouped[item.project][disc]) grouped[item.project][disc] = [];
          grouped[item.project][disc].push(item);

          if (!allDisciplines[item.project]) allDisciplines[item.project] = new Set();
          allDisciplines[item.project].add(disc);
        });

        // Convert Set to Array
        const discMap = {};
        for (let proj in allDisciplines) {
          discMap[proj] = Array.from(allDisciplines[proj]);
        }

        setData(grouped);
        setDisciplines(discMap);
      })
      .catch(err => console.error("Ошибка загрузки:", err));
  }, []);

  return (
    <Box sx={{ p: 4 }}>
      <Typography variant="h5" gutterBottom>
        📁 Проекты Revit — версии по дисциплинам
      </Typography>

      <Paper elevation={6}>
        {Object.keys(data).map((project) => (
          <Accordion
            key={project}
            expanded={expandedProject === project}
            onChange={() => setExpandedProject(expandedProject === project ? null : project)}
          >
            <AccordionSummary expandIcon={<ExpandMoreIcon />}>
              <Typography sx={{ fontWeight: "bold" }}>{project}</Typography>
            </AccordionSummary>
            <AccordionDetails>
              <FormControl fullWidth sx={{ mb: 2 }}>
              <InputLabel>Дисциплина</InputLabel>
            <Select
              value={selectedDiscipline[project] || ""}
              label="Дисциплина"
              onChange={(e) =>
                setSelectedDiscipline({ ...selectedDiscipline, [project]: e.target.value })
              }
            >
              {(disciplines[project] || []).map((disc, i) => (
                <MenuItem key={i} value={disc}>{disc}</MenuItem>
              ))}
            </Select>
          </FormControl>

          <Table size="small">
            <TableHead sx={{ backgroundColor: "#f0f0f0" }}>
              <TableRow>
                <TableCell>Файл</TableCell>
                <TableCell>Версия</TableCell>
                <TableCell>Изменено</TableCell>
                <TableCell>Кем</TableCell>
                <TableCell>Опубликовано</TableCell>
                <TableCell>Кем опубликовано</TableCell>
                <TableCell>Статус</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {(data[project][selectedDiscipline[project]] || []).map((item, idx) => (
                <TableRow key={idx}>
                  <TableCell>{item.file_name}</TableCell>
                  <TableCell>{item.version_number}</TableCell>
                  <TableCell>{item.last_modified_time}</TableCell>
                  <TableCell>{item.last_modified_user}</TableCell>
                  <TableCell>{item.published_time}</TableCell>
                  <TableCell>{item.published_user}</TableCell>
                  <TableCell>{item.process_state}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </AccordionDetails>
      </Accordion>
    ))}
  </Paper>
</Box>
  );
}
