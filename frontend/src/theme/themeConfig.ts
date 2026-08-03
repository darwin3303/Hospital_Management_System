import type { ThemeConfig } from 'antd';
import { blue, neutral, semantic, radii } from './tokens';

/**
 * Single source of truth for Ant Design's theme. Every AntD component
 * (Button, Table, Menu, etc.) reads its colours from this object, so a
 * palette change here updates the whole app without touching component code.
 */
export const themeConfig: ThemeConfig = {
  token: {
    colorPrimary: blue[600],
    colorLink: blue[600],
    colorLinkHover: blue[400],
    colorSuccess: semantic.success,
    colorWarning: semantic.warning,
    colorError: semantic.danger,
    colorBgLayout: neutral[50],
    colorBgContainer: neutral[0],
    colorBorder: neutral[200],
    colorText: neutral[900],
    colorTextSecondary: neutral[600],
    colorTextTertiary: neutral[400],
    borderRadius: radii.md,
    fontFamily:
      "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif",
  },
  components: {
    Layout: {
      siderBg: neutral[0],
      headerBg: neutral[0],
      bodyBg: neutral[50],
    },
    Menu: {
      itemSelectedBg: blue[50],
      itemSelectedColor: blue[600],
      itemHoverBg: blue[50],
      itemActiveBg: blue[100],
    },
    Button: {
      colorPrimary: blue[600],
      colorPrimaryHover: blue[400],
    },
    Table: {
      headerBg: neutral[50],
      headerColor: neutral[600],
      rowHoverBg: blue[50],
    },
    Card: {
      borderRadiusLG: radii.lg,
    },
    Tag: {
      defaultBg: neutral[100],
    },
  },
};
