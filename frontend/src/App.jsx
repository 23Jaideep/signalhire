import React, { useState, useEffect } from "react";
import Editor from "@monaco-editor/react";

function App() {
  // --- STATE ---
  const [files, setFiles] = useState({});
  const [activeFile, setActiveFile] = useState("");
  const [output, setOutput] = useState("");
  const [coreResult, setCoreResult] = useState(null);
  const [mutationResult, setMutationResult] = useState(null);
  const [analytics, setAnalytics] = useState(null);
  const [loadingPhase, setLoadingPhase] = useState(null);
  const [sessionId, setSessionId] = useState(null);
  const [taskId, setTaskId] = useState(null);

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
      console.log("NEW SESSION:", data.session_id);

      setSessionId(data.session_id);
      console.log("STATE WILL BE:", data.session_id);

      console.log("SESSION STARTED:", data.session_id);

    } catch (err) {
      console.error("Failed to start session", err);
      setOutput("Failed to start session");
    }
  };

  


useEffect(() => {
  startSession();
}, []);

  const uploadTask = async (event) => {

  const file = event.target.files[0];

  if (!file) return;

  const formData = new FormData();

  formData.append("file", file);

  try {

    // ---- upload zip ----
    const uploadRes = await fetch(
      "http://127.0.0.1:8000/upload_task",
      {
        method: "POST",
        body: formData,
      }
    );

    const uploadData = await uploadRes.json();

    console.log("UPLOAD RESPONSE:", uploadData);

    if (uploadData.status !== "uploaded") {

      setOutput("Task upload failed");

      return;
    }

    const uploadedTaskId = uploadData.task_id;

    setTaskId(uploadedTaskId);

    // ---- fetch uploaded task ----
    console.log("FETCHING TASK:", uploadedTaskId);
    const taskRes = await fetch(
      `http://127.0.0.1:8000/uploaded_task/${uploadedTaskId}`
    );

    const taskData = await taskRes.json();

    console.log("TASK DATA:", taskData);

    setFiles(taskData.files);

    const firstFile = Object.keys(taskData.files)[0];

    setActiveFile(firstFile);

    setOutput("Task loaded successfully");

  } catch (err) {

  console.error("UPLOAD ERROR:", err);

  setOutput(String(err));

}
};

  // --- RUN TESTS ---
  const runTests = async (phase) => {
    if (!sessionId) {
      setOutput("Session not started yet");
      return;
    }

    setLoadingPhase(phase);
    console.log("Sending session:", sessionId);
    try {
      const res = await fetch("http://127.0.0.1:8000/run_tests", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
  files,
  session_id: sessionId,
  task_id: taskId,
  phase,
}),
      });

      const data = await res.json();

      if (phase === "core") {
          setCoreResult(data);
      } else {
          setMutationResult(data);
      }

    } catch (err) {
      console.error(err);
      setOutput("Error connecting to backend");
    }

    setLoadingPhase(null);
  };

  const loadAnalytics = async () => {
    if (!sessionId) return;

    const res = await fetch(
      `http://127.0.0.1:8000/session/${sessionId}`
    );

    const data = await res.json();

    console.log(data);

    setAnalytics(data);
  };

  return (
    <div style={{ height: "100vh" }}>
      <div style={{ padding: 10 }}>

  <input
    type="file"
    accept=".zip"
    onChange={uploadTask}
  />

</div>
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
      <div
        style={{
          flex: 2,
          overflow: "hidden",
        }}
      >
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
      <div
        style={{
          flex: 1,
          padding: 20,
          borderLeft: "1px solid gray",
          overflowY: "auto",
          overflowX: "hidden",
          minWidth: 350,
        }}
      >
        
        <h3>Test Runner</h3>

        <div style={{ marginBottom: 10 }}>
          <b>Session ID:</b>
          <div style={{ fontSize: 12 }}>
            {sessionId || "Starting..."}
          </div>
        </div>

        <div style={{ marginBottom: 10 }}>
  <b>Task ID:</b>

  <div style={{ fontSize: 12 }}>
    {taskId || "No task uploaded"}
  </div>
</div>

        <button
    onClick={() => runTests("core")}
    disabled={loadingPhase === "core"}
>
    {loadingPhase === "core"
        ? "Running..."
        : "Run Core Tests"}
</button>

<button
    onClick={() => runTests("mutation")}
    disabled={loadingPhase === "mutation"}
>
    {loadingPhase === "mutation"
        ? "Running..."
        : "Run Mutation Tests"}
</button>
<div style={{ marginTop: 20 }}>

    <h4>Core Tests</h4>

    {coreResult ? (
        <>
            <p>
                Status: {coreResult.passed ? "✅ PASSED" : "❌ FAILED"}
            </p>

            <pre
              style={{
                whiteSpace: "pre-wrap",
                wordBreak: "break-word",
                overflowX: "auto",
                maxWidth: "100%",
              }}
            >
              {coreResult.output}
            </pre>
        </>
    ) : (
        <p>Not run yet</p>
    )}

</div>

<div style={{ marginTop: 20 }}>

    <h4>Mutation Tests</h4>

    {mutationResult ? (
        <>
            <p>
                Status: {mutationResult.passed ? "✅ PASSED" : "❌ FAILED"}
            </p>

            <pre
              style={{
                whiteSpace: "pre-wrap",
                wordBreak: "break-word",
                overflowX: "auto",
                maxWidth: "100%",
              }}
            >
              {mutationResult.output}
            </pre>
        </>
    ) : (
        <p>Not run yet</p>
    )}

</div>
<div style={{ marginTop: 30 }}>

  <button onClick={loadAnalytics}>
    Load Session Analytics
  </button>
  {analytics && (
  <div style={{ marginTop: 20 }}>

    <h3>Interview Analytics</h3>

    <p>Core Runs: {analytics.summary.core_runs}</p>

    <p>Mutation Runs: {analytics.summary.mutation_runs}</p>

    <p>
      Core Passed:
      {analytics.summary.core_passed ? " ✅" : " ❌"}
    </p>

    <p>
      Mutation Passed:
      {analytics.summary.mutation_passed ? " ✅" : " ❌"}
    </p>

    <p>
  Avg edit time: {analytics.summary.time_between_runs?.avg?.toFixed(2) ?? "-"} s
</p>

  </div>
)}

</div>
      </div>
    </div>
    </div>
  );
}

export default App;