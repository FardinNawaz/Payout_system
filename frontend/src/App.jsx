import {
  BrowserRouter,
  Routes,
  Route,
  Navigate
} from "react-router-dom";

import Login from "./pages/Login";
import Dashboard from "./pages/Dashboard";
import Organizations from "./pages/Organizations";
import Sidebar from "./components/sidebar";
import Header from "./components/Header";

function ProtectedLayout({ children }) {
  return (
    <div className="dashboard-layout">
      <Sidebar />

      <div className="main-content">
        <Header />
        {children}
      </div>
    </div>
  );
}

function App() {
  const token = localStorage.getItem("access_token");

  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Navigate to="/login" replace />} />

        <Route path="/login" element={<Login />} />

        <Route
          path="/dashboard"
          element={
            token ? (
              <ProtectedLayout>
                <Dashboard />
              </ProtectedLayout>
            ) : (
              <Navigate to="/login" replace />
            )
          }
        />

        <Route
          path="/organizations"
          element={
            token ? (
              <ProtectedLayout>
                <Organizations />
              </ProtectedLayout>
            ) : (
              <Navigate to="/login" replace />
            )
          }
        />
      </Routes>
    </BrowserRouter>
  );
}

export default App;