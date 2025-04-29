import React, { useEffect, useState } from "react";
import {
  Box, Typography, Paper, Button, Table, TableHead, TableBody,
  TableCell, TableRow, Dialog, DialogTitle, DialogContent,
  TextField, MenuItem, DialogActions, Grid
} from "@mui/material";
import { MapContainer, TileLayer, Marker, Popup } from "react-leaflet";
import "leaflet/dist/leaflet.css";
import L from "leaflet";
import { CSSTransition, TransitionGroup } from "react-transition-group";
import "../../styles/alerts.css";

const customIcon = new L.Icon({
  iconUrl: "/assets/marker-3d.png",
  iconSize: [40, 40],
  iconAnchor: [20, 40],
  popupAnchor: [0, -40],
});

export default function MapPage() {
  const [points, setPoints] = useState([]);
  const [cityMap, setCityMap] = useState({});
  const [selectedProject, setSelectedProject] = useState(null);
  const [designers, setDesigners] = useState([]);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [isEditing, setIsEditing] = useState(false);
  const [editId, setEditId] = useState(null);
  const [newDesigner, setNewDesigner] = useState(initDesigner());
  const [customDiscipline, setCustomDiscipline] = useState("");
  const [toast, setToast] = useState("");

  const [emailDialogOpen, setEmailDialogOpen] = useState(false);
  const [selectedRecipients, setSelectedRecipients] = useState([]);
  const [senderEmail, setSenderEmail] = useState("");

  const disciplines = [
    "Архитектура", "Конструкция", "Инсталляция",
    "Кондиционирование", "Электрика", "Пневматика", "Спринклеры", "Другое"
  ];

  const [filterDiscipline, setFilterDiscipline] = useState("");
  const [filterCompany, setFilterCompany] = useState("");
  const [filterPosition, setFilterPosition] = useState("");

  function initDesigner() {
    return {
      discipline: "",
      first_name: "",
      last_name: "",
      company: "",
      email: "",
      phone: "",
      position: ""
    };
  }

  const showToast = (msg) => {
    setToast(msg);
    setTimeout(() => setToast(""), 3000);
  };

  useEffect(() => {
    fetch("http://localhost:8000/api/coordinates")
      .then(res => res.json())
      .then(async (data) => {
        setPoints(data);
        const cities = {};
        for (const p of data) {
          const key = `${p.latitude}_${p.longitude}`;
          if (!cities[key]) {
            const city = await fetchCityFromCoords(p.latitude, p.longitude);
            cities[key] = city;
          }
        }
        setCityMap(cities);
      });
  }, []);

  const fetchCityFromCoords = async (lat, lon) => {
    try {
      const res = await fetch(`https://nominatim.openstreetmap.org/reverse?format=jsonv2&lat=${lat}&lon=${lon}`, {
        headers: { "User-Agent": "Revit-Map-App/1.0" }
      });
      const data = await res.json();
      return data.address.city || data.address.town || data.address.village || "Неизвестно";
    } catch {
      return "Неизвестно";
    }
  };

  const fetchDesigners = (projectName) => {
    fetch(`http://localhost:8000/api/designers?project=${projectName}`)
      .then(res => res.json())
      .then(data => {
        setSelectedProject(projectName);
        setDesigners(data);
      });
  };

  const handleOpenDialog = (designer = null) => {
    if (designer) {
      setNewDesigner(designer);
      setIsEditing(true);
      setEditId(designer.id);
      if (!disciplines.includes(designer.discipline)) {
        setCustomDiscipline(designer.discipline);
        setNewDesigner(d => ({ ...d, discipline: "Другое" }));
      }
    } else {
      setNewDesigner(initDesigner());
      setIsEditing(false);
      setEditId(null);
      setCustomDiscipline("");
    }
    setDialogOpen(true);
  };

  const handleSave = () => {
    const discipline = newDesigner.discipline === "Другое" ? customDiscipline : newDesigner.discipline;
    if (!newDesigner.email.includes("@")) return showToast("❌ Некорректный email");
    if (newDesigner.phone.length < 7) return showToast("❌ Некорректный телефон");

    const payload = { ...newDesigner, project_name: selectedProject, discipline };

    const url = isEditing
      ? `http://localhost:8000/api/designers/${selectedProject}/${editId}`
      : "http://localhost:8000/api/designers";
    const method = isEditing ? "PUT" : "POST";

    fetch(url, {
      method,
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    })
      .then(() => {
        setDialogOpen(false);
        fetchDesigners(selectedProject);
        showToast(isEditing ? "✅ Обновлено" : "✅ Добавлено");
      });
  };

  const handleDelete = (id) => {
    if (!window.confirm("Удалить проектировщика?")) return;
    fetch(`http://localhost:8000/api/designers/${selectedProject}/${id}`, {
      method: "DELETE"
    }).then(() => {
      fetchDesigners(selectedProject);
      showToast("🗑️ Удалено");
    });
  };

  const resetFilters = () => {
    setFilterDiscipline("");
    setFilterCompany("");
    setFilterPosition("");
  };

  const filteredDesigners = designers.filter(d =>
    (!filterDiscipline || d.discipline === filterDiscipline) &&
    (!filterCompany || d.company.toLowerCase().includes(filterCompany.toLowerCase())) &&
    (!filterPosition || d.position.toLowerCase().includes(filterPosition.toLowerCase()))
  );

  const sendEmail = () => {
    if (!senderEmail) {
      alert("Введите ваш email.");
      return;
    }
    if (selectedRecipients.length === 0) {
      alert("Выберите хотя бы одного получателя.");
      return;
    }
    const to = selectedRecipients.join(";");
    const subject = `Проект ${selectedProject}`;
    const body = `Отправитель: ${senderEmail}\n\nСообщение по проекту ${selectedProject}`;

    window.location.href = `mailto:${to}?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(body)}`;
    setEmailDialogOpen(false);
  };

  return (
    <Box sx={{ p: 4 }}>
      <Typography variant="h4" align="center" gutterBottom>🌍 Карта проектов</Typography>

      <Paper elevation={6} sx={{ borderRadius: 3, overflow: "hidden", mb: 4 }}>
        <MapContainer center={[31.5, 34.9]} zoom={8} style={{ height: "500px", width: "100%" }}>
          <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
          {points.map((p, i) => {
            const key = `${p.latitude}_${p.longitude}`;
            const city = cityMap[key] || "Определение...";
            return (
              <Marker key={i} position={[p.latitude, p.longitude]} icon={customIcon}
                eventHandlers={{ click: () => fetchDesigners(p.project) }}>
                <Popup>
                  <strong>{p.project}</strong><br />
                  <b>Город:</b> {city}<br />
                  {p.latitude.toFixed(5)}, {p.longitude.toFixed(5)}<br />
                  Высота: {p.elevation}<br />
                  Угол: {p.angle}
                </Popup>
              </Marker>
            );
          })}
        </MapContainer>
      </Paper>

      {selectedProject && (
        <Box>
          <Typography variant="h6" gutterBottom>👷 Проектировщики проекта: {selectedProject}</Typography>

          <Grid container spacing={2} mb={2}>
            {/* Фильтры */}
            <Grid item xs={12} md={4}>
              <TextField
                select label="Фильтр: дисциплина"
                value={filterDiscipline}
                onChange={(e) => setFilterDiscipline(e.target.value)}
                fullWidth
                sx={{ minWidth: 300 }}
              >
                <MenuItem value="">Все</MenuItem>
                {Array.from(new Set(designers.map(d => d.discipline))).map((discipline, i) => (
                  <MenuItem key={i} value={discipline}>{discipline}</MenuItem>
                ))}
              </TextField>
            </Grid>
            <Grid item xs={12} md={4}>
              <TextField
                select label="Фильтр: фирма"
                value={filterCompany}
                onChange={(e) => setFilterCompany(e.target.value)}
                fullWidth
                sx={{ minWidth: 300 }}
              >
                <MenuItem value="">Все</MenuItem>
                {Array.from(new Set(designers.map(d => d.company))).map((company, i) => (
                  <MenuItem key={i} value={company}>{company}</MenuItem>
                ))}
              </TextField>
            </Grid>
            <Grid item xs={12} md={4}>
              <TextField
                select label="Фильтр: должность"
                value={filterPosition}
                onChange={(e) => setFilterPosition(e.target.value)}
                fullWidth
                sx={{ minWidth: 300 }}
              >
                <MenuItem value="">Все</MenuItem>
                {Array.from(new Set(designers.map(d => d.position))).map((position, i) => (
                  <MenuItem key={i} value={position}>{position}</MenuItem>
                ))}
              </TextField>
            </Grid>
            <Grid item xs={12}>
              <Button variant="outlined" onClick={resetFilters} fullWidth>Сбросить фильтры</Button>
            </Grid>
          </Grid>

          {/* Таблица проектировщиков */}
          <Table>
            <TableHead>
              <TableRow sx={{ backgroundColor: "#e0e0e0" }}>
                <TableCell>Имя</TableCell>
                <TableCell>Фамилия</TableCell>
                <TableCell>Фирма</TableCell>
                <TableCell>Дисциплина</TableCell>
                <TableCell>Email</TableCell>
                <TableCell>Телефон</TableCell>
                <TableCell>Должность</TableCell>
                <TableCell>Действия</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {filteredDesigners.map((d, i) => (
                <TableRow key={i}>
                  <TableCell>{d.first_name}</TableCell>
                  <TableCell>{d.last_name}</TableCell>
                  <TableCell>{d.company}</TableCell>
                  <TableCell>{d.discipline}</TableCell>
                  <TableCell>{d.email}</TableCell>
                  <TableCell>{d.phone}</TableCell>
                  <TableCell>{d.position}</TableCell>
                  <TableCell>
                    <Button size="small" onClick={() => handleOpenDialog(d)}>✏️</Button>
                    <Button size="small" onClick={() => handleDelete(d.id)}>🗑️</Button>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>

          {/* Кнопки */}
          <Box mt={2} display="flex" gap={2}>
            <Button variant="contained" onClick={() => handleOpenDialog()}>
              ➕ Добавить проектировщика
            </Button>
            {designers.length > 0 && (
              <Button variant="outlined" onClick={() => setEmailDialogOpen(true)}>
                ✉️ Написать email
              </Button>
            )}
          </Box>
        </Box>
      )}

      {/* Диалог добавления/редактирования проектировщика */}
      <Dialog open={dialogOpen} onClose={() => setDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>{isEditing ? "Редактировать" : "Добавить"} проектировщика</DialogTitle>
        <DialogContent sx={{ display: "flex", flexDirection: "column", gap: 2, mt: 1 }}>
  {/* Выбор дисциплины */}
  <TextField
    select
    label="Дисциплина"
    value={newDesigner.discipline}
    onChange={(e) => setNewDesigner(prev => ({ ...prev, discipline: e.target.value }))}
    fullWidth
  >
    {disciplines.map((d, i) => (
      <MenuItem key={i} value={d}>{d}</MenuItem>
    ))}
  </TextField>

  {/* Если выбрано "Другое" — отдельное поле для ввода своей дисциплины */}
  {newDesigner.discipline === "Другое" && (
    <TextField
      label="Введите свою дисциплину"
      value={customDiscipline}
      onChange={(e) => setCustomDiscipline(e.target.value)}
      fullWidth
    />
  )}

  {/* Остальные поля формы */}
  <TextField
    label="Имя"
    value={newDesigner.first_name}
    onChange={(e) => setNewDesigner(prev => ({ ...prev, first_name: e.target.value }))}
    fullWidth
  />
  <TextField
    label="Фамилия"
    value={newDesigner.last_name}
    onChange={(e) => setNewDesigner(prev => ({ ...prev, last_name: e.target.value }))}
    fullWidth
  />
  <TextField
    label="Фирма"
    value={newDesigner.company}
    onChange={(e) => setNewDesigner(prev => ({ ...prev, company: e.target.value }))}
    fullWidth
  />
  <TextField
    label="Email"
    value={newDesigner.email}
    onChange={(e) => setNewDesigner(prev => ({ ...prev, email: e.target.value }))}
    fullWidth
  />
  <TextField
    label="Телефон"
    value={newDesigner.phone}
    onChange={(e) => setNewDesigner(prev => ({ ...prev, phone: e.target.value }))}
    fullWidth
  />
  <TextField
    label="Должность"
    value={newDesigner.position}
    onChange={(e) => setNewDesigner(prev => ({ ...prev, position: e.target.value }))}
    fullWidth
  />
</DialogContent>

        <DialogActions>
          <Button onClick={() => setDialogOpen(false)}>Отмена</Button>
          <Button variant="contained" onClick={handleSave}>💾 Сохранить</Button>
        </DialogActions>
      </Dialog>

      {/* Диалог отправки Email */}
      <Dialog open={emailDialogOpen} onClose={() => setEmailDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>✉️ Отправить письмо проектировщикам</DialogTitle>
        <DialogContent sx={{ display: "flex", flexDirection: "column", gap: 2, mt: 1 }}>
          <TextField label="Ваш Email" value={senderEmail} onChange={(e) => setSenderEmail(e.target.value)} />
          <Typography variant="h6" sx={{ mt: 2 }}>Получатели:</Typography>
          {designers.map((designer, i) => (
            <Box key={i} display="flex" alignItems="center" mb={1}>
              <input type="checkbox" checked={selectedRecipients.includes(designer.email)}
                onChange={(e) => {
                  const checked = e.target.checked;
                  setSelectedRecipients(prev => checked ? [...prev, designer.email] : prev.filter(mail => mail !== designer.email));
                }} style={{ marginRight: 8 }} />
              {designer.first_name} {designer.last_name} ({designer.email})
            </Box>
          ))}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setEmailDialogOpen(false)}>Отмена</Button>
          <Button variant="contained" onClick={sendEmail}>📨 Отправить</Button>
        </DialogActions>
      </Dialog>

      {/* Всплывающее уведомление */}
      <TransitionGroup>
        {toast && (
          <CSSTransition timeout={300} classNames="fade" key="toast">
            <div className="toast alert alert-success position-fixed bottom-0 end-0 m-4">
              {toast}
            </div>
          </CSSTransition>
        )}
      </TransitionGroup>
    </Box>
  );
}
