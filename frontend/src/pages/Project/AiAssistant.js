import React, { useState } from "react";
import {
  Box,
  Typography,
  TextField,
  Button,
  Paper,
  Divider
} from "@mui/material";
const apiUrl = process.env.REACT_APP_API_URL || "${apiUrl}";

export default function AiAssistant() {
  const [question, setQuestion] = useState("");
  const [chat, setChat] = useState([]);
  const [loading, setLoading] = useState(false);

  const handleSend = async () => {
    if (!question.trim() || loading) return;

    const userMessage = { role: "user", text: question };
    setChat((prev) => [...prev, userMessage]);
    setLoading(true);

    try {
      const res = await fetch(`${apiUrl}/api/chat`, {

        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question })
      });

      const data = await res.json();
      const botMessage = { role: "bot", text: data.answer };
      setChat((prev) => [...prev, botMessage]);
    } catch (err) {
      setChat((prev) => [
        ...prev,
        { role: "bot", text: "⚠️ Ошибка сервера. Проверь соединение." }
      ]);
    }

    setQuestion("");
    setLoading(false);
  };

  return (
    <Box sx={{ p: 4, maxWidth: 900, margin: "auto" }}>
      <Typography variant="h4" fontWeight="bold" align="center" gutterBottom>
        🤖 AI-Ассистент (FastAPI)
      </Typography>

      <Paper sx={{ p: 2, mb: 2, height: 400, overflowY: "auto", backgroundColor: "#f4f6f8" }}>
        {chat.length === 0 && (
          <Typography color="text.secondary" align="center" sx={{ mt: 12 }}>
            💬 Задай вопрос про проекты, версии, дисциплины, координаты...
          </Typography>
        )}
        {chat.map((msg, i) => (
          <Box
            key={i}
            sx={{
              display: "flex",
              justifyContent: msg.role === "user" ? "flex-end" : "flex-start",
              mb: 1
            }}
          >
            <Box
              sx={{
                px: 2,
                py: 1.5,
                borderRadius: 2,
                maxWidth: "75%",
                backgroundColor: msg.role === "user" ? "#1976d2" : "#e0e0e0",
                color: msg.role === "user" ? "#fff" : "#000",
                whiteSpace: "pre-line"
              }}
            >
              {msg.text}
            </Box>
          </Box>
        ))}
      </Paper>

      <Divider sx={{ my: 2 }} />

      <Box sx={{ display: "flex", gap: 2 }}>
        <TextField
          fullWidth
          label="Задай вопрос..."
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && handleSend()}
        />
        <Button
          variant="contained"
          onClick={handleSend}
          disabled={loading || !question.trim()}
        >
          {loading ? "..." : "Отправить"}
        </Button>
      </Box>
    </Box>
  );
}

