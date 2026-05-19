import { Navigate, Route, Routes } from "react-router-dom";

import { Layout } from "../components/Layout";
import { ProtectedRoute } from "../components/ProtectedRoute";
import { PublicOnlyRoute } from "../components/PublicOnlyRoute";
import { HomePage } from "../pages/HomePage";
import { LoginPage } from "../pages/LoginPage";
import { NotFoundPage } from "../pages/NotFoundPage";
import { RegisterPage } from "../pages/RegisterPage";
import { AcademicProfilePage } from "../pages/AcademicProfilePage";
import { ACCESS_TOKEN_KEY } from "../services/auth";

export function AppRoutes() {
  const hasAccessToken = Boolean(localStorage.getItem(ACCESS_TOKEN_KEY));

  return (
    <Routes>
      <Route element={<Layout />}>
        <Route index element={<Navigate to={hasAccessToken ? "/home" : "/login"} replace />} />
        <Route
          path="home"
          element={
            <ProtectedRoute>
              <HomePage />
            </ProtectedRoute>
          }
        />
        <Route
          path="login"
          element={
            <PublicOnlyRoute>
              <LoginPage />
            </PublicOnlyRoute>
          }
        />
        <Route
          path="register"
          element={
            <PublicOnlyRoute>
              <RegisterPage />
            </PublicOnlyRoute>
          }
        />
        <Route
          path="academic-profile"
          element={
            <ProtectedRoute>
              <AcademicProfilePage />
            </ProtectedRoute>
          }
        />
        <Route path="*" element={<NotFoundPage />} />
      </Route>
    </Routes>
  );
}
