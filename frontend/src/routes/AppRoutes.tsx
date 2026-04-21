import { Navigate, Route, Routes } from "react-router-dom";

import { Layout } from "../components/Layout";
import { LoginPage } from "../pages/LoginPage";
import { NotFoundPage } from "../pages/NotFoundPage";
import { RegisterPage } from "../pages/RegisterPage";


export function AppRoutes() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route index element={<Navigate to="/login" replace />} />
        <Route path="home" element={<Navigate to="/" replace />} />
        <Route path="login" element={<LoginPage />} />
        <Route path="register" element={<RegisterPage />} />
        {/* TODO: Add protected routes here. */}
        <Route path="*" element={<NotFoundPage />} />
      </Route>
    </Routes>
  );
}
