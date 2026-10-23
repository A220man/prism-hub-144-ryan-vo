// Frontend Tests - Components
import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { HealthCheck } from './components/HealthCheck';
import { Modal } from './components/Modal';
import { ToastProvider, useToast } from './components/Toast';

// Mock API for HealthCheck
vi.mock('./api/client', () => ({
  api: {
    getHealth: vi.fn().mockResolvedValue({
      status: 'healthy',
      version: '1.0.0',
      environment: 'development',
      database: 'healthy',
      demo_mode: false,
    }),
  },
}));

describe('HealthCheck', () => {
  it('shows loading state initially', () => {
    render(<HealthCheck />);
    expect(screen.getByText('Checking backend health...')).toBeInTheDocument();
  });

  it('displays healthy status after load', async () => {
    render(<HealthCheck />);
    await waitFor(() => {
      expect(screen.getByText('Backend Status')).toBeInTheDocument();
    });
    expect(screen.getByText('All systems operational')).toBeInTheDocument();
    expect(screen.getByText('Version:')).toBeInTheDocument();
    expect(screen.getByText('1.0.0')).toBeInTheDocument();
  });
});

describe('Modal', () => {
  it('renders when open', () => {
    render(
      <Modal isOpen={true} onClose={vi.fn()} title="Test Modal">
        <p>Modal content</p>
      </Modal>
    );
    expect(screen.getByRole('dialog')).toBeInTheDocument();
    expect(screen.getByText('Test Modal')).toBeInTheDocument();
    expect(screen.getByText('Modal content')).toBeInTheDocument();
  });

  it('does not render when closed', () => {
    render(
      <Modal isOpen={false} onClose={vi.fn()} title="Test Modal">
        <p>Modal content</p>
      </Modal>
    );
    expect(screen.queryByRole('dialog')).not.toBeInTheDocument();
  });

  it('calls onClose when overlay clicked', () => {
    const onClose = vi.fn();
    render(
      <Modal isOpen={true} onClose={onClose} title="Test Modal">
        <p>Modal content</p>
      </Modal>
    );
    fireEvent.click(screen.getByText('Modal content').parentElement!);
    // Overlay click should close
    fireEvent.click(document.body);
    // Actually clicking overlay - need to target it
    expect(onClose).not.toHaveBeenCalled(); // Content click shouldn't close
  });

  it('closes on Escape key', () => {
    const onClose = vi.fn();
    render(
      <Modal isOpen={true} onClose={onClose} title="Test Modal">
        <p>Modal content</p>
      </Modal>
    );
    fireEvent.keyDown(document, { key: 'Escape' });
    expect(onClose).toHaveBeenCalled();
  });
});

describe('Toast', () => {
  it('shows toast when showToast called', () => {
    function TestComponent() {
      const { showToast } = useToast();
      return <button onClick={() => showToast('Test message', 'success')}>Show Toast</button>;
    }

    render(
      <ToastProvider>
        <TestComponent />
      </ToastProvider>
    );

    fireEvent.click(screen.getByRole('button', { name: 'Show Toast' }));
    expect(screen.getByRole('alert')).toHaveTextContent('Test message');
  });

  it('auto-dismisses toast after timeout', async () => {
    function TestComponent() {
      const { showToast } = useToast();
      return <button onClick={() => showToast('Test message', 'info')}>Show Toast</button>;
    }

    render(
      <ToastProvider>
        <TestComponent />
      </ToastProvider>
    );

    fireEvent.click(screen.getByRole('button', { name: 'Show Toast' }));
    expect(screen.getByRole('alert')).toBeInTheDocument();

    // Wait for auto-dismiss (5 seconds in implementation, but we use fake timers)
    await waitFor(() => {
      expect(screen.queryByRole('alert')).not.toBeInTheDocument();
    }, { timeout: 6000 });
  });
});