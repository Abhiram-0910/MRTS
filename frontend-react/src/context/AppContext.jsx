/**
 * AppContext — lightweight context for non-auth app-wide state.
 *
 * Auth (login/logout/token) is handled exclusively by AuthContext.
 * This context only holds userId (derived from the logged-in user)
 * and language preference.
 */
import React, { createContext, useContext } from 'react';
import { useAuth } from './AuthContext';

const AppContext = createContext();

export const AppProvider = ({ children }) => {
  const { user } = useAuth();

  // userId comes from the authenticated user; falls back to 'guest'
  const userId = user?.username ?? 'guest';
  const language = 'en';

  return (
    <AppContext.Provider value={{ userId, language }}>
      {children}
    </AppContext.Provider>
  );
};

export const useAppContext = () => useContext(AppContext);
