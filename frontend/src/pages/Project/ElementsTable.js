import React, { useEffect, useState } from "react";
import {
  Box, Typography, MenuItem, Select, FormControl,
  InputLabel, Table, TableHead, TableBody, TableRow, TableCell, Paper
} from "@mui/material";

const ElementsExplorer = () => {
  const [projects, setProjects] = useState([]);
  const [files, setFiles] = useState([]);
  const [versions, setVersions] = useState([]);
  const [views, setViews] = useState([]);
  const [elements, setElements] = useState([]);

  const [selectedProject, setSelectedProject] = useState("");
  const [selectedFile, setSelectedFile] = useState("");
  const [selectedVersion, setSelectedVersion] = useState("");
  const [selectedView, setSelectedView] = useState("");

  // Загрузка проектов
  useEffect(() => {
    fetch("http://localhost:8000/api/projects-list")
      .then(res => res.json())
      .then(setProjects);
  }, []);

  // Загрузка файлов по проекту
  useEffect(() => {
    if (!selectedProject) return;
    fetch(`http://localhost:8000/api/files-by-project?project=${selectedProject}`)
      .then(res => res.json())
      .then(setFiles);
  }, [selectedProject]);

  // Загрузка версий и видов
  useEffect(() => {
    if (!selectedProject || !selectedFile) return;
    fetch(`http://localhost:8000/api/views-3d?project=${selectedProject}&file_name=${selectedFile}`)
      .then(res => res.json())
      .then(data => {
        const uniqueVersions = [...new Set(data.map(v => v.version_number))];
        setVersions(uniqueVersions);
        setViews(data);
      });
  }, [selectedFile]);

  // Загрузка элементов по выбранному виду
  useEffect(() => {
    if (!selectedProject || !selectedFile || !selectedVersion || !selectedView) return;
    fetch(`http://localhost:8000/api/elements-by-view?project=${selectedProject}&file_name=${selectedFile}&version=${selectedVersion}&view_name=${selectedView}`)
      .then(res => res.json())
      .then(setElements);
  }, [selectedView]);

  return (
    <Box p={4}>
      <Typography variant="h5" gutterBottom>🧱 Элементы и параметры</Typography>

      <Box display="flex" gap={2} mb={3}>
        <FormControl sx={{ minWidth: 160 }}>
          <InputLabel>Проект</InputLabel>
          <Select value={selectedProject} label="Проект" onChange={e => {
            setSelectedProject(e.target.value);
            setSelectedFile("");
            setSelectedVersion("");
            setSelectedView("");
            setElements([]);
          }}>
            {projects.map(p => (
              <MenuItem key={p} value={p}>{p}</MenuItem>
            ))}
          </Select>
        </FormControl>

        <FormControl sx={{ minWidth: 160 }} disabled={!selectedProject}>
          <InputLabel>Файл</InputLabel>
          <Select value={selectedFile} label="Файл" onChange={e => {
            setSelectedFile(e.target.value);
            setSelectedVersion("");
            setSelectedView("");
            setElements([]);
          }}>
            {files.map(f => (
              <MenuItem key={f} value={f}>{f}</MenuItem>
            ))}
          </Select>
        </FormControl>

        <FormControl sx={{ minWidth: 120 }} disabled={!selectedFile}>
          <InputLabel>Версия</InputLabel>
          <Select value={selectedVersion} label="Версия" onChange={e => {
            setSelectedVersion(e.target.value);
            setSelectedView("");
            setElements([]);
          }}>
            {versions.map(v => (
              <MenuItem key={v} value={v}>{v}</MenuItem>
            ))}
          </Select>
        </FormControl>

        <FormControl sx={{ minWidth: 160 }} disabled={!selectedVersion}>
          <InputLabel>3D Вид</InputLabel>
          <Select value={selectedView} label="3D Вид" onChange={e => setSelectedView(e.target.value)}>
            {views.filter(v => v.version_number === selectedVersion).map((v, i) => (
              <MenuItem key={i} value={v.view_name}>{v.view_name}</MenuItem>
            ))}
          </Select>
        </FormControl>
      </Box>

      {elements.length > 0 && (
        <Paper elevation={4}>
          <Table size="small">
            <TableHead>
              <TableRow sx={{ backgroundColor: "#e0f7fa" }}>
                <TableCell>Object ID</TableCell>
                <TableCell>Название</TableCell>
                <TableCell>Параметры</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {elements.map((el, idx) => (
                <TableRow key={idx}>
                  <TableCell>{el.object_id}</TableCell>
                  <TableCell>{el.name}</TableCell>
                  <TableCell>
                    <pre style={{ whiteSpace: "pre-wrap", fontSize: "0.75em" }}>
                      {JSON.stringify(el.properties, null, 2)}
                    </pre>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </Paper>
      )}
    </Box>
  );
};

export default ElementsExplorer;
