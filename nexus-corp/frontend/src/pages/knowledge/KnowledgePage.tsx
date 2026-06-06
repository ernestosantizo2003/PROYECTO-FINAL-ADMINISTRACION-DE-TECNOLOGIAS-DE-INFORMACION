import React, { useEffect, useState, useCallback } from 'react';
import { Plus, Edit, Trash2, BookOpen, ToggleLeft, ToggleRight } from 'lucide-react';
import { KnowledgeRule } from '../../types';
import { rulesService, CreateRuleDto } from '../../services/rules.service';
import { Button } from '../../components/ui/Button';
import { Input, Textarea } from '../../components/ui/Input';
import { Select } from '../../components/ui/Select';
import { Modal } from '../../components/ui/Modal';
import { Badge, PriorityBadge } from '../../components/ui/Badge';
import { Spinner } from '../../components/ui/Spinner';
import { useToast } from '../../hooks/useToast';
import { ToastContainer } from '../../components/ui/Toast';
import { useAuth } from '../../hooks/useAuth';

type DemandRisk = 'bajo' | 'medio' | 'alto';
type Operator = '<' | '<=' | '>' | '>=' | '==' | '!=';

interface ConditionRow {
  enabled: boolean;
  operator: Operator | string;
  value: string;
}

interface ConditionBuilder {
  stock_level: ConditionRow;
  demand_level: ConditionRow;
  risk_level: ConditionRow;
}

const defaultConditions: ConditionBuilder = {
  stock_level: { enabled: false, operator: '<', value: '30' },
  demand_level: { enabled: false, operator: '==', value: 'alto' },
  risk_level: { enabled: false, operator: '==', value: 'alto' },
};

interface RuleFormData {
  name: string;
  description: string;
  category: string;
  priority: '1' | '2' | '3';
  action: string;
  is_active: boolean;
  conditions: ConditionBuilder;
}

const emptyForm: RuleFormData = {
  name: '',
  description: '',
  category: '',
  priority: '2',
  action: '',
  is_active: true,
  conditions: { ...defaultConditions },
};

const categoryOptions = [
  { value: 'inventario', label: 'Inventario' },
  { value: 'logistica', label: 'Logística' },
  { value: 'riesgo', label: 'Riesgo' },
  { value: 'demanda', label: 'Demanda' },
];

const priorityOptions = [
  { value: '1', label: 'Alta (1)' },
  { value: '2', label: 'Media (2)' },
  { value: '3', label: 'Baja (3)' },
];

const numericOperatorOptions = [
  { value: '<', label: '<' },
  { value: '<=', label: '<=' },
  { value: '>', label: '>' },
  { value: '>=', label: '>=' },
  { value: '==', label: '==' },
  { value: '!=', label: '!=' },
];

const levelOperatorOptions = [
  { value: '==', label: '==' },
  { value: '!=', label: '!=' },
];

const levelValueOptions: { value: DemandRisk; label: string }[] = [
  { value: 'bajo', label: 'Bajo' },
  { value: 'medio', label: 'Medio' },
  { value: 'alto', label: 'Alto' },
];

function ruleToConditionBuilder(
  conditions: Record<string, { operator: string; value: string | number }>
): ConditionBuilder {
  const cb: ConditionBuilder = {
    stock_level: { enabled: false, operator: '<', value: '30' },
    demand_level: { enabled: false, operator: '==', value: 'alto' },
    risk_level: { enabled: false, operator: '==', value: 'alto' },
  };
  if (conditions.stock_level) {
    cb.stock_level = {
      enabled: true,
      operator: conditions.stock_level.operator,
      value: String(conditions.stock_level.value),
    };
  }
  if (conditions.demand_level) {
    cb.demand_level = {
      enabled: true,
      operator: conditions.demand_level.operator,
      value: String(conditions.demand_level.value),
    };
  }
  if (conditions.risk_level) {
    cb.risk_level = {
      enabled: true,
      operator: conditions.risk_level.operator,
      value: String(conditions.risk_level.value),
    };
  }
  return cb;
}

function conditionBuilderToRecord(
  cb: ConditionBuilder
): Record<string, { operator: string; value: string | number }> {
  const result: Record<string, { operator: string; value: string | number }> = {};
  if (cb.stock_level.enabled) {
    result.stock_level = {
      operator: cb.stock_level.operator,
      value: Number(cb.stock_level.value),
    };
  }
  if (cb.demand_level.enabled) {
    result.demand_level = {
      operator: cb.demand_level.operator,
      value: cb.demand_level.value,
    };
  }
  if (cb.risk_level.enabled) {
    result.risk_level = {
      operator: cb.risk_level.operator,
      value: cb.risk_level.value,
    };
  }
  return result;
}

export const KnowledgePage: React.FC = () => {
  const [rules, setRules] = useState<KnowledgeRule[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [editingRule, setEditingRule] = useState<KnowledgeRule | null>(null);
  const [formData, setFormData] = useState<RuleFormData>(emptyForm);
  const [isSaving, setIsSaving] = useState(false);
  const [deleteConfirm, setDeleteConfirm] = useState<string | null>(null);
  const [filterCategory, setFilterCategory] = useState('');
  const [filterActive, setFilterActive] = useState('');
  const { toasts, removeToast, success, error: toastError } = useToast();
  const { hasRole } = useAuth();

  const canEdit = hasRole(['admin_conocimiento', 'admin_sistema']);

  const loadRules = useCallback(async () => {
    setIsLoading(true);
    try {
      const params: { category?: string; is_active?: boolean } = {};
      if (filterCategory) params.category = filterCategory;
      if (filterActive !== '') params.is_active = filterActive === 'true';
      const data = await rulesService.getRules(params);
      setRules(data.items);
    } catch {
      toastError('Error al cargar las reglas');
    } finally {
      setIsLoading(false);
    }
  }, [filterCategory, filterActive, toastError]);

  useEffect(() => {
    loadRules();
  }, [loadRules]);

  const openCreateModal = () => {
    setEditingRule(null);
    setFormData({ ...emptyForm, conditions: { ...defaultConditions } });
    setShowModal(true);
  };

  const openEditModal = (rule: KnowledgeRule) => {
    setEditingRule(rule);
    setFormData({
      name: rule.name,
      description: rule.description,
      category: rule.category,
      priority: String(rule.priority) as '1' | '2' | '3',
      action: rule.action,
      is_active: rule.is_active,
      conditions: ruleToConditionBuilder(rule.conditions),
    });
    setShowModal(true);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!formData.name || !formData.category || !formData.action) {
      toastError('Por favor completa los campos requeridos');
      return;
    }
    const builtConditions = conditionBuilderToRecord(formData.conditions);
    if (Object.keys(builtConditions).length === 0) {
      toastError('Debes habilitar al menos una condición');
      return;
    }

    setIsSaving(true);
    try {
      const payload: CreateRuleDto = {
        name: formData.name,
        description: formData.description,
        category: formData.category,
        priority: Number(formData.priority) as 1 | 2 | 3,
        action: formData.action,
        is_active: formData.is_active,
        conditions: builtConditions,
      };
      if (editingRule) {
        await rulesService.updateRule(editingRule.id, payload);
        success('Regla actualizada correctamente');
      } else {
        await rulesService.createRule(payload);
        success('Regla creada correctamente');
      }
      setShowModal(false);
      loadRules();
    } catch (err: unknown) {
      const axiosErr = err as { response?: { data?: { detail?: string } } };
      toastError(axiosErr?.response?.data?.detail || 'Error al guardar la regla');
    } finally {
      setIsSaving(false);
    }
  };

  const handleDelete = async (id: string) => {
    try {
      await rulesService.deleteRule(id);
      success('Regla eliminada correctamente');
      setDeleteConfirm(null);
      loadRules();
    } catch {
      toastError('Error al eliminar la regla');
    }
  };

  const handleToggle = async (rule: KnowledgeRule) => {
    try {
      await rulesService.toggleRule(rule.id, !rule.is_active);
      success(`Regla ${rule.is_active ? 'desactivada' : 'activada'}`);
      loadRules();
    } catch {
      toastError('Error al cambiar estado de la regla');
    }
  };

  const formatConditions = (
    conditions: Record<string, { operator: string; value: string | number }>
  ) => {
    return Object.entries(conditions)
      .map(([k, v]) => `${k} ${v.operator} ${v.value}`)
      .join(', ');
  };

  const updateCondition = (
    field: keyof ConditionBuilder,
    key: keyof ConditionRow,
    val: string | boolean
  ) => {
    setFormData((prev) => ({
      ...prev,
      conditions: {
        ...prev.conditions,
        [field]: { ...prev.conditions[field], [key]: val },
      },
    }));
  };

  return (
    <>
      <ToastContainer toasts={toasts} onRemove={removeToast} />
      <div className="space-y-6">
        <div className="flex items-center justify-between flex-wrap gap-3">
          <div>
            <h2 className="text-xl font-semibold text-gray-900">Base de Conocimiento</h2>
            <p className="text-sm text-gray-500 mt-1">
              Gestiona las reglas de inferencia del sistema experto
            </p>
          </div>
          {canEdit && (
            <Button
              variant="primary"
              leftIcon={<Plus className="w-4 h-4" />}
              onClick={openCreateModal}
            >
              Nueva Regla
            </Button>
          )}
        </div>

        {/* Filters */}
        <div className="flex flex-wrap gap-3 items-center bg-white p-4 rounded-lg border border-gray-200">
          <Select
            options={[{ value: '', label: 'Todas las categorías' }, ...categoryOptions]}
            value={filterCategory}
            onChange={(e) => setFilterCategory(e.target.value)}
            label="Categoría"
          />
          <Select
            options={[
              { value: '', label: 'Todos los estados' },
              { value: 'true', label: 'Activas' },
              { value: 'false', label: 'Inactivas' },
            ]}
            value={filterActive}
            onChange={(e) => setFilterActive(e.target.value)}
            label="Estado"
          />
        </div>

        <div className="bg-white rounded-lg border border-gray-200 shadow-sm overflow-hidden">
          {isLoading ? (
            <div className="flex justify-center py-16">
              <Spinner size="lg" />
            </div>
          ) : rules.length === 0 ? (
            <div className="text-center py-16">
              <BookOpen className="w-12 h-12 text-gray-300 mx-auto mb-3" />
              <p className="text-gray-500">No hay reglas que coincidan con los filtros</p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    {['Nombre', 'Categoría', 'Prioridad', 'Condiciones', 'Acción', 'Estado', 'Acciones'].map(
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
                  {rules.map((rule, idx) => (
                    <tr
                      key={rule.id}
                      className={`hover:bg-gray-50 transition-colors ${idx % 2 === 1 ? 'bg-gray-50/50' : ''}`}
                    >
                      <td className="px-4 py-3 text-sm font-medium text-gray-900">
                        <div>
                          <p className="font-medium">{rule.name}</p>
                          {rule.description && (
                            <p className="text-xs text-gray-500 mt-0.5 truncate max-w-xs">
                              {rule.description}
                            </p>
                          )}
                        </div>
                      </td>
                      <td className="px-4 py-3">
                        <Badge variant="indigo">{rule.category}</Badge>
                      </td>
                      <td className="px-4 py-3">
                        <PriorityBadge priority={rule.priority} />
                      </td>
                      <td className="px-4 py-3 text-xs text-gray-500 max-w-[200px] truncate font-mono">
                        {formatConditions(rule.conditions)}
                      </td>
                      <td className="px-4 py-3 text-sm text-gray-700 max-w-[180px] truncate">
                        {rule.action}
                      </td>
                      <td className="px-4 py-3">
                        <Badge variant={rule.is_active ? 'success' : 'gray'}>
                          {rule.is_active ? 'Activa' : 'Inactiva'}
                        </Badge>
                      </td>
                      <td className="px-4 py-3">
                        <div className="flex items-center gap-1">
                          {canEdit && (
                            <>
                              <button
                                onClick={() => handleToggle(rule)}
                                className="p-1.5 rounded text-gray-400 hover:text-indigo-600 hover:bg-indigo-50 transition-colors"
                                title={rule.is_active ? 'Desactivar' : 'Activar'}
                              >
                                {rule.is_active ? (
                                  <ToggleRight className="w-4 h-4" />
                                ) : (
                                  <ToggleLeft className="w-4 h-4" />
                                )}
                              </button>
                              <button
                                onClick={() => openEditModal(rule)}
                                className="p-1.5 rounded text-gray-400 hover:text-blue-600 hover:bg-blue-50 transition-colors"
                                title="Editar"
                              >
                                <Edit className="w-4 h-4" />
                              </button>
                              <button
                                onClick={() => setDeleteConfirm(rule.id)}
                                className="p-1.5 rounded text-gray-400 hover:text-red-600 hover:bg-red-50 transition-colors"
                                title="Eliminar"
                              >
                                <Trash2 className="w-4 h-4" />
                              </button>
                            </>
                          )}
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

      {/* Create/Edit Modal */}
      <Modal
        isOpen={showModal}
        onClose={() => setShowModal(false)}
        title={editingRule ? 'Editar Regla' : 'Nueva Regla de Conocimiento'}
        size="2xl"
        footer={
          <div className="flex justify-end gap-3">
            <Button variant="secondary" onClick={() => setShowModal(false)}>
              Cancelar
            </Button>
            <Button variant="primary" isLoading={isSaving} onClick={handleSubmit}>
              {editingRule ? 'Actualizar' : 'Crear Regla'}
            </Button>
          </div>
        }
      >
        <form onSubmit={handleSubmit} className="space-y-5">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <Input
              label="Nombre"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              required
              placeholder="Ej. Alerta de Stock Crítico"
            />
            <Select
              label="Categoría"
              value={formData.category}
              onChange={(e) => setFormData({ ...formData, category: e.target.value })}
              options={categoryOptions}
              placeholder="Selecciona categoría"
              required
            />
          </div>

          <Input
            label="Descripción"
            value={formData.description}
            onChange={(e) => setFormData({ ...formData, description: e.target.value })}
            placeholder="Descripción breve de la regla"
          />

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <Select
              label="Prioridad"
              value={formData.priority}
              onChange={(e) =>
                setFormData({ ...formData, priority: e.target.value as '1' | '2' | '3' })
              }
              options={priorityOptions}
            />
            <div className="flex items-center gap-2 mt-6">
              <input
                type="checkbox"
                id="is_active"
                checked={formData.is_active}
                onChange={(e) => setFormData({ ...formData, is_active: e.target.checked })}
                className="w-4 h-4 text-indigo-600 rounded"
              />
              <label htmlFor="is_active" className="text-sm font-medium text-gray-700">
                Regla activa
              </label>
            </div>
          </div>

          {/* Conditions Builder */}
          <div className="border border-gray-200 rounded-lg p-4 bg-gray-50">
            <h4 className="text-sm font-semibold text-gray-700 mb-3">
              Condiciones (CUANDO...)
            </h4>
            <div className="space-y-3">
              {/* Stock Level */}
              <div className="flex items-center gap-3 flex-wrap">
                <input
                  type="checkbox"
                  checked={formData.conditions.stock_level.enabled}
                  onChange={(e) =>
                    updateCondition('stock_level', 'enabled', e.target.checked)
                  }
                  className="w-4 h-4 text-indigo-600 rounded flex-shrink-0"
                />
                <span className="text-sm font-medium text-gray-600 w-28 flex-shrink-0">
                  Nivel de Stock
                </span>
                <select
                  disabled={!formData.conditions.stock_level.enabled}
                  value={formData.conditions.stock_level.operator}
                  onChange={(e) =>
                    updateCondition('stock_level', 'operator', e.target.value)
                  }
                  className="border border-gray-300 rounded px-2 py-1 text-sm disabled:opacity-50 w-16"
                >
                  {numericOperatorOptions.map((o) => (
                    <option key={o.value} value={o.value}>
                      {o.label}
                    </option>
                  ))}
                </select>
                <input
                  type="number"
                  min="0"
                  max="100"
                  disabled={!formData.conditions.stock_level.enabled}
                  value={formData.conditions.stock_level.value}
                  onChange={(e) =>
                    updateCondition('stock_level', 'value', e.target.value)
                  }
                  className="border border-gray-300 rounded px-2 py-1 text-sm w-20 disabled:opacity-50"
                  placeholder="0-100"
                />
                <span className="text-xs text-gray-400">%</span>
              </div>

              {/* Demand Level */}
              <div className="flex items-center gap-3 flex-wrap">
                <input
                  type="checkbox"
                  checked={formData.conditions.demand_level.enabled}
                  onChange={(e) =>
                    updateCondition('demand_level', 'enabled', e.target.checked)
                  }
                  className="w-4 h-4 text-indigo-600 rounded flex-shrink-0"
                />
                <span className="text-sm font-medium text-gray-600 w-28 flex-shrink-0">
                  Nivel de Demanda
                </span>
                <select
                  disabled={!formData.conditions.demand_level.enabled}
                  value={formData.conditions.demand_level.operator}
                  onChange={(e) =>
                    updateCondition('demand_level', 'operator', e.target.value)
                  }
                  className="border border-gray-300 rounded px-2 py-1 text-sm disabled:opacity-50 w-16"
                >
                  {levelOperatorOptions.map((o) => (
                    <option key={o.value} value={o.value}>
                      {o.label}
                    </option>
                  ))}
                </select>
                <select
                  disabled={!formData.conditions.demand_level.enabled}
                  value={formData.conditions.demand_level.value}
                  onChange={(e) =>
                    updateCondition('demand_level', 'value', e.target.value)
                  }
                  className="border border-gray-300 rounded px-2 py-1 text-sm disabled:opacity-50"
                >
                  {levelValueOptions.map((o) => (
                    <option key={o.value} value={o.value}>
                      {o.label}
                    </option>
                  ))}
                </select>
              </div>

              {/* Risk Level */}
              <div className="flex items-center gap-3 flex-wrap">
                <input
                  type="checkbox"
                  checked={formData.conditions.risk_level.enabled}
                  onChange={(e) =>
                    updateCondition('risk_level', 'enabled', e.target.checked)
                  }
                  className="w-4 h-4 text-indigo-600 rounded flex-shrink-0"
                />
                <span className="text-sm font-medium text-gray-600 w-28 flex-shrink-0">
                  Nivel de Riesgo
                </span>
                <select
                  disabled={!formData.conditions.risk_level.enabled}
                  value={formData.conditions.risk_level.operator}
                  onChange={(e) =>
                    updateCondition('risk_level', 'operator', e.target.value)
                  }
                  className="border border-gray-300 rounded px-2 py-1 text-sm disabled:opacity-50 w-16"
                >
                  {levelOperatorOptions.map((o) => (
                    <option key={o.value} value={o.value}>
                      {o.label}
                    </option>
                  ))}
                </select>
                <select
                  disabled={!formData.conditions.risk_level.enabled}
                  value={formData.conditions.risk_level.value}
                  onChange={(e) =>
                    updateCondition('risk_level', 'value', e.target.value)
                  }
                  className="border border-gray-300 rounded px-2 py-1 text-sm disabled:opacity-50"
                >
                  {levelValueOptions.map((o) => (
                    <option key={o.value} value={o.value}>
                      {o.label}
                    </option>
                  ))}
                </select>
              </div>
            </div>
          </div>

          <Textarea
            label="Acción (ENTONCES...)"
            value={formData.action}
            onChange={(e) => setFormData({ ...formData, action: e.target.value })}
            required
            placeholder="Ej. Emitir alerta de reabastecimiento urgente y notificar al equipo de logística"
            className="min-h-[80px]"
          />
        </form>
      </Modal>

      {/* Delete Confirmation */}
      <Modal
        isOpen={!!deleteConfirm}
        onClose={() => setDeleteConfirm(null)}
        title="Confirmar Eliminación"
        size="sm"
        footer={
          <div className="flex justify-end gap-3">
            <Button variant="secondary" onClick={() => setDeleteConfirm(null)}>
              Cancelar
            </Button>
            <Button
              variant="danger"
              onClick={() => deleteConfirm && handleDelete(deleteConfirm)}
            >
              Eliminar
            </Button>
          </div>
        }
      >
        <p className="text-gray-600">
          ¿Estás seguro de que deseas eliminar esta regla? Esta acción no se puede deshacer.
        </p>
      </Modal>
    </>
  );
};
