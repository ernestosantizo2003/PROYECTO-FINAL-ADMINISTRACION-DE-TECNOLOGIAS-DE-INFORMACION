import React, { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { Lock, User, Eye, EyeOff, Cpu, AlertCircle } from 'lucide-react';
import { useAuth } from '../../hooks/useAuth';
import { Button } from '../../components/ui/Button';
import { Input } from '../../components/ui/Input';

export const LoginPage: React.FC = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const from = (location.state as { from?: { pathname: string } })?.from?.pathname || '/dashboard';

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!username.trim() || !password.trim()) {
      setError('Por favor ingresa tu usuario y contraseña');
      return;
    }
    setError('');
    setIsLoading(true);
    try {
      await login(username, password);
      navigate(from, { replace: true });
    } catch (err: unknown) {
      const axiosError = err as { response?: { data?: { detail?: string } } };
      const msg =
        axiosError?.response?.data?.detail ||
        'Credenciales incorrectas. Verifica tu usuario y contraseña.';
      setError(msg);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="w-full max-w-md">
      {/* Logo */}
      <div className="text-center mb-8">
        <div className="inline-flex items-center justify-center w-16 h-16 bg-indigo-600 rounded-2xl shadow-lg mb-4">
          <Cpu className="w-9 h-9 text-white" />
        </div>
        <h1 className="text-3xl font-bold text-white tracking-tight">
          NEXUS<span className="text-indigo-400">CORP</span>
        </h1>
        <p className="text-gray-400 text-sm mt-2">
          Arquitectura de Inteligencia Organizacional
        </p>
        <p className="text-gray-500 text-xs mt-1">
          Sistema de Soporte a Decisiones Basado en Conocimiento
        </p>
      </div>

      {/* Card */}
      <div className="bg-white rounded-2xl shadow-2xl p-8">
        <h2 className="text-xl font-semibold text-gray-900 mb-6 text-center">
          Iniciar Sesión
        </h2>

        {error && (
          <div className="flex items-center gap-2 bg-red-50 border border-red-200 text-red-700 text-sm rounded-lg px-4 py-3 mb-5">
            <AlertCircle className="w-4 h-4 flex-shrink-0" />
            <span>{error}</span>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <Input
            label="Usuario"
            id="username"
            type="text"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            placeholder="Ingresa tu nombre de usuario"
            required
            autoComplete="username"
            autoFocus
            leftIcon={<User className="w-4 h-4" />}
          />

          <Input
            label="Contraseña"
            id="password"
            type={showPassword ? 'text' : 'password'}
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="Ingresa tu contraseña"
            required
            autoComplete="current-password"
            leftIcon={<Lock className="w-4 h-4" />}
            rightIcon={
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="hover:text-gray-600 transition-colors"
              >
                {showPassword ? (
                  <EyeOff className="w-4 h-4" />
                ) : (
                  <Eye className="w-4 h-4" />
                )}
              </button>
            }
          />

          <Button
            type="submit"
            variant="primary"
            size="lg"
            isLoading={isLoading}
            className="w-full mt-2"
          >
            {isLoading ? 'Iniciando sesión...' : 'Iniciar Sesión'}
          </Button>
        </form>

        {/* Test credentials */}
        <div className="mt-6 p-4 bg-gray-50 rounded-lg border border-gray-200">
          <p className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-2">
            Credenciales de Prueba
          </p>
          <div className="space-y-1 text-xs text-gray-600">
            <div className="flex justify-between">
              <span className="font-medium">Admin Sistema:</span>
              <span className="font-mono">admin / admin123</span>
            </div>
            <div className="flex justify-between">
              <span className="font-medium">Decisor:</span>
              <span className="font-mono">decisor / decisor123</span>
            </div>
            <div className="flex justify-between">
              <span className="font-medium">Analista:</span>
              <span className="font-mono">analista / analista123</span>
            </div>
            <div className="flex justify-between">
              <span className="font-medium">Admin Conocimiento:</span>
              <span className="font-mono">knowledge / knowledge123</span>
            </div>
          </div>
        </div>
      </div>

      <p className="text-center text-gray-600 text-xs mt-6">
        &copy; {new Date().getFullYear()} NexusCorp — Sistema de Inteligencia Organizacional
      </p>
    </div>
  );
};
