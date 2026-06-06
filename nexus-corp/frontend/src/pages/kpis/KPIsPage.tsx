import React, { useEffect, useState } from 'react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  Legend,
} from 'recharts';
import { BookOpen, Target, CheckSquare, Star, TrendingUp, ThumbsUp, ThumbsDown } from 'lucide-react';
import { KPI, DashboardStats } from '../../types';
import { kpisService } from '../../services/kpis.service';
import { StatCard, Card } from '../../components/ui/Card';
import { Spinner } from '../../components/ui/Spinner';

const PIE_COLORS = ['#ef4444', '#f97316', '#eab308', '#22c55e', '#6366f1'];

export const KPIsPage: React.FC = () => {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [kpis, setKpis] = useState<KPI[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [statsData, kpisData] = await Promise.all([
          kpisService.getDashboard(),
          kpisService.getKPIs({ size: 100 }),
        ]);
        setStats(statsData);
        setKpis(kpisData.items);
      } catch {
        setError('Error al cargar los KPIs. Verifica la conexión con el servidor.');
      } finally {
        setIsLoading(false);
      }
    };
    fetchData();
  }, []);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Spinner size="xl" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-8 text-center">
        <p className="text-red-700 font-medium">{error}</p>
      </div>
    );
  }

  const feedbackPieData = stats?.feedback_distribution.map((f) => ({
    name: `${f.rating} ★`,
    value: f.count,
  })) || [];

  const acceptRate =
    stats && (stats.accepted_recommendations + stats.rejected_recommendations) > 0
      ? (stats.accepted_recommendations /
          (stats.accepted_recommendations + stats.rejected_recommendations)) *
        100
      : 0;

  return (
    <div className="space-y-6">
      {/* Summary Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-4">
        <StatCard
          title="Reglas Activas"
          value={stats?.total_rules ?? 0}
          icon={<BookOpen className="w-6 h-6" />}
          color="indigo"
        />
        <StatCard
          title="Escenarios"
          value={stats?.total_scenarios ?? 0}
          icon={<Target className="w-6 h-6" />}
          color="blue"
        />
        <StatCard
          title="Decisiones"
          value={stats?.total_decisions ?? 0}
          icon={<CheckSquare className="w-6 h-6" />}
          color="green"
        />
        <StatCard
          title="Satisfacción"
          value={`${(stats?.avg_satisfaction ?? 0).toFixed(1)}/5`}
          icon={<Star className="w-6 h-6" />}
          color="yellow"
        />
        <StatCard
          title="Rec. Aceptadas"
          value={stats?.accepted_recommendations ?? 0}
          icon={<ThumbsUp className="w-6 h-6" />}
          color="green"
        />
        <StatCard
          title="Rec. Rechazadas"
          value={stats?.rejected_recommendations ?? 0}
          icon={<ThumbsDown className="w-6 h-6" />}
          color="red"
        />
      </div>

      {/* Acceptance Rate */}
      <div className="bg-white rounded-lg border border-gray-200 shadow-sm p-5">
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center gap-2">
            <TrendingUp className="w-5 h-5 text-indigo-600" />
            <h3 className="font-semibold text-gray-900">
              Tasa de Aceptación de Recomendaciones
            </h3>
          </div>
          <span className="text-2xl font-bold text-indigo-600">
            {acceptRate.toFixed(1)}%
          </span>
        </div>
        <div className="w-full bg-gray-100 rounded-full h-4">
          <div
            className="bg-gradient-to-r from-indigo-500 to-green-500 h-4 rounded-full transition-all duration-500"
            style={{ width: `${acceptRate}%` }}
          />
        </div>
        <div className="flex justify-between text-xs text-gray-500 mt-1">
          <span>{stats?.accepted_recommendations ?? 0} aceptadas</span>
          <span>{stats?.rejected_recommendations ?? 0} rechazadas</span>
        </div>
      </div>

      {/* Decisions by Month - Full Width */}
      <Card title="Decisiones por Mes" padding="md">
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={stats?.decisions_by_month || []}>
            <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
            <XAxis dataKey="month" tick={{ fontSize: 12, fill: '#6b7280' }} />
            <YAxis tick={{ fontSize: 12, fill: '#6b7280' }} />
            <Tooltip
              contentStyle={{
                borderRadius: '8px',
                border: '1px solid #e5e7eb',
                fontSize: '13px',
              }}
            />
            <Bar dataKey="count" fill="#6366f1" radius={[4, 4, 0, 0]} name="Decisiones" />
          </BarChart>
        </ResponsiveContainer>
      </Card>

      {/* Two charts side by side */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card title="Distribución de Feedback por Calificación" padding="md">
          {feedbackPieData.length > 0 ? (
            <ResponsiveContainer width="100%" height={280}>
              <PieChart>
                <Pie
                  data={feedbackPieData}
                  cx="50%"
                  cy="45%"
                  outerRadius={90}
                  dataKey="value"
                  label={({ name, value }) => `${name}: ${value}`}
                >
                  {feedbackPieData.map((_entry, index) => (
                    <Cell
                      key={`cell-${index}`}
                      fill={PIE_COLORS[index % PIE_COLORS.length]}
                    />
                  ))}
                </Pie>
                <Tooltip
                  contentStyle={{
                    borderRadius: '8px',
                    border: '1px solid #e5e7eb',
                    fontSize: '13px',
                  }}
                />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          ) : (
            <div className="flex items-center justify-center h-48 text-gray-400">
              Sin datos de feedback
            </div>
          )}
        </Card>

        <Card title="Reglas por Categoría" padding="md">
          <ResponsiveContainer width="100%" height={280}>
            <BarChart data={stats?.rules_by_category || []} layout="vertical">
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis type="number" tick={{ fontSize: 12, fill: '#6b7280' }} />
              <YAxis
                type="category"
                dataKey="category"
                tick={{ fontSize: 12, fill: '#6b7280' }}
                width={90}
              />
              <Tooltip
                contentStyle={{
                  borderRadius: '8px',
                  border: '1px solid #e5e7eb',
                  fontSize: '13px',
                }}
              />
              <Bar dataKey="count" fill="#22c55e" radius={[0, 4, 4, 0]} name="Reglas" />
            </BarChart>
          </ResponsiveContainer>
        </Card>
      </div>

      {/* KPI Records Table */}
      {kpis.length > 0 && (
        <Card title="Registros de KPI" padding="none">
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  {['KPI', 'Valor', 'Unidad', 'Período', 'Categoría', 'Fecha'].map((h) => (
                    <th
                      key={h}
                      className="px-4 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider"
                    >
                      {h}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {kpis.map((kpi, idx) => (
                  <tr
                    key={kpi.id}
                    className={`hover:bg-gray-50 ${idx % 2 === 1 ? 'bg-gray-50/50' : ''}`}
                  >
                    <td className="px-4 py-3 text-sm font-medium text-gray-900">
                      {kpi.name}
                    </td>
                    <td className="px-4 py-3 text-sm font-bold text-indigo-600">
                      {kpi.value}
                    </td>
                    <td className="px-4 py-3 text-sm text-gray-600">{kpi.unit}</td>
                    <td className="px-4 py-3 text-sm text-gray-600">{kpi.period}</td>
                    <td className="px-4 py-3 text-sm text-gray-600">{kpi.category}</td>
                    <td className="px-4 py-3 text-sm text-gray-500">
                      {new Date(kpi.created_at).toLocaleDateString('es-GT')}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Card>
      )}
    </div>
  );
};
