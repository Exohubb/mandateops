import { Route, Routes } from "react-router-dom";
import { AppShell } from "./components/layout/AppShell";
import { HomePage } from "./pages/HomePage";
import { DashboardPage } from "./pages/DashboardPage";
import { MandateExplorerPage } from "./pages/MandateExplorerPage";
import { CopilotPage } from "./pages/CopilotPage";
import { AuditTrailPage } from "./pages/AuditTrailPage";
import { AiJudgmentPage } from "./pages/AiJudgmentPage";

function App() {
  return (
    <AppShell>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/dashboard" element={<DashboardPage />} />
        <Route path="/mandates" element={<MandateExplorerPage />} />
        <Route path="/copilot" element={<CopilotPage />} />
        <Route path="/audit" element={<AuditTrailPage />} />
        <Route path="/ai-judgment" element={<AiJudgmentPage />} />
      </Routes>
    </AppShell>
  );
}

export default App;
