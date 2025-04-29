import React, { useState, useEffect, useRef } from "react";
import { Box, Typography, Paper, TextField, Button, IconButton, Tooltip, Table, TableHead, TableRow, TableCell, TableBody } from "@mui/material";
import { FaChevronDown, FaChevronRight } from "react-icons/fa";
import { motion, AnimatePresence } from "framer-motion";
import { Link } from "react-router-dom";
import html2pdf from "html2pdf.js";

const bimSections = [
  {
    title: "📁 BIM 360 / ACC: Получение данных из моделей",
    content: (
      <>
        Используются <strong>Workshared Cloud Models</strong>, сохранённые через Revit ➔ "Save to Cloud".  
        Данные можно получить через API без дополнительной оплаты:
        <ul>
          <li>📄 Метаданные о видах: <code>/metadata</code></li>
          <li>📄 Параметры элементов: <code>/metadata/{"{guid}"}/properties</code></li>
          <li>📄 Структура элементов: <code>/metadata/{"{guid}"}</code></li>
        </ul>
        <strong>Важно:</strong> публикация должна быть сделана через <em>Publish Latest</em> в Revit.
      </>
    ),
    backgroundColor: "#e3f2fd",
  },
  {
    title: "🧩 BIM 360 / ACC: Активности и публикации",
    content: (
      <>
        Используется API <strong>Activity Stream</strong>:
        <ul>
          <li>✅ Публикация через Revit ➔ корректная активность и статусы в API</li>
          <li>⚠️ Публикация через Docs ➔ только фиксация файла без активности</li>
        </ul>
      </>
    ),
    backgroundColor: "#e8f5e9",
  },
  {
    title: "📑 Расшифровка координат из PDF",
    content: (
      <>
        При распознавании координат возникли сложности:
        <ul>
          <li>🌍 Разные системы координат в разных странах</li>
          <li>🧠 Автоматическое определение формата координат</li>
          <li>🏙️ Автоматическое определение города проекта для карты</li>
        </ul>
      </>
    ),
    backgroundColor: "#fff3e0",
  },
  {
    title: "🚀 Развитие проекта",
    content: (
      <>
        <strong>Версия 1:</strong> Изучение работы APS и получение данных.<br />
        <strong>Версия 2:</strong> Разработка backend (FastAPI) и frontend (React), создание базы данных.<br />
        <strong>Версия 3:</strong> Чат-бот для анализа BIM проектов, планирование AI на PyTorch.
      </>
    ),
    backgroundColor: "#ede7f6",
  },
];

const fullstackSection = {
  title: "💻 Fullstack Проект: сайт и база данных",
  content: (
    <>
      <Typography variant="h6" gutterBottom>🔹 Технологии:</Typography>
      <ul>
        <li>Backend: <strong>FastAPI</strong> + <strong>SQLite</strong></li>
        <li>Frontend: <strong>React.js</strong> + <strong>Material UI</strong> + <strong>Framer Motion</strong></li>
        <li>PDF-резюме: <Link to="/about">Страница "Обо мне"</Link> (создание резюме в PDF)</li>
        <li>Интеграция: Autodesk Platform Services (APS)</li>
      </ul>

      <Typography variant="h6" gutterBottom sx={{ mt: 3 }}>🔹 Страницы сайта:</Typography>
      <ul>
        <li><Link to="/">🏠 Главная страница (Home)</Link> — описание проекта и новые идеи</li>
        <li><Link to="/about">🙋 Страница "Обо мне"</Link> — создание и скачивание PDF-резюме</li>
        <li><Link to="/project/map">🗺️ Карта проектов</Link> — карта координат и проектировщиков</li>
        <li><Link to="/project/projects-table">📂 Файлы и версии Revit</Link> — таблица файлов моделей</li>
        <li><Link to="/project/elements-table">📑 Элементы и параметры</Link> — таблица структуры моделей</li>
        <li><Link to="/project/ai-assistant">🤖 AI-ассистент</Link> — чат для анализа проектов</li>
      </ul>
    </>
  ),
  backgroundColor: "#f1f8e9",
};

const databaseTablesSection = {
  title: "🗺️ Структура таблиц базы данных",
  content: (
    <Box sx={{ mt: 2 }}>
      <Typography variant="h6" gutterBottom>🔹 Таблица rvt_files</Typography>
      <Table size="small">
        <TableHead>
          <TableRow>
            <TableCell>Поле</TableCell>
            <TableCell>Тип</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          <TableRow><TableCell>id</TableCell><TableCell>INTEGER (PK)</TableCell></TableRow>
          <TableRow><TableCell>project_id</TableCell><TableCell>TEXT</TableCell></TableRow>
          <TableRow><TableCell>file_name</TableCell><TableCell>TEXT</TableCell></TableRow>
          <TableRow><TableCell>file_id</TableCell><TableCell>TEXT</TableCell></TableRow>
          <TableRow><TableCell>version_number</TableCell><TableCell>INTEGER</TableCell></TableRow>
          <TableRow><TableCell>version_id</TableCell><TableCell>TEXT</TableCell></TableRow>
          <TableRow><TableCell>urn</TableCell><TableCell>TEXT</TableCell></TableRow>
          <TableRow><TableCell>last_modified_time</TableCell><TableCell>TEXT</TableCell></TableRow>
          <TableRow><TableCell>last_modified_user</TableCell><TableCell>TEXT</TableCell></TableRow>
          <TableRow><TableCell>published_time</TableCell><TableCell>TEXT</TableCell></TableRow>
          <TableRow><TableCell>published_user</TableCell><TableCell>TEXT</TableCell></TableRow>
          <TableRow><TableCell>process_state</TableCell><TableCell>TEXT</TableCell></TableRow>
        </TableBody>
      </Table>

      <Typography variant="h6" gutterBottom sx={{ mt: 4 }}>🔹 Таблица views</Typography>
      <Table size="small">
        <TableHead>
          <TableRow>
            <TableCell>Поле</TableCell>
            <TableCell>Тип</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          <TableRow><TableCell>id</TableCell><TableCell>INTEGER (PK)</TableCell></TableRow>
          <TableRow><TableCell>view_key</TableCell><TableCell>TEXT</TableCell></TableRow>
          <TableRow><TableCell>project_name</TableCell><TableCell>TEXT</TableCell></TableRow>
          <TableRow><TableCell>file_name</TableCell><TableCell>TEXT</TableCell></TableRow>
          <TableRow><TableCell>version_number</TableCell><TableCell>INTEGER</TableCell></TableRow>
          <TableRow><TableCell>view_name</TableCell><TableCell>TEXT</TableCell></TableRow>
          <TableRow><TableCell>guid</TableCell><TableCell>TEXT</TableCell></TableRow>
        </TableBody>
      </Table>

      <Typography variant="h6" gutterBottom sx={{ mt: 4 }}>🔹 Таблица elements</Typography>
      <Table size="small">
        <TableHead>
          <TableRow>
            <TableCell>Поле</TableCell>
            <TableCell>Тип</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          <TableRow><TableCell>id</TableCell><TableCell>INTEGER (PK)</TableCell></TableRow>
          <TableRow><TableCell>view_id</TableCell><TableCell>INTEGER (FK → views.id)</TableCell></TableRow>
          <TableRow><TableCell>object_id</TableCell><TableCell>INTEGER</TableCell></TableRow>
          <TableRow><TableCell>name</TableCell><TableCell>TEXT</TableCell></TableRow>
          <TableRow><TableCell>raw_json</TableCell><TableCell>TEXT</TableCell></TableRow>
        </TableBody>
      </Table>

      <Typography variant="h6" gutterBottom sx={{ mt: 4 }}>🔹 Таблица properties</Typography>
      <Table size="small">
        <TableHead>
          <TableRow>
            <TableCell>Поле</TableCell>
            <TableCell>Тип</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          <TableRow><TableCell>id</TableCell><TableCell>INTEGER (PK)</TableCell></TableRow>
          <TableRow><TableCell>view_id</TableCell><TableCell>INTEGER (FK → views.id)</TableCell></TableRow>
          <TableRow><TableCell>object_id</TableCell><TableCell>INTEGER</TableCell></TableRow>
          <TableRow><TableCell>raw_json</TableCell><TableCell>TEXT</TableCell></TableRow>
        </TableBody>
      </Table>

      <Typography variant="h6" gutterBottom sx={{ mt: 4 }}>🔹 Таблица project_coordinates</Typography>
      <Table size="small">
        <TableHead>
          <TableRow>
            <TableCell>Поле</TableCell>
            <TableCell>Тип</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          <TableRow><TableCell>id</TableCell><TableCell>INTEGER (PK)</TableCell></TableRow>
          <TableRow><TableCell>project_name</TableCell><TableCell>TEXT</TableCell></TableRow>
          <TableRow><TableCell>north_south</TableCell><TableCell>TEXT</TableCell></TableRow>
          <TableRow><TableCell>east_west</TableCell><TableCell>TEXT</TableCell></TableRow>
          <TableRow><TableCell>elevation</TableCell><TableCell>TEXT</TableCell></TableRow>
          <TableRow><TableCell>angle_to_true_north</TableCell><TableCell>TEXT</TableCell></TableRow>
        </TableBody>
      </Table>
    </Box>
  ),
  backgroundColor: "#fff8e1",
};


const Home = () => {
  const [ideas, setIdeas] = useState({
    technicalCurrent: "",
    technicalFuture: "",
    companyCurrent: "",
    companyFuture: "",
    clientCurrent: "",
    clientFuture: "",
  });
  
  
  const [openIndex, setOpenIndex] = useState(null);
  const ideasRef = useRef();

  useEffect(() => {
    const savedIdeas = localStorage.getItem("project_ideas");
    if (savedIdeas) {
      setIdeas(JSON.parse(savedIdeas));
    }
  }, []);
  

  const saveIdeasAsPDF = () => {
    if (ideasRef.current) {
      const ideasText = `
        🔹 Технические решения — текущие идеи:
        ${ideas.techCurrent || "—"}
        
        🔹 Технические решения — новые идеи:
        ${ideas.techFuture || "—"}
  
        🔹 Решения для удобства внутри фирмы — текущие идеи:
        ${ideas.companyCurrent || "—"}
  
        🔹 Решения для удобства внутри фирмы — новые идеи:
        ${ideas.companyFuture || "—"}
  
        🔹 Идеи для внешних клиентов — текущие:
        ${ideas.clientCurrent || "—"}
  
        🔹 Идеи для внешних клиентов — новые:
        ${ideas.clientFuture || "—"}
      `;
  
      const element = document.createElement("div");
      element.innerText = ideasText;
      html2pdf().from(element).save("My_Project_Ideas.pdf");
    }
  };
  
  
  

  const toggleSection = (index) => {
    setOpenIndex(openIndex === index ? null : index);
  };

  return (
    <Box sx={{ maxWidth: "1200px", margin: "0 auto", py: 5 }}>
      <Typography variant="h3" align="center" color="primary" gutterBottom>
        🛠️ О проекте
      </Typography>

      {[...bimSections, fullstackSection, databaseTablesSection].map((section, index) => (
        <Paper
          key={index}
          elevation={4}
          sx={{
            backgroundColor: section.backgroundColor,
            mb: 4,
            borderRadius: 3,
            p: 2,
            cursor: "pointer"
          }}
          onClick={() => toggleSection(index)}
        >
          <Box display="flex" alignItems="center">
            <Typography variant="h5" sx={{ flexGrow: 1 }}>
              {section.title}
            </Typography>
            <IconButton>
              {openIndex === index ? <FaChevronDown /> : <FaChevronRight />}
            </IconButton>
          </Box>

          <AnimatePresence>
            {openIndex === index && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: "auto" }}
                exit={{ opacity: 0, height: 0 }}
                transition={{ duration: 0.5 }}
                style={{ overflow: "hidden" }}
              >
                <Box mt={2}>
                  {section.content}
                </Box>
              </motion.div>
            )}
          </AnimatePresence>
        </Paper>
      ))}

          {/* 💡 Блок для идей по категориям */}
      <Paper elevation={2} sx={{ p: 4, backgroundColor: "#fffde7", borderRadius: 3, mt: 6 }}>
        <Typography variant="h5" gutterBottom>💡 Идеи развития</Typography>
        <Box ref={ideasRef}>
            {/* 🔹 1. Технические решения для оптимизации работы */}
            <Typography variant="h5" gutterBottom sx={{ mt: 4 }}>1. 🛠️ Технические решения для оптимизации работы</Typography>

            <Typography variant="subtitle1" gutterBottom>• Мои текущие идеи:</Typography>
            <TextField
              fullWidth
              multiline
              rows={4}
              placeholder="Введите свои текущие идеи..."
              value={ideas.techCurrent}
              onChange={(e) => {
                const updatedIdeas = { ...ideas, techCurrent: e.target.value };
                setIdeas(updatedIdeas);
                localStorage.setItem("project_ideas", JSON.stringify(updatedIdeas));
              }}
              sx={{ mb: 3 }}
            />

            <Typography variant="subtitle1" gutterBottom>• Новые идеи (будущее):</Typography>
            <TextField
              fullWidth
              multiline
              rows={4}
              placeholder="Введите идеи на будущее..."
              value={ideas.techFuture}
              onChange={(e) => {
                const updatedIdeas = { ...ideas, techFuture: e.target.value };
                setIdeas(updatedIdeas);
                localStorage.setItem("project_ideas", JSON.stringify(updatedIdeas));
              }}
              sx={{ mb: 5 }}
            />

            {/* 🔹 2. Решения для внутренней координации */}
            <Typography variant="h5" gutterBottom sx={{ mt: 4 }}>2. 🤝 Решения для внутренней координации в компании</Typography>

            <Typography variant="subtitle1" gutterBottom>• Мои текущие идеи:</Typography>
            <TextField
              fullWidth
              multiline
              rows={4}
              placeholder="Введите текущие идеи для внутренней координации..."
              value={ideas.companyCurrent}
              onChange={(e) => {
                const updatedIdeas = { ...ideas, companyCurrent: e.target.value };
                setIdeas(updatedIdeas);
                localStorage.setItem("project_ideas", JSON.stringify(updatedIdeas));
              }}
              sx={{ mb: 3 }}
            />

            <Typography variant="subtitle1" gutterBottom>• Новые идеи (будущее):</Typography>
            <TextField
              fullWidth
              multiline
              rows={4}
              placeholder="Введите новые идеи для улучшения внутренней работы..."
              value={ideas.companyFuture}
              onChange={(e) => {
                const updatedIdeas = { ...ideas, companyFuture: e.target.value };
                setIdeas(updatedIdeas);
                localStorage.setItem("project_ideas", JSON.stringify(updatedIdeas));
              }}
              sx={{ mb: 5 }}
            />

            {/* 🔹 3. Решения для внешних клиентов */}
            <Typography variant="h5" gutterBottom sx={{ mt: 4 }}>3. 🌍 Решения для внешних клиентов</Typography>

            <Typography variant="subtitle1" gutterBottom>• Мои текущие идеи:</Typography>
            <TextField
              fullWidth
              multiline
              rows={4}
              placeholder="Введите текущие идеи для клиентов..."
              value={ideas.clientCurrent}
              onChange={(e) => {
                const updatedIdeas = { ...ideas, clientCurrent: e.target.value };
                setIdeas(updatedIdeas);
                localStorage.setItem("project_ideas", JSON.stringify(updatedIdeas));
              }}
              sx={{ mb: 3 }}
            />

            <Typography variant="subtitle1" gutterBottom>• Новые идеи (будущее):</Typography>
            <TextField
              fullWidth
              multiline
              rows={4}
              placeholder="Введите новые идеи для работы с клиентами..."
              value={ideas.clientFuture}
              onChange={(e) => {
                const updatedIdeas = { ...ideas, clientFuture: e.target.value };
                setIdeas(updatedIdeas);
                localStorage.setItem("project_ideas", JSON.stringify(updatedIdeas));
              }}
            />
          </Box>


        <Button variant="contained" color="success" sx={{ mt: 4 }} onClick={saveIdeasAsPDF}>
          💾 Сохранить все идеи в PDF
        </Button>
      </Paper>

    </Box>
  );
};

export default Home;
