import React, { useEffect, useState, useCallback } from 'react';
import { Eye, FileText, MessageSquare } from 'lucide-react';
import { Decision, Recommendation } from '../../types';
import { decisionsService } from '../../services/decisions.service';
import { feedbackService, CreateFeedbackDto } from '../../services/feedback.service';
import { Button } from '../../components/ui/Button';
import { Select } from '../../components/ui/Select';
import { Modal } from '../../components/ui/Modal';
import { Badge, PriorityBadge } from '../../components/ui/Badge';
import { Spinner } from '../../components/ui/Spinner';
import { StarRating } from '../../components/ui/StarRating';
import { useToast } from '../../hooks/useToast';
import { ToastContainer } from '../../components/ui/Toast';
import { Textarea } from '../../components/ui/Input';

const statusVariant = (status: string) => {
  if (status === 'aceptada') return 'success';
  if (status === 'rechazada') return 'danger';
  return 'warning';
};

const statusLabel = (status: string) => {
  if (status === 'aceptada') return 'Aceptada';
  if (status === 'rechazada') return 'Rechazada';
  return 'Pendiente';
};

export const DecisionsPage: React.FC = () => {
  const [decisions, setDecisions] = useState<Decision[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [statusFilter, setStatusFilter] = useState('');
  const [selectedDecision, setSelectedDecision] = useState<Decision | null>(null);
  const [showDetail, setShowDetail] = useState(false);
  const [showFeedback, setShowFeedback] = useState(false);
  const [feedbackForm, setFeedbackForm] = useState({ rating: 0, comment: '' });
  const [isSavingFeedback, setIsSavingFeedback] = useState(false);
  const { toasts, removeToast, success, error: toastError } = useToast();

  const loadDecisions = useCallback(async () => {
    setIsLoading(true);
    try {
      const params: { status?: string } = {};
      if (statusFilter) params.status = statusFilter;
      const data = await decisionsService.getDecisions(params);
      setDecisions(data.items);
    } catch {
      toastError('Error al cargar las decisiones');
    } finally {
      setIsLoading(false);
    }
  }, [statusFilter, toastError]);

  useEffect(() => {
    loadDecisions();
  }, [loadDecisions]);

  const openDetail = (decision: Decision) => {
    setSelectedDecision(decision);
    setShowDetail(true);
  };

  const openFeedback = (decision: Decision) => {
    setSelectedDecision(decision);
    setFeedbackForm({ rating: 0, comment: '' });
    setShowFeedback(true);
    setShowDetail(false);
  };

  const handleSaveFeedback = async () => {
    if (!selectedDecision) return;
    if (feedbackForm.rating === 0) {
      toastError('Por favor selecciona una calificación');
      return;
    }
    setIsSavingFeedback(true);
    try {
      const data: CreateFeedbackDto = {
        decision_id: selectedDecision.id,
        rating: feedbackForm.rating,
        comment: feedbackForm.comment,
      };
      await feedbackService.createFeedback(data);
      success('Retroalimentación guardada correctamente');
      setShowFeedback(false);
    } catch {
      toastError('Error al guardar la retroalimentación');
    } finally {
      setIsSavingFeedback(false);
    }
  };

  const RecDetail: React.FC<{ rec: Recommendation }> = ({ rec }) => (
    <div className="border border-gray-200 rounded-lg p-3 space-y-2">
      <div className="flex items-center gap-2">
        <PriorityBadge priority={rec.priority as 1 | 2 | 3} />
        <span className="text-sm font-medium text-gray-900 flex-1">{rec.text}</span>
        <Badge variant={rec.is_accepted ? 'success' : 'gray'} size="sm">
          {rec.is_accepted ? 'Aceptada' : 'Pendiente'}
        </Badge>
      </div>
      {rec.justification && (
        <p className="text-xs text-gray-500 italic pl-1">{rec.justification}</p>
      )}
    </div>
  );

  return (
    <>
      <ToastContainer toasts={toasts} onRemove={removeToast} />
      <div className="space-y-6">
        <div className="flex items-center justify-between flex-wrap gap-3">
          <div>
            <h2 className="text-xl font-semibold text-gray-900">Historial de Decisiones</h2>
            <p className="text-sm text-gray-500 mt-1">
              Registro de todas las decisiones generadas por el sistema
            </p>
          </div>
        </div>

        {/* Filters */}
        <div className="bg-white p-4 rounded-lg border border-gray-200 flex items-center gap-4">
          <Select
            label="Estado"
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            options={[
              { value: '', label: 'Todos los estados' },
              { value: 'pendiente', label: 'Pendiente' },
              { value: 'aceptada', label: 'Aceptada' },
              { value: 'rechazada', label: 'Rechazada' },
            ]}
          />
          <div className="pt-5">
            <span className="text-sm text-gray-500">
              {decisions.length} decisión(es) encontrada(s)
            </span>
          </div>
        </div>

        <div className="bg-white rounded-lg border border-gray-200 shadow-sm overflow-hidden">
          {isLoading ? (
            <div className="flex justify-center py-16">
              <Spinner size="lg" />
            </div>
          ) : decisions.length === 0 ? (
            <div className="text-center py-16">
              <FileText className="w-12 h-12 text-gray-300 mx-auto mb-3" />
              <p className="text-gray-500">No hay decisiones registradas</p>
              <p className="text-gray-400 text-sm mt-1">
                Ejecuta un análisis What-If para generar tu primera decisión
              </p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    {['Fecha', 'Escenario', 'Parámetros', 'Recomendaciones', 'Estado', 'Acciones'].map(
                      (h) => (
                        <th
                          key={h}
                          className="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider"
                        >
                          {h}
                        </th>
                      )
                    )}
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200">
                  {decisions.map((decision, idx) => (
                    <tr
                      key={decision.id}
                      className={`hover:bg-gray-50 transition-colors ${idx % 2 === 1 ? 'bg-gray-50/50' : ''}`}
                    >
                      <td className="px-4 py-3 text-sm text-gray-600 whitespace-nowrap">
                        {new Date(decision.created_at).toLocaleDateString('es-GT', {
                          day: '2-digit',
                          month: 'short',
                          year: 'numeric',
                          hour: '2-digit',
                          minute: '2-digit',
                        })}
                      </td>
                      <td className="px-4 py-3 text-sm font-medium text-gray-900">
                        {decision.scenario?.name || `—`}
                      </td>
                      <td className="px-4 py-3 text-xs text-gray-500">
                        {decision.scenario ? (
                          <div className="space-y-0.5">
                            <div>Stock: <strong>{decision.scenario.stock_level}%</strong></div>
                            <div>Demanda: <strong className="capitalize">{decision.scenario.demand_level}</strong></div>
                            <div>Riesgo: <strong className="capitalize">{decision.scenario.risk_level}</strong></div>
                          </div>
                        ) : '—'}
                      </td>
                      <td className="px-4 py-3 text-sm text-gray-600">
                        <span className="inline-flex items-center gap-1">
                          <span className="font-semibold">
                            {decision.recommendations?.length ?? 0}
                          </span>
                          recomendación(es)
                        </span>
                      </td>
                      <td className="px-4 py-3">
                        <Badge variant={statusVariant(decision.status)}>
                          {statusLabel(decision.status)}
                        </Badge>
                      </td>
                      <td className="px-4 py-3">
                        <div className="flex items-center gap-2">
                          <Button
                            size="sm"
                            variant="ghost"
                            leftIcon={<Eye className="w-3.5 h-3.5" />}
                            onClick={() => openDetail(decision)}
                          >
                            Ver
                          </Button>
                          <Button
                            size="sm"
                            variant="secondary"
                            leftIcon={<MessageSquare className="w-3.5 h-3.5" />}
                            onClick={() => openFeedback(decision)}
                          >
                            Feedback
                          </Button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>

      {/* Detail Modal */}
      <Modal
        isOpen={showDetail}
        onClose={() => setShowDetail(false)}
        title="Detalle de Decisión"
        size="xl"
        footer={
          <div className="flex justify-between gap-3">
            <Button
              variant="secondary"
              leftIcon={<MessageSquare className="w-4 h-4" />}
              onClick={() => selectedDecision && openFeedback(selectedDecision)}
            >
              Agregar Feedback
            </Button>
            <Button variant="primary" onClick={() => setShowDetail(false)}>
              Cerrar
            </Button>
          </div>
        }
      >
        {selectedDecision && (
          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-4 p-4 bg-gray-50 rounded-lg">
              <div>
                <p className="text-xs text-gray-500 uppercase font-semibold tracking-wider">
                  Escenario
                </p>
                <p className="text-sm font-medium text-gray-900 mt-1">
                  {selectedDecision.scenario?.name || '—'}
                </p>
              </div>
              <div>
                <p className="text-xs text-gray-500 uppercase font-semibold tracking-wider">
                  Estado
                </p>
                <div className="mt-1">
                  <Badge variant={statusVariant(selectedDecision.status)}>
                    {statusLabel(selectedDecision.status)}
                  </Badge>
                </div>
              </div>
              <div>
                <p className="text-xs text-gray-500 uppercase font-semibold tracking-wider">
                  Parámetros
                </p>
                {selectedDecision.scenario && (
                  <div className="text-sm text-gray-700 mt-1 space-y-0.5">
                    <p>Stock: <strong>{selectedDecision.scenario.stock_level}%</strong></p>
                    <p>Demanda: <strong className="capitalize">{selectedDecision.scenario.demand_level}</strong></p>
                    <p>Riesgo: <strong className="capitalize">{selectedDecision.scenario.risk_level}</strong></p>
                  </div>
                )}
              </div>
              <div>
                <p className="text-xs text-gray-500 uppercase font-semibold tracking-wider">
                  Fecha
                </p>
                <p className="text-sm text-gray-700 mt-1">
                  {new Date(selectedDecision.created_at).toLocaleDateString('es-GT', {
                    day: '2-digit',
                    month: 'long',
                    year: 'numeric',
                  })}
                </p>
              </div>
            </div>

            {selectedDecision.notes && (
              <div>
                <p className="text-xs text-gray-500 uppercase font-semibold tracking-wider mb-1">
                  Notas
                </p>
                <p className="text-sm text-gray-700 bg-gray-50 rounded p-3">
                  {selectedDecision.notes}
                </p>
              </div>
            )}

            <div>
              <p className="text-xs text-gray-500 uppercase font-semibold tracking-wider mb-2">
                Recomendaciones ({selectedDecision.recommendations?.length ?? 0})
              </p>
              {selectedDecision.recommendations?.length > 0 ? (
                <div className="space-y-2">
                  {[...selectedDecision.recommendations]
                    .sort((a, b) => a.priority - b.priority)
                    .map((rec) => (
                      <RecDetail key={rec.id} rec={rec} />
                    ))}
                </div>
              ) : (
                <p className="text-sm text-gray-500 text-center py-4">
                  No hay recomendaciones para esta decisión
                </p>
              )}
            </div>
          </div>
        )}
      </Modal>

      {/* Feedback Modal */}
      <Modal
        isOpen={showFeedback}
        onClose={() => setShowFeedback(false)}
        title="Agregar Retroalimentación"
        size="md"
        footer={
          <div className="flex justify-end gap-3">
            <Button variant="secondary" onClick={() => setShowFeedback(false)}>
              Cancelar
            </Button>
            <Button
              variant="primary"
              isLoading={isSavingFeedback}
              onClick={handleSaveFeedback}
            >
              Guardar Feedback
            </Button>
          </div>
        }
      >
        <div className="space-y-4">
          {selectedDecision && (
            <div className="p-3 bg-gray-50 rounded-lg">
              <p className="text-sm text-gray-500">Decisión:</p>
              <p className="text-sm font-medium text-gray-900">
                {selectedDecision.scenario?.name || `Decisión ${selectedDecision.id.slice(0, 8)}`}
              </p>
            </div>
          )}

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Calificación <span className="text-red-500">*</span>
            </label>
            <StarRating
              value={feedbackForm.rating}
              onChange={(r) => setFeedbackForm({ ...feedbackForm, rating: r })}
              size="lg"
            />
            {feedbackForm.rating > 0 && (
              <p className="text-sm text-gray-500 mt-1">
                {['', 'Muy malo', 'Malo', 'Regular', 'Bueno', 'Excelente'][feedbackForm.rating]}
              </p>
            )}
          </div>

          <Textarea
            label="Comentario"
            value={feedbackForm.comment}
            onChange={(e) =>
              setFeedbackForm({ ...feedbackForm, comment: e.target.value })
            }
            placeholder="Describe tu experiencia con esta decisión..."
          />
        </div>
      </Modal>
    </>
  );
};
