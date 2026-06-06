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
  LineChart,
  Line,
  Legend,
} from 'recharts';
import { BookOpen, Target, CheckSquare, Star, FileText } from 'lucide-react';
import { kpisService } from '../../services/kpis.service';
import { decisionsService } from '../../services/decisions.service';
import { DashboardStats, Decision } from '../../types';
import { StatCard, Card } from '../../components/ui/Card';
import { Spinner } from '../../components/ui/Spinner';
import { Badge } from '../../components/ui/Badge';

const PIE_COLORS = ['#ef4444', '#f97316', '#eab308', '#22c55e', '#6366f1'];

const statusVariant = (status: string) => {
  if (status === 'aceptada') return 'success';
  if (status === 'rechazada') return 'danger';
  return 'warning';
};

export const DashboardPage: React.FC = () => {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [recentDecisions, setRecentDecisions] = useState<Decision[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [statsData, decisionsData] = await Promise.all([
          kpisService.getDashboard(),
          decisionsService.getDecisions({ page: 1, size: 5 }),
        ]);
        setStats(statsData);
        setRecentDecisions(decisionsData.items);
      } catch {
        setError('Error al cargar el dashboard. Verifica tu conexión con el servidor.');
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
        <p className="text-red-500 text-sm mt-1">
          Asegúrate de que el backend esté corriendo en http://localhost:8000
        </p>
      </div>
    );
  }

  const feedbackPieData = stats?.feedback_distribution.map((f) => ({
    name: `${f.rating} estrellas`,
    value: f.count,
  })) || [];

  return (
    <div className="space-y-6">
      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          title="Total Reglas"
          value={stats?.total_rules ?? 0}
          icon={<BookOpen className="w-6 h-6" />}
          color="indigo"
        />
        <StatCard
          title="Total Escenarios"
          value={stats?.total_scenarios ?? 0}
          icon={<Target className="w-6 h-6" />}
          color="blue"
        />
        <StatCard
          title="Total Decisiones"
          value={stats?.total_decisions ?? 0}
          icon={<CheckSquare className="w-6 h-6" />}
          color="green"
        />
        <StatCard
          title="Satisfacción Promedio"
          value={`${(stats?.avg_satisfaction ?? 0).toFixed(1)} / 5`}
          icon={<Star className="w-6 h-6" />}
          color="yellow"
        />
      </div>

      {/* Charts Row 1 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card title="Decisiones por Mes" padding="md">
          <ResponsiveContainer width="100%" height={280}>
            <BarChart data={stats?.decisions_by_month || []}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis
                dataKey="month"
                tick={{ fontSize: 12, fill: '#6b7280' }}
              />
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

        <Card title="Distribución de Satisfacción" padding="md">
          <ResponsiveContainer width="100%" height={280}>
            <PieChart>
              <Pie
                data={feedbackPieData}
                cx="50%"
                cy="50%"
                outerRadius={100}
                dataKey="value"
                label={({ name, percent }) =>
                  `${name} (${(percent * 100).toFixed(0)}%)`
                }
                labelLine={false}
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
        </Card>
      </div>

      {/* Charts Row 2 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card title="Reglas por Categoría" padding="md">
          <ResponsiveContainer width="100%" height={250}>
            <BarChart
              data={stats?.rules_by_category || []}
              layout="vertical"
            >
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

        <Card title="Tendencia de Decisiones" padding="md">
          <ResponsiveContainer width="100%" height={250}>
            <LineChart data={stats?.decisions_by_month || []}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
              <XAxis
                dataKey="month"
                tick={{ fontSize: 12, fill: '#6b7280' }}
              />
              <YAxis tick={{ fontSize: 12, fill: '#6b7280' }} />
              <Tooltip
                contentStyle={{
                  borderRadius: '8px',
                  border: '1px solid #e5e7eb',
                  fontSize: '13px',
                }}
              />
              <Line
                type="monotone"
                dataKey="count"
                stroke="#6366f1"
                strokeWidth={2}
                dot={{ fill: '#6366f1', r: 4 }}
                name="Decisiones"
              />
            </LineChart>
          </ResponsiveContainer>
        </Card>
      </div>

      {/* Recent Activity */}
      <Card title="Actividad Reciente" subtitle="Últimas 5 decisiones" padding="none">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">
                  Fecha
                </th>
                <th className="px-6 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">
                  Escenario
                </th>
                <th className="px-6 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">
                  Recomendaciones
                </th>
                <th className="px-6 py-3 text-left text-xs font-semibold text-gray-500 uppercase tracking-wider">
                  Estado
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {recentDecisions.length === 0 ? (
                <tr>
                  <td colSpan={4} className="px-6 py-8 text-center text-sm text-gray-500">
                    <FileText className="w-8 h-8 text-gray-300 mx-auto mb-2" />
                    No hay decisiones registradas aún
                  </td>
                </tr>
              ) : (
                recentDecisions.map((decision, index) => (
                  <tr
                    key={decision.id}
                    className={`hover:bg-gray-50 ${index % 2 === 1 ? 'bg-gray-50/50' : ''}`}
                  >
                    <td className="px-6 py-3 text-sm text-gray-700 whitespace-nowrap">
                      {new Date(decision.created_at).toLocaleDateString('es-GT', {
                        day: '2-digit',
                        month: 'short',
                        year: 'numeric',
                      })}
                    </td>
                    <td className="px-6 py-3 text-sm text-gray-700">
                      {decision.scenario?.name || `Escenario ${decision.scenario_id.slice(0, 8)}`}
                    </td>
                    <td className="px-6 py-3 text-sm text-gray-700">
                      {decision.recommendations?.length ?? 0} recomendación(es)
                    </td>
                    <td className="px-6 py-3">
                      <Badge
                        variant={statusVariant(decision.status)}
                      >
                        {decision.status.charAt(0).toUpperCase() + decision.status.slice(1)}
                      </Badge>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </Card>
    </div>
  );
};
