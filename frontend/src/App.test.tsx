// Frontend Tests - Dashboard
import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { App } from './App';

// Mock API
vi.mock('./api/client', () => ({
  api: {
    getHealth: vi.fn().mockResolvedValue({
      status: 'healthy',
      version: '1.0.0',
      environment: 'development',
      database: 'healthy',
      demo_mode: true,
    }),
  },
}));

describe('Dashboard', () => {
  it('renders dashboard with health check', async () => {
    render(
      <BrowserRouter>
        <App />
      </BrowserRouter>
    );

    expect(screen.getByText('Prism Hub')).toBeInTheDocument();
    expect(screen.getByRole('heading', { name: 'Dashboard' })).toBeInTheDocument();
    // Health check loads asynchronously
    await vi.waitFor(() => {
      expect(screen.getByText('Backend Status')).toBeInTheDocument();
    });
  });
});

describe('App Routing', () => {
  it('navigates to prompts page', async () => {
    render(
      <BrowserRouter>
        <App />
      </BrowserRouter>
    );

    const promptsLink = screen.getByRole('link', { name: 'Prompts' });
    promptsLink.click();

    await vi.waitFor(() => {
      expect(screen.getByRole('heading', { name: 'Prompts' })).toBeInTheDocument();
    });
  });

  it('navigates to evaluation page', async () => {
    render(
      <BrowserRouter>
        <App />
      </BrowserRouter>
    );

    const evalLink = screen.getByRole('link', { name: 'Evaluation' });
    evalLink.click();

    await vi.waitFor(() => {
      expect(screen.getByRole('heading', { name: 'Evaluation' })).toBeInTheDocument();
    });
  });

  it('navigates to settings page', async () => {
    render(
      <BrowserRouter>
        <App />
      </BrowserRouter>
    );

    const settingsLink = screen.getByRole('link', { name: 'Settings' });
    settingsLink.click();

    await vi.waitFor(() => {
      expect(screen.getByRole('heading', { name: 'Settings' })).toBeInTheDocument();
    });
  });
});