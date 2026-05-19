import { Navigate } from "react-router-dom";
import { ReactNode } from "react";

import { ACCESS_TOKEN_KEY } from "../services/auth";

type PublicOnlyRouteProps = {
  children: ReactNode;
};

export function PublicOnlyRoute({ children }: PublicOnlyRouteProps) {
  const hasAccessToken = Boolean(localStorage.getItem(ACCESS_TOKEN_KEY));

  if (hasAccessToken) {
    return <Navigate to="/home" replace />;
  }

  return <>{children}</>;
}
