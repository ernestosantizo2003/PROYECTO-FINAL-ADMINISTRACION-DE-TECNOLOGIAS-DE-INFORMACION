import React, { useState } from 'react';
import { Play, Save, AlertCircle, CheckCircle, XCircle, ChevronDown, ChevronUp } from 'lucide-react';
import { Decision, Recommendation, WhatIfRequest } from '../../types';
import { decisionsService } from '../../services/decisions.service';
import { Button } from '../../components/ui/Button';
import { Input, Textarea } from '../../components/ui/Input';
import { Card } from '../../components/ui/Card';
import { PriorityBadge } from '../../components/ui/Badge';
import { Spinner } from '../../components/ui/Spinner';
import { useToast } from '../../hooks/useToast';
import { ToastContainer } from '../../components/ui/Toast';

type Level = 'bajo' | 'medio' | 'alto';

interface WhatIfForm {
  name: string;
  description: string;
  stock_level: number;
  demand_level: Level;
  risk_level: Level;
}

const levelColors: Record<Level, string> = {
  bajo: 'bg-green-100 border-green-400 text-green-700',
  medio: 'bg-yellow-100 border-yellow-400 text-yellow-700',
  alto: 'bg-red-100 border-red-400 text-red-700',
};

const levelLabels: Record<Level, string> = {
  bajo: 'Bajo',
  medio: 'Medio',
  alto: 'Alto',
};

const RecommendationCard: React.FC<{
  rec: Recommendation;
  index: number;
  onAccept: (id: string) => void;
  onReject: (id: string) => void;
  localStatus: Record<string, 'accepted' | 'rejected'>;
}> = ({ rec, index, onAccept, onReject, localStatus }) => {
  const [expanded, setExpanded] = useState(true);
  const status = localStatus[rec.id];

  return (
    <div
      className={`border rounded-lg overflow-hidden transition-all ${
        status === 'accepted'
          ? 'border-green-300 bg-green-50'
          : status === 'rejected'
          ? 'border-red-300 bg-red-50 opacity-70'
          : 'border-gray-200 bg-white'
      }`}
    >
      <div className="flex items-center gap-3 p-4">
        <div className="flex items-center justify-center w-8 h-8 rounded-full bg-indigo-100 text-indigo-700 font-bold text-sm flex-shrink-0">
          {index + 1}
        </div>
        <div className="flex-1 min-w-0">
          <p className="text-sm font-medium text-gray-900 truncate">{rec.text}</p>
        </div>
        <div className="flex items-center gap-2 flex-shrink-0">
          <PriorityBadge priority={rec.priority as 1 | 2 | 3} />
          <button
            onClick={() => setExpanded(!expanded)}
            className="p-1 text-gray-400 hover:text-gray-600"
          >
            {expanded ? (
              <ChevronUp className="w-4 h-4" />
            ) : (
              <ChevronDown className="w-4 h-4" />
            )}
          </button>
        </div>
      </div>

      {expanded && (
        <div className="px-4 pb-4 border-t border-gray-100">
          <p className="text-xs text-gray-500 mt-3 mb-3 italic">{rec.justification}</p>
          {!status && (
            <div className="flex gap-2">
              <Button
                size="sm"
                variant="success"
                leftIcon={<CheckCircle className="w-3.5 h-3.5" />}
                onClick={() => onAccept(rec.id)}
              >
                Aceptar
              </Button>
              <Button
                size="sm"
                variant="danger"
                leftIcon={<XCircle className="w-3.5 h-3.5" />}
                onClick={() => onReject(rec.id)}
              >
                Rechazar
              </Button>
            </div>
          )}
          {status === 'accepted' && (
            <div className="flex items-center gap-2 text-green-600 text-sm font-medium">
              <CheckCircle className="w-4 h-4" />
              Recomendación aceptada
            </div>
          )}
          {status === 'rejected' && (
            <div className="flex items-center gap-2 text-red-600 text-sm font-medium">
              <XCircle className="w-4 h-4" />
              Recomendación rechazada
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export const WhatIfPage: React.FC = () => {
  const [form, setForm] = useState<WhatIfForm>({
    name: '',
    description: '',
    stock_level: 50,
    demand_level: 'medio',
    risk_level: 'medio',
  });
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [result, setResult] = useState<Decision | null>(null);
  const [localStatus, setLocalStatus] = useState<Record<string, 'accepted' | 'rejected'>>({});
  const [notes, setNotes] = useState('');
  const [saved, setSaved] = useState(false);
  const { toasts, removeToast, success, error: toastError } = useToast();

  const handleAnalyze = async () => {
    if (!form.name.trim()) {
      toastError('Por favor ingresa un nombre para el escenario');
      return;
    }
    setIsAnalyzing(true);
    setResult(null);
    setLocalStatus({});
    setSaved(false);
    try {
      const req: WhatIfRequest = {
        name: form.name,
        description: form.description,
        stock_level: form.stock_level,
        demand_level: form.demand_level,
        risk_level: form.risk_level,
      };
      const decision = await decisionsService.analyzeWhatIf(req);
      setResult(decision);
    } catch (err: unknown) {
      const axiosErr = err as { response?: { data?: { detail?: string } } };
      toastError(axiosErr?.response?.data?.detail || 'Error al ejecutar el análisis');
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleAccept = (id: string) => {
    setLocalStatus((prev) => ({ ...prev, [id]: 'accepted' }));
  };

  const handleReject = (id: string) => {
    setLocalStatus((prev) => ({ ...prev, [id]: 'rejected' }));
  };

  const handleSave = async () => {
    if (!result) return;
    setIsSaving(true);
    try {
      await decisionsService.updateDecisionStatus(result.id, 'aceptada', notes);
      setSaved(true);
      success('Decisión guardada correctamente');
    } catch {
      toastError('Error al guardar la decisión');
    } finally {
      setIsSaving(false);
    }
  };

  const stockColor =
    form.stock_level < 25
      ? 'text-red-600'
      : form.stock_level < 50
      ? 'text-yellow-600'
      : 'text-green-600';

  return (
    <>
      <ToastContainer toasts={toasts} onRemove={removeToast} />
      <div className="grid grid-cols-1 lg:grid-cols-5 gap-6 h-full">
        {/* Left Panel - Configuration */}
        <div className="lg:col-span-2 space-y-5">
          <Card title="Configuración del Escenario" padding="md">
            <div className="space-y-4">
              <Input
                label="Nombre del Escenario"
                value={form.name}
                onChange={(e) => setForm({ ...form, name: e.target.value })}
                required
                placeholder="Ej. Escenario Q1 2025"
              />
              <Input
                label="Descripción (opcional)"
                value={form.description}
                onChange={(e) => setForm({ ...form, description: e.target.value })}
                placeholder="Descripción del escenario"
              />

              {/* Stock Level Slider */}
              <div>
                <div className="flex items-center justify-between mb-2">
                  <label className="block text-sm font-medium text-gray-700">
                    Nivel de Stock
                  </label>
                  <span className={`text-2xl font-bold ${stockColor}`}>
                    {form.stock_level}%
                  </span>
                </div>
                <input
                  type="range"
                  min="0"
                  max="100"
                  value={form.stock_level}
                  onChange={(e) =>
                    setForm({ ...form, stock_level: Number(e.target.value) })
                  }
                  className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-indigo-600"
                />
                <div className="flex justify-between text-xs text-gray-400 mt-1">
                  <span>Crítico (0%)</span>
                  <span>Óptimo (100%)</span>
                </div>
              </div>

              {/* Demand Level */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Nivel de Demanda
                </label>
                <div className="grid grid-cols-3 gap-2">
                  {(['bajo', 'medio', 'alto'] as Level[]).map((level) => (
                    <button
                      key={level}
                      type="button"
                      onClick={() => setForm({ ...form, demand_level: level })}
                      className={`py-2 px-3 rounded-lg border-2 text-sm font-medium transition-all ${
                        form.demand_level === level
                          ? levelColors[level]
                          : 'border-gray-200 bg-gray-50 text-gray-500 hover:border-gray-300'
                      }`}
                    >
                      {levelLabels[level]}
                    </button>
                  ))}
                </div>
              </div>

              {/* Risk Level */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Nivel de Riesgo
                </label>
                <div className="grid grid-cols-3 gap-2">
                  {(['bajo', 'medio', 'alto'] as Level[]).map((level) => (
                    <button
                      key={level}
                      type="button"
                      onClick={() => setForm({ ...form, risk_level: level })}
                      className={`py-2 px-3 rounded-lg border-2 text-sm font-medium transition-all ${
                        form.risk_level === level
                          ? levelColors[level]
                          : 'border-gray-200 bg-gray-50 text-gray-500 hover:border-gray-300'
                      }`}
                    >
                      {levelLabels[level]}
                    </button>
                  ))}
                </div>
              </div>

              <Button
                variant="primary"
                size="lg"
                className="w-full"
                isLoading={isAnalyzing}
                leftIcon={<Play className="w-4 h-4" />}
                onClick={handleAnalyze}
              >
                {isAnalyzing ? 'Analizando...' : 'Ejecutar Análisis'}
              </Button>
            </div>
          </Card>

          {/* Summary */}
          <Card title="Parámetros del Escenario" padding="md">
            <dl className="space-y-2">
              <div className="flex justify-between text-sm">
                <dt className="text-gray-500">Stock:</dt>
                <dd className={`font-semibold ${stockColor}`}>{form.stock_level}%</dd>
              </div>
              <div className="flex justify-between text-sm">
                <dt className="text-gray-500">Demanda:</dt>
                <dd className="font-semibold capitalize">{form.demand_level}</dd>
              </div>
              <div className="flex justify-between text-sm">
                <dt className="text-gray-500">Riesgo:</dt>
                <dd className="font-semibold capitalize">{form.risk_level}</dd>
              </div>
            </dl>
          </Card>
        </div>

        {/* Right Panel - Results */}
        <div className="lg:col-span-3">
          {isAnalyzing ? (
            <Card padding="md">
              <div className="flex flex-col items-center justify-center py-16">
                <Spinner size="xl" />
                <p className="text-gray-500 mt-4">Ejecutando motor de inferencia...</p>
                <p className="text-gray-400 text-sm mt-1">
                  Evaluando reglas de conocimiento
                </p>
              </div>
            </Card>
          ) : result === null ? (
            <Card padding="md">
              <div className="flex flex-col items-center justify-center py-16 text-center">
                <div className="w-16 h-16 bg-indigo-50 rounded-full flex items-center justify-center mb-4">
                  <Play className="w-8 h-8 text-indigo-400" />
                </div>
                <h3 className="text-gray-700 font-medium text-lg">
                  Configura y ejecuta el análisis
                </h3>
                <p className="text-gray-400 text-sm mt-2 max-w-sm">
                  Ajusta los parámetros del escenario en el panel izquierdo y presiona
                  "Ejecutar Análisis" para obtener recomendaciones del sistema experto.
                </p>
              </div>
            </Card>
          ) : (
            <div className="space-y-4">
              {/* Scenario Summary */}
              <Card padding="md">
                <div className="flex items-start gap-3">
                  <div className="p-2 bg-indigo-50 rounded-lg">
                    <AlertCircle className="w-5 h-5 text-indigo-600" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-gray-900">
                      Escenario Analizado
                    </h3>
                    <p className="text-sm text-gray-500 mt-0.5">
                      {result.scenario?.name}
                    </p>
                    <div className="flex gap-4 mt-2 text-xs text-gray-600">
                      <span>Stock: <strong>{result.scenario?.stock_level}%</strong></span>
                      <span>Demanda: <strong className="capitalize">{result.scenario?.demand_level}</strong></span>
                      <span>Riesgo: <strong className="capitalize">{result.scenario?.risk_level}</strong></span>
                    </div>
                  </div>
                </div>
              </Card>

              {/* Recommendations */}
              <div>
                <h3 className="text-sm font-semibold text-gray-700 mb-3">
                  Recomendaciones ({result.recommendations?.length ?? 0})
                  {result.rules_fired?.length > 0 && (
                    <span className="ml-2 text-xs font-normal text-gray-400">
                      — {result.rules_fired.length} regla(s) activada(s)
                    </span>
                  )}
                </h3>

                {!result.recommendations || result.recommendations.length === 0 ? (
                  <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6 text-center">
                    <AlertCircle className="w-8 h-8 text-yellow-500 mx-auto mb-2" />
                    <p className="text-yellow-700 font-medium">
                      No se encontraron reglas aplicables
                    </p>
                    <p className="text-yellow-600 text-sm mt-1">
                      Ninguna regla activa coincide con los parámetros del escenario.
                      Verifica la base de conocimiento.
                    </p>
                  </div>
                ) : (
                  <div className="space-y-3">
                    {[...result.recommendations]
                      .sort((a, b) => a.priority - b.priority)
                      .map((rec, idx) => (
                        <RecommendationCard
                          key={rec.id}
                          rec={rec}
                          index={idx}
                          onAccept={handleAccept}
                          onReject={handleReject}
                          localStatus={localStatus}
                        />
                      ))}
                  </div>
                )}
              </div>

              {/* Notes + Save */}
              {result.recommendations && result.recommendations.length > 0 && !saved && (
                <Card padding="md">
                  <Textarea
                    label="Notas de la Decisión"
                    value={notes}
                    onChange={(e) => setNotes(e.target.value)}
                    placeholder="Agrega notas o justificaciones adicionales..."
                  />
                  <div className="mt-4">
                    <Button
                      variant="primary"
                      leftIcon={<Save className="w-4 h-4" />}
                      isLoading={isSaving}
                      onClick={handleSave}
                      className="w-full"
                    >
                      Guardar Decisión
                    </Button>
                  </div>
                </Card>
              )}

              {saved && (
                <div className="flex items-center gap-3 bg-green-50 border border-green-200 rounded-lg p-4">
                  <CheckCircle className="w-5 h-5 text-green-600 flex-shrink-0" />
                  <div>
                    <p className="text-green-800 font-medium">Decisión guardada correctamente</p>
                    <p className="text-green-600 text-sm">
                      Puedes encontrarla en la sección de Decisiones
                    </p>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </>
  );
};
