import React, { useState, useEffect } from "react";
import Editor from "@monaco-editor/react";

function App() {
  // --- STATE ---
  const [files, setFiles] = useState({});
  const [activeFile, setActiveFile] = useState("");

  const [output, setOutput] = useState("");
  const [loading, setLoading] = useState(false);
  const [sessionId, setSessionId] = useState(null);

  // --- START SESSION ---
  const startSession = async () => {
    try {
      const res = await fetch("http://127.0.0.1:8000/session/start", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          candidate_id: "test_user",
          task_name: "task1",
        }),
      });

      const data = await res.json();

      setSessionId(data.session_id);

      console.log("SESSION STARTED:", data.session_id);

    } catch (err) {
      console.error("Failed to start session", err);
      setOutput("Failed to start session");
    }
  };

  // --- AUTO START SESSION ---

  const loadTask = async () => {

  try {

    const res = await fetch(
      "http://127.0.0.1:8000/task/log_parser_v1"
    );

    const data = await res.json();

    setFiles(data.files);

    const firstFile = Object.keys(data.files)[0];

    setActiveFile(firstFile);

    console.log("TASK LOADED:", data);

  } catch (err) {

    console.error("Task loading failed", err);

  }
};

useEffect(() => {
  startSession();
  loadTask();
}, []);

  // --- RUN TESTS ---
  const runTests = async () => {
    if (!sessionId) {
      setOutput("Session not started yet");
      return;
    }

    setLoading(true);

    try {
      const res = await fetch("http://127.0.0.1:8000/run_tests", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
  files,
  session_id: sessionId,
}),
      });

      const data = await res.json();

      if (data.passed) {
        setOutput("PASSED");
      } else {
        setOutput("FAILED");
      }

    } catch (err) {
      console.error(err);
      setOutput("Error connecting to backend");
    }

    setLoading(false);
  };

  return (
    <div style={{ height: "100vh" }}>

      <div
  style={{
    display: "flex",
    gap: 10,
    padding: 10,
    background: "#1e1e1e"
  }}
>

  {Object.keys(files).map((file) => (

    <button
      key={file}
      onClick={() => setActiveFile(file)}
      style={{
        padding: "6px 12px",
        background:
          activeFile === file ? "#444" : "#222",
        color: "white",
        border: "1px solid #666"
      }}
    >
      {file}
    </button>

  ))}

</div>
      <div style={{ display: "flex", height: "calc(100% - 50px)" }}>
      {/* LEFT: EDITOR */}
      <div style={{ flex: 2 }}>
        <Editor
          height="100%"
          defaultLanguage="python"
          value={files[activeFile] || ""}

onChange={(value) => {

  setFiles({
    ...files,
    [activeFile]: value
  });

}}
          theme="vs-dark"
        />
      </div>

      {/* RIGHT: PANEL */}
      <div style={{ flex: 1, padding: 20, borderLeft: "1px solid gray" }}>
        
        <h3>Test Runner</h3>

        <div style={{ marginBottom: 10 }}>
          <b>Session ID:</b>
          <div style={{ fontSize: 12 }}>
            {sessionId || "Starting..."}
          </div>
        </div>

        <button onClick={runTests} disabled={loading}>
          {loading ? "Running..." : "Run Tests"}
        </button>

        <div style={{ marginTop: 20 }}>
          <b>Output:</b>
          <pre>{output}</pre>
        </div>
      </div>
    </div>
    </div>
  );
}

export default App;