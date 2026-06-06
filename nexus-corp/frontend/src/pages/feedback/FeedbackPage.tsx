import React, { useEffect, useState, useCallback } from 'react';
import { Plus, MessageSquare, Star } from 'lucide-react';
import { Feedback, Decision } from '../../types';
import { feedbackService, CreateFeedbackDto } from '../../services/feedback.service';
import { decisionsService } from '../../services/decisions.service';
import { Button } from '../../components/ui/Button';
import { Select } from '../../components/ui/Select';
import { Modal } from '../../components/ui/Modal';
import { StatCard } from '../../components/ui/Card';
import { Spinner } from '../../components/ui/Spinner';
import { StarRating } from '../../components/ui/StarRating';
import { useToast } from '../../hooks/useToast';
import { ToastContainer } from '../../components/ui/Toast';
import { Textarea } from '../../components/ui/Input';

export const FeedbackPage: React.FC = () => {
  const [feedbackList, setFeedbackList] = useState<Feedback[]>([]);
  const [decisions, setDecisions] = useState<Decision[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [formData, setFormData] = useState({ decision_id: '', rating: 0, comment: '' });
  const [isSaving, setIsSaving] = useState(false);
  const { toasts, removeToast, success, error: toastError } = useToast();

  const stats = {
    total: feedbackList.length,
    avgRating:
      feedbackList.length > 0
        ? feedbackList.reduce((s, f) => s + f.rating, 0) / feedbackList.length
        : 0,
    fiveStarCount: feedbackList.filter((f) => f.rating === 5).length,
    oneStarCount: feedbackList.filter((f) => f.rating === 1).length,
  };

  const loadData = useCallback(async () => {
    try {
      const [fbRes, decRes] = await Promise.all([
        feedbackService.getFeedback(),
        decisionsService.getDecisions({ size: 100 }),
      ]);
      setFeedbackList(fbRes.items);
      setDecisions(decRes.items);
    } catch {
      toastError('Error al cargar los datos');
    } finally {
      setIsLoading(false);
    }
  }, [toastError]);

  useEffect(() => {
    loadData();
  }, [loadData]);

  const openModal = () => {
    setFormData({ decision_id: '', rating: 0, comment: '' });
    setShowModal(true);
  };

  const handleSubmit = async () => {
    if (!formData.decision_id) {
      toastError('Selecciona una decisión');
      return;
    }
    if (formData.rating === 0) {
      toastError('Selecciona una calificación');
      return;
    }
    setIsSaving(true);
    try {
      const data: CreateFeedbackDto = {
        decision_id: formData.decision_id,
        rating: formData.rating,
        comment: formData.comment,
      };
      await feedbackService.createFeedback(data);
      success('Retroalimentación guardada correctamente');
      setShowModal(false);
      loadData();
    } catch (err: unknown) {
      const axiosErr = err as { response?: { data?: { detail?: string } } };
      toastError(axiosErr?.response?.data?.detail || 'Error al guardar el feedback');
    } finally {
      setIsSaving(false);
    }
  };

  const getDecisionLabel = (id: string) => {
    const d = decisions.find((d) => d.id === id);
    return d?.scenario?.name || `Decisión ${id.slice(0, 8)}`;
  };

  const ratingLabel = ['', 'Muy malo', 'Malo', 'Regular', 'Bueno', 'Excelente'];

  return (
    <>
      <ToastContainer toasts={toasts} onRemove={removeToast} />
      <div className="space-y-6">
        <div className="flex items-center justify-between flex-wrap gap-3">
          <div>
            <h2 className="text-xl font-semibold text-gray-900">Retroalimentación</h2>
            <p className="text-sm text-gray-500 mt-1">
              Opiniones y calificaciones sobre las decisiones del sistema
            </p>
          </div>
          <Button
            variant="primary"
            leftIcon={<Plus className="w-4 h-4" />}
            onClick={openModal}
          >
            Agregar Feedback
          </Button>
        </div>

        {/* Summary Cards */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <StatCard
            title="Total Feedback"
            value={stats.total}
            icon={<MessageSquare className="w-6 h-6" />}
            color="indigo"
          />
          <StatCard
            title="Calificación Promedio"
            value={`${stats.avgRating.toFixed(1)} / 5`}
            icon={<Star className="w-6 h-6" />}
            color="yellow"
          />
          <StatCard
            title="5 Estrellas"
            value={stats.fiveStarCount}
            icon={<Star className="w-6 h-6" />}
            color="green"
          />
          <StatCard
            title="1 Estrella"
            value={stats.oneStarCount}
            icon={<Star className="w-6 h-6" />}
            color="red"
          />
        </div>

        {/* Rating Distribution */}
        {feedbackList.length > 0 && (
          <div className="bg-white rounded-lg border border-gray-200 shadow-sm p-5">
            <h3 className="text-sm font-semibold text-gray-700 mb-4">
              Distribución de Calificaciones
            </h3>
            <div className="space-y-2">
              {[5, 4, 3, 2, 1].map((rating) => {
                const count = feedbackList.filter((f) => f.rating === rating).length;
                const pct = stats.total > 0 ? (count / stats.total) * 100 : 0;
                return (
                  <div key={rating} className="flex items-center gap-3">
                    <div className="flex items-center gap-1 w-20 flex-shrink-0">
                      <span className="text-sm text-gray-600">{rating}</span>
                      <Star className="w-3.5 h-3.5 text-yellow-400 fill-yellow-400" />
                    </div>
                    <div className="flex-1 bg-gray-100 rounded-full h-2.5">
                      <div
                        className="bg-yellow-400 h-2.5 rounded-full transition-all duration-300"
                        style={{ width: `${pct}%` }}
                      />
                    </div>
                    <span className="text-sm text-gray-500 w-12 text-right">
                      {count} ({pct.toFixed(0)}%)
                    </span>
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {/* Table */}
        <div className="bg-white rounded-lg border border-gray-200 shadow-sm overflow-hidden">
          {isLoading ? (
            <div className="flex justify-center py-16">
              <Spinner size="lg" />
            </div>
          ) : feedbackList.length === 0 ? (
            <div className="text-center py-16">
              <MessageSquare className="w-12 h-12 text-gray-300 mx-auto mb-3" />
              <p className="text-gray-500">No hay retroalimentación registrada</p>
              <p className="text-gray-400 text-sm mt-1">
                Agrega la primera calificación haciendo clic en "Agregar Feedback"
              </p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    {['Decisión', 'Calificación', 'Descripción', 'Comentario', 'Fecha'].map(
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
                  {feedbackList.map((fb, idx) => (
                    <tr
                      key={fb.id}
                      className={`hover:bg-gray-50 transition-colors ${idx % 2 === 1 ? 'bg-gray-50/50' : ''}`}
                    >
                      <td className="px-4 py-3 text-sm font-medium text-gray-900 max-w-[200px] truncate">
                        {getDecisionLabel(fb.decision_id)}
                      </td>
                      <td className="px-4 py-3">
                        <StarRating value={fb.rating} readonly size="sm" />
                      </td>
                      <td className="px-4 py-3 text-sm text-gray-600">
                        {ratingLabel[fb.rating] || '—'}
                      </td>
                      <td className="px-4 py-3 text-sm text-gray-600 max-w-[200px] truncate">
                        {fb.comment || <span className="text-gray-400 italic">Sin comentario</span>}
                      </td>
                      <td className="px-4 py-3 text-sm text-gray-500 whitespace-nowrap">
                        {new Date(fb.created_at).toLocaleDateString('es-GT', {
                          day: '2-digit',
                          month: 'short',
                          year: 'numeric',
                        })}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>

      <Modal
        isOpen={showModal}
        onClose={() => setShowModal(false)}
        title="Agregar Retroalimentación"
        size="md"
        footer={
          <div className="flex justify-end gap-3">
            <Button variant="secondary" onClick={() => setShowModal(false)}>
              Cancelar
            </Button>
            <Button
              variant="primary"
              isLoading={isSaving}
              onClick={handleSubmit}
            >
              Guardar
            </Button>
          </div>
        }
      >
        <div className="space-y-4">
          <Select
            label="Decisión"
            value={formData.decision_id}
            onChange={(e) => setFormData({ ...formData, decision_id: e.target.value })}
            options={decisions.map((d) => ({
              value: d.id,
              label: d.scenario?.name || `Decisión ${d.id.slice(0, 8)}`,
            }))}
            placeholder="Selecciona una decisión"
            required
          />

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Calificación <span className="text-red-500">*</span>
            </label>
            <StarRating
              value={formData.rating}
              onChange={(r) => setFormData({ ...formData, rating: r })}
              size="lg"
            />
            {formData.rating > 0 && (
              <p className="text-sm text-gray-500 mt-1">
                {ratingLabel[formData.rating]}
              </p>
            )}
          </div>

          <Textarea
            label="Comentario"
            value={formData.comment}
            onChange={(e) => setFormData({ ...formData, comment: e.target.value })}
            placeholder="Comparte tu experiencia con esta decisión..."
          />
        </div>
      </Modal>
    </>
  );
};
