import React, { useState, useRef } from "react";
import {
  Typography,
  Container,
  Button,
  Stack,
  TextField,
  Divider,
  Paper,
  IconButton,
  Slide,
  Box,
} from "@mui/material";
import SchoolIcon from "@mui/icons-material/School";
import BusinessIcon from "@mui/icons-material/Business";
import AddCircleOutlineIcon from "@mui/icons-material/AddCircleOutline";
import DeleteIcon from "@mui/icons-material/Delete";
import html2pdf from "html2pdf.js";
import "bootstrap/dist/css/bootstrap.min.css";

const About = () => {
  const resumeRef = useRef();

  const [formData, setFormData] = useState({
    name: "",
    email: "",
    phone: "",
    city: "",
  });

  const [educationList, setEducationList] = useState([""]);
  const [skillsList, setSkillsList] = useState([""]);
  const [langsList, setLangsList] = useState([""]);
  const [projectsList, setProjectsList] = useState([""]);

  const handleChange = (e) => {
    setFormData((prev) => ({ ...prev, [e.target.name]: e.target.value }));
  };

  const handleSavePdf = () => {
    const element = resumeRef.current;
  
    const today = new Date();
    const formattedDate = today.toLocaleDateString('ru-RU').split('.').join('-'); // Формат: 26-04-2025
  
    let fileName = "resume.pdf"; // на всякий случай дефолтное имя
  
    if (formData.name) {
      const parts = formData.name.trim().split(' '); // Разбиваем имя по пробелу
      if (parts.length >= 2) {
        const [lastName, firstName] = parts; // Предполагаем "Фамилия Имя"
        fileName = `${lastName}_${firstName}_${formattedDate}.pdf`;
      } else {
        fileName = `${parts[0]}_${formattedDate}.pdf`; // Если только одно слово
      }
    } else {
      fileName = `resume_${formattedDate}.pdf`; // Если имя не заполнено
    }
  
    html2pdf()
      .from(element)
      .set({ filename: fileName })
      .save();
  };
  

  const handleListChange = (setter, index, value, list) => {
    const updated = [...list];
    updated[index] = value;
    setter(updated);
  };

  const addItem = (setter, list) => setter([...list, ""]);
  const removeItem = (setter, list, index) => {
    const updated = [...list];
    updated.splice(index, 1);
    setter(updated);
  };

  return (
    <Container maxWidth="md" sx={{ py: 4, background: "linear-gradient(to bottom, #f3e5f5, #e1f5fe)", borderRadius: 4 }}>
      <Typography variant="h4" gutterBottom fontWeight="bold" align="center">
        🧑‍💻 Резюме: AI-разработчик
      </Typography>

      <Stack spacing={2} direction="column" alignItems="center" sx={{ mb: 3 }}>
        <Button
          variant="outlined"
          color="primary"
          startIcon={<SchoolIcon />}
          href="https://www.johnbryce.co.il/"
          target="_blank"
        >
          Колледж, где я училась
        </Button>
        <Button
          variant="outlined"
          color="secondary"
          startIcon={<BusinessIcon />}
          href="https://www.wxg.co.il/"
          target="_blank"
        >
          Место работы
        </Button>
      </Stack>

      <Divider sx={{ mb: 3 }} />

      <Typography variant="h5" gutterBottom>📝 Заполните информацию</Typography>
      <Stack spacing={2} sx={{ mb: 4 }}>
        <TextField name="name" label="Имя" value={formData.name} onChange={handleChange} fullWidth />
        <TextField name="email" label="Email" value={formData.email} onChange={handleChange} fullWidth />
        <TextField name="phone" label="Телефон" value={formData.phone} onChange={handleChange} fullWidth />
        <TextField name="city" label="Город" value={formData.city} onChange={handleChange} fullWidth />
      </Stack>

      {[
        { label: "Образование", list: educationList, setter: setEducationList },
        { label: "Навыки", list: skillsList, setter: setSkillsList },
        { label: "Языки", list: langsList, setter: setLangsList },
        { label: "Проекты", list: projectsList, setter: setProjectsList },
      ].map(({ label, list, setter }, sectionIndex) => (
        <Box key={label} sx={{ mb: 4 }}>
          <Typography variant="h6" gutterBottom>{label}</Typography>
          {list.map((item, index) => (
            <Slide in direction="up" key={index}>
              <Stack direction="row" spacing={1} alignItems="center" sx={{ mb: 1 }}>
                <TextField
                  value={item}
                  onChange={(e) => handleListChange(setter, index, e.target.value, list)}
                  fullWidth
                  placeholder={`${label} ${index + 1}`}
                />
                <IconButton onClick={() => removeItem(setter, list, index)}>
                  <DeleteIcon color="error" />
                </IconButton>
              </Stack>
            </Slide>
          ))}
          <Button
            variant="text"
            startIcon={<AddCircleOutlineIcon />}
            onClick={() => addItem(setter, list)}
          >
            Добавить {label.toLowerCase()}
          </Button>
        </Box>
      ))}

      <Divider sx={{ my: 4 }} />
      <Typography variant="h5" gutterBottom>📄 Предпросмотр</Typography>

      <Paper elevation={3} ref={resumeRef} sx={{ p: 3, backgroundColor: "#fafafa", borderRadius: 3 }}>
        <Typography variant="h6">{formData.name}</Typography>
        <Typography>Email: {formData.email}</Typography>
        <Typography>Телефон: {formData.phone}</Typography>
        <Typography>Город: {formData.city}</Typography>

        <br />
        <Typography fontWeight="bold">🎓 Образование:</Typography>
        <ul>{educationList.map((edu, i) => edu && <li key={i}>{edu}</li>)}</ul>

        <Typography fontWeight="bold">🛠 Навыки:</Typography>
        <ul>{skillsList.map((skill, i) => skill && <li key={i}>{skill}</li>)}</ul>

        <Typography fontWeight="bold">🌐 Языки:</Typography>
        <ul>{langsList.map((lang, i) => lang && <li key={i}>{lang}</li>)}</ul>

        <Typography fontWeight="bold">📁 Проекты:</Typography>
        <ul>{projectsList.map((proj, i) => proj && <li key={i}>{proj}</li>)}</ul>
      </Paper>

      <Button variant="contained" color="success" className="mt-4" onClick={handleSavePdf}>
        💾 Сохранить как PDF
      </Button>
    </Container>
  );
};

export default About;
