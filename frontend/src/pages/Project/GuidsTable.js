import React, { useEffect, useState } from "react";
import {
  Accordion, AccordionSummary, AccordionDetails, Typography,
  Box, List, ListItem, ListItemText
} from "@mui/material";
import ExpandMoreIcon from "@mui/icons-material/ExpandMore";
import ForgeViewer from "../../components/ForgeViewer";
const apiUrl = process.env.REACT_APP_API_URL || "${apiUrl}";

export default function GuidsTable() {
  const [data, setData] = useState([]);

  useEffect(() => {
    fetch(`${apiUrl}/api/views-table`)

      .then((res) => res.json())
      .then(setData)
      .catch((err) => console.error("Ошибка загрузки видов:", err));
  }, []);

  const grouped = {};
  data.forEach((entry) => {
    const { project, discipline, file_name, version_number, views } = entry;
    if (!grouped[project]) grouped[project] = {};
    if (!grouped[project][discipline]) grouped[project][discipline] = {};
    if (!grouped[project][discipline][file_name]) grouped[project][discipline][file_name] = {};
    grouped[project][discipline][file_name][version_number] = views;
  });

  return (
    <Box sx={{ p: 4 }}>
      <Typography variant="h4" gutterBottom align="center">
        📐 Таблица видов (GUIDs)
      </Typography>

      {Object.entries(grouped).map(([project, disciplines]) => (
        <Accordion key={project}>
          <AccordionSummary expandIcon={<ExpandMoreIcon />}>
            <Typography variant="h6">📁 {project}</Typography>
          </AccordionSummary>
          <AccordionDetails>
            {Object.entries(disciplines).map(([discipline, files]) => (
              <Accordion key={discipline}>
                <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                  <Typography>📌 Дисциплина: <strong>{discipline}</strong></Typography>
                </AccordionSummary>
                <AccordionDetails>
                  {Object.entries(files).map(([file, versions]) => (
                    <Accordion key={file}>
                      <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                        <Typography>📄 {file}</Typography>
                      </AccordionSummary>
                      <AccordionDetails>
                        {Object.entries(versions).map(([version, views]) => (
                          <Accordion key={version}>
                            <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                              <Typography>📦 Версия {version}</Typography>
                            </AccordionSummary>
                            <AccordionDetails>
                              {views.length > 0 ? (
                                views.map((v, i) => (
                                  <Box key={i} sx={{ mb: 4 }}>
                                    <Typography variant="subtitle2">
                                      👁 {v.view_name}
                                    </Typography>
                                    <ForgeViewer urn={v.urn} guid={v.guid} height={300} />
                                  </Box>
                                ))
                              ) : (
                                <Typography color="text.secondary">Нет доступных видов</Typography>
                              )}
                            </AccordionDetails>
                          </Accordion>
                        ))}
                      </AccordionDetails>
                    </Accordion>
                  ))}
                </AccordionDetails>
              </Accordion>
            ))}
          </AccordionDetails>
        </Accordion>
      ))}
    </Box>
  );
}

