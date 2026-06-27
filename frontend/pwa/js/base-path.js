/**
 * Base path para GitHub Pages (project site: usuario.github.io/TerraPilot/).
 */
window.TERRAPILOT_BASE = (() => {
  if (!window.location.hostname.includes('github.io')) return '';
  const parts = window.location.pathname.split('/').filter(Boolean);
  if (!parts.length || parts[0].includes('.')) return '/';
  const repo = parts[0];
  if (parts[1] === 'pwa' || parts[1] === 'analyst') {
    return `/${repo}/${parts[1]}/`;
  }
  return `/${repo}/`;
})();

window.terrapilotUrl = (path) => {
  const clean = String(path).replace(/^\//, '');
  return `${window.TERRAPILOT_BASE}${clean}`;
};
