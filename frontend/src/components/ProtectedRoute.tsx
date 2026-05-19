import { Navigate } from "react-router-dom";
import { ReactNode } from "react";

import { ACCESS_TOKEN_KEY } from "../services/auth";

type ProtectedRouteProps = {
  children: ReactNode;
};

export function ProtectedRoute({ children }: ProtectedRouteProps) {
  const hasAccessToken = Boolean(localStorage.getItem(ACCESS_TOKEN_KEY));

  if (!hasAccessToken) {
    return <Navigate to="/login" replace />;
  }

  return <>{children}</>;
}
