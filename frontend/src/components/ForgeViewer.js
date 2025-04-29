import React, { useEffect, useRef, useState } from "react";

export default function ForgeViewer({ urn, guid, height = 300 }) {
  const viewerRef = useRef(null);
  const [token, setToken] = useState(null);

  useEffect(() => {
    fetch("http://localhost:8000/api/token")
      .then((res) => res.json())
      .then((data) => setToken(data.access_token))
      .catch((err) => console.error("Ошибка получения токена:", err));
  }, []);

  useEffect(() => {
    if (!urn || !guid || !token) return;

    const options = {
      env: "AutodeskProduction",
      accessToken: token,
    };

    Autodesk.Viewing.Initializer(options, () => {
      const viewerDiv = viewerRef.current;
      const viewer = new Autodesk.Viewing.GuiViewer3D(viewerDiv);
      viewer.start();

      const documentId = `urn:${urn}`;
      Autodesk.Viewing.Document.load(documentId, (doc) => {
        const viewable = doc.getRoot().findByGuid(guid);
        if (viewable) {
          viewer.loadDocumentNode(doc, viewable);
        } else {
          console.warn("Viewable с GUID не найден:", guid);
        }
      });
    });

    return () => {
      if (viewerRef.current) viewerRef.current.innerHTML = "";
    };
  }, [urn, guid, token]);

  return <div ref={viewerRef} style={{ height: `${height}px`, width: "100%", border: "1px solid #ccc", borderRadius: "8px", marginBottom: "1rem" }} />;
}
