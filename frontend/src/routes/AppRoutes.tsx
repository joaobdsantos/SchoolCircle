import { Navigate, Route, Routes } from "react-router-dom";

import { Layout } from "../components/Layout";
import { HomePage } from "../pages/HomePage";
import { NotFoundPage } from "../pages/NotFoundPage";


export function AppRoutes() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route index element={<HomePage />} />
        <Route path="home" element={<Navigate to="/" replace />} />
        {/* TODO: Add authentication routes and protected routes here. */}
        <Route path="*" element={<NotFoundPage />} />
      </Route>
    </Routes>
  );
}
