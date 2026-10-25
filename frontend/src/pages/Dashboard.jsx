import React, { useState, useEffect } from 'react';
import MetricCard from '../components/MetricCard';
import { DollarSign, Cpu, Zap, FileText, Loader2 } from 'lucide-react';
import api from '../api';

const Dashboard = () => {
  const [metrics, setMetrics] = useState({
    total_procesados: 0,
    latencia_promedio_ms: 0,
    costo_estimado_usd: 0,
    historial: []
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchMetrics = async () => {
      try {
        const response = await api.get('/dashboard/metrics');
        setMetrics(response.data);
      } catch (error) {
        console.error("Error cargando métricas:", error);
      } finally {
        setLoading(false);
      }
    };
    
    fetchMetrics();
  }, []);

  if (loading) {
    return (
      <div className="flex h-full items-center justify-center">
        <Loader2 className="animate-spin text-brand-cyan" size={40} />
      </div>
    );
  }

  return (
    <div className="p-8">
      <header className="mb-8">
        <h2 className="text-3xl font-bold text-brand-dark">Panel de Control</h2>
        <p className="text-gray-500 mt-1">Monitoreo en tiempo real del pipeline de análisis.</p>
      </header>

      {/* Grid de Métricas Reales */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <MetricCard title="Artículos Procesados" value={metrics.total_procesados} icon={FileText} />
        <MetricCard title="Costo Estimado" value={`$${metrics.costo_estimado_usd}`} icon={DollarSign} />
        <MetricCard title="Latencia Promedio" value={`${metrics.latencia_promedio_ms}ms`} icon={Zap} />
        <MetricCard title="Tokens (Aprox)" value={metrics.total_procesados * 500} icon={Cpu} />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Placeholder para Gráfico */}
        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100 lg:col-span-2 h-80 flex flex-col">
          <h3 className="font-semibold text-brand-dark mb-4">Análisis de Sentimiento (Simulado)</h3>
          <div className="flex-1 bg-brand-pale/30 rounded-lg flex items-center justify-center border border-brand-light border-dashed">
            <span className="text-brand-blue font-medium">Gráfico de Barras (Próximamente)</span>
          </div>
        </div>
        
        {/* Tabla de Últimos Artículos Reales */}
        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100 h-80 flex flex-col">
          <h3 className="font-semibold text-brand-dark mb-4">Últimos Artículos</h3>
          <ul className="space-y-3 overflow-y-auto flex-1">
            {metrics.historial.length === 0 ? (
              <p className="text-gray-400 text-sm text-center mt-10">No hay artículos procesados aún.</p>
            ) : (
              metrics.historial.map((item, i) => (
                <li key={i} className="flex flex-col text-sm border-b border-gray-50 pb-2">
                  <div className="flex justify-between items-center">
                    <span className="text-gray-700 font-medium truncate w-3/4">{item.title}</span>
                    <span className="text-xs px-2 py-1 bg-green-100 text-green-700 rounded-full font-medium">OK</span>
                  </div>
                  <span className="text-xs text-gray-400 mt-1">{item.timestamp} | {item.latency_ms}ms</span>
                </li>
              ))
            )}
          </ul>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;