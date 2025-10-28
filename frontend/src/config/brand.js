/**
 * DiveTeacher Brand Configuration
 * Ocean-themed color palette and brand constants
 */

export const brand = {
  name: 'DiveTeacher',
  tagline: 'Your AI-Powered Diving Education Platform',
  
  colors: {
    // Primary ocean blues
    primary: '#0077BE',      // Deep ocean blue
    secondary: '#00A8E8',    // Bright aqua
    accent: '#00C9FF',       // Light cyan
    dark: '#003D5B',         // Dark navy
    
    // Status colors
    success: '#10b981',
    warning: '#f59e0b',
    error: '#ef4444',
    info: '#3b82f6',
  },
  
  stages: [
    { key: 'validation', label: 'Validation', range: [0, 25] },
    { key: 'conversion', label: 'Conversion', range: [25, 50] },
    { key: 'chunking', label: 'Chunking', range: [50, 75] },
    { key: 'ingestion', label: 'Ingestion', range: [75, 100] }
  ],
  
  // API endpoints
  api: {
    upload: '/api/upload',
    uploadStatus: (id) => `/api/upload/${id}/status`,
    queryStream: '/api/query/stream',
    queryHealth: '/api/query/health',
  }
};

