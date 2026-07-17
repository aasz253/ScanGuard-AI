export function getRiskColor(score) {
  if (score >= 80) return 'text-red-500';
  if (score >= 60) return 'text-orange-500';
  if (score >= 40) return 'text-yellow-500';
  if (score >= 20) return 'text-green-500';
  return 'text-emerald-500';
}

export function getRiskBg(score) {
  if (score >= 80) return 'bg-red-500/10';
  if (score >= 60) return 'bg-orange-500/10';
  if (score >= 40) return 'bg-yellow-500/10';
  if (score >= 20) return 'bg-green-500/10';
  return 'bg-emerald-500/10';
}

export function getRiskBadge(risk) {
  const map = {
    critical: 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400',
    high: 'bg-orange-100 text-orange-700 dark:bg-orange-900/30 dark:text-orange-400',
    medium: 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-400',
    low: 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400',
  };
  return map[risk] || map.low;
}

export function getRiskLabel(score) {
  if (score >= 80) return 'CRITICAL';
  if (score >= 60) return 'HIGH';
  if (score >= 40) return 'MEDIUM';
  if (score >= 20) return 'LOW';
  return 'MINIMAL';
}

export function formatNumber(n) {
  if (n >= 1000000) return (n / 1000000).toFixed(1) + 'M';
  if (n >= 1000) return (n / 1000).toFixed(1) + 'K';
  return n?.toString() || '0';
}
