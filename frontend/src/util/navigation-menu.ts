/** Whether a footer/header nav row should show the external-link glyph. */
export function showExternalNavIcon(subItem: {
  label: string;
  key: string;
  to: string;
  icon?: boolean;
}): boolean {
  return Boolean(subItem.icon);
}
