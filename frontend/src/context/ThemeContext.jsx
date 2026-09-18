import React, { createContext, useContext, useEffect, useState } from 'react';

const ThemeContext = createContext();
export const useTheme = () => useContext(ThemeContext);

const THEME_KEY = 'ecg_theme';

// Nguon DUY NHAT cho theme sang/toi toan app (truoc/sau dang nhap deu dung chung context nay,
// khong con tach rieng logic o LoginPage.jsx nhu truoc). theme: 'light' | 'dark' | null (null =
// theo he thong, khong ep - qua prefers-color-scheme). Ap dung bang attribute data-theme tren
// <html>, doc boi index.css.
export const ThemeProvider = ({ children }) => {
  const [theme, setTheme] = useState(() => {
    try {
      return localStorage.getItem(THEME_KEY) || null;
    } catch {
      return null;
    }
  });

  useEffect(() => {
    const root = document.documentElement;
    if (theme) {
      root.setAttribute('data-theme', theme);
    } else {
      root.removeAttribute('data-theme');
    }
    try {
      if (theme) localStorage.setItem(THEME_KEY, theme);
      else localStorage.removeItem(THEME_KEY);
    } catch {
      // localStorage khong kha dung (private mode...) - theme van hoat dong trong phien
    }
  }, [theme]);

  const isDarkActive = theme
    ? theme === 'dark'
    : typeof window !== 'undefined' && window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;

  const toggleTheme = () => setTheme(isDarkActive ? 'light' : 'dark');

  return (
    <ThemeContext.Provider value={{ theme, setTheme, isDarkActive, toggleTheme }}>
      {children}
    </ThemeContext.Provider>
  );
};

export default ThemeContext;
