import { Navigate, Route, Routes } from "react-router-dom";

import { Layout } from "../components/Layout";
import { ProtectedRoute } from "../components/ProtectedRoute";
import { PublicOnlyRoute } from "../components/PublicOnlyRoute";
import { HomePage } from "../pages/HomePage";
import { LoginPage } from "../pages/LoginPage";
import { NotFoundPage } from "../pages/NotFoundPage";
import { RegisterPage } from "../pages/RegisterPage";
import { AcademicProfilePage } from "../pages/AcademicProfilePage";
import { EditProfilePage } from "../pages/EditProfilePage";
import { PresencePage } from "../pages/PresencePage";
import { StudySessionPage } from "../pages/StudySessionPage";
import { ProgressPage } from "../pages/ProgressPage";
import { GroupsPage } from "../pages/GroupsPage";
import { GroupMembersPage } from "../pages/GroupMembersPage";
import { GroupRankingPage } from "../pages/GroupRankingPage";
import { HistoryPage } from "../pages/HistoryPage";
import { InvitesPage } from "../pages/InvitesPage";
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
        <Route
          path="edit-profile"
          element={
            <ProtectedRoute>
              <EditProfilePage />
            </ProtectedRoute>
          }
        />
        <Route
          path="presence"
          element={
            <ProtectedRoute>
              <PresencePage />
            </ProtectedRoute>
          }
        />
        <Route
          path="study-sessions"
          element={
            <ProtectedRoute>
              <StudySessionPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="progress"
          element={
            <ProtectedRoute>
              <ProgressPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="groups"
          element={
            <ProtectedRoute>
              <GroupsPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="groups/:groupId/members"
          element={
            <ProtectedRoute>
              <GroupMembersPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="groups/:groupId/ranking"
          element={
            <ProtectedRoute>
              <GroupRankingPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="history"
          element={
            <ProtectedRoute>
              <HistoryPage />
            </ProtectedRoute>
          }
        />
        <Route
          path="invites"
          element={
            <ProtectedRoute>
              <InvitesPage />
            </ProtectedRoute>
          }
        />
        <Route path="*" element={<NotFoundPage />} />
      </Route>
    </Routes>
  );
}
