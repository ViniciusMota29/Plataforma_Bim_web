import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { ifcApi, inspectionsApi, assetsApi } from '../api/client'
import './Dashboard.css'

export default function Dashboard() {
  const { data: ifcFiles } = useQuery({
    queryKey: ['ifcFiles'],
    queryFn: () => ifcApi.list().then((res) => res.data),
  })

  const { data: inspections } = useQuery({
    queryKey: ['inspections'],
    queryFn: () => inspectionsApi.list().then((res) => res.data),
  })

  const { data: assets } = useQuery({
    queryKey: ['assets'],
    queryFn: () => assetsApi.list().then((res) => res.data),
  })

  const stats = {
    totalIFCFiles: ifcFiles?.length || 0,
    totalAssets: assets?.length || 0,
    totalInspections: inspections?.length || 0,
    inspectionsWithPathology: inspections?.filter((i: any) => i.has_pathology).length || 0,
    criticalAssets: assets?.filter((a: any) => a.condition_score === 1).length || 0,
  }

  return (
    <div className="dashboard">
      <h1>Dashboard</h1>

      <div className="stats-grid">
        <div className="stat-card">
          <h3>Arquivos IFC</h3>
          <p className="stat-value">{stats.totalIFCFiles}</p>
        </div>
        <div className="stat-card">
          <h3>Ativos</h3>
          <p className="stat-value">{stats.totalAssets}</p>
        </div>
        <div className="stat-card">
          <h3>Inspeções</h3>
          <p className="stat-value">{stats.totalInspections}</p>
        </div>
        <div className="stat-card critical">
          <h3>Patologias Detectadas</h3>
          <p className="stat-value">{stats.inspectionsWithPathology}</p>
        </div>
        <div className="stat-card critical">
          <h3>Ativos Críticos</h3>
          <p className="stat-value">{stats.criticalAssets}</p>
        </div>
      </div>

      <div className="dashboard-sections">
        <section className="dashboard-section">
          <h2>Últimas Inspeções</h2>
          <div className="inspections-list">
            {inspections?.slice(0, 5).map((inspection: any) => (
              <Link
                key={inspection.id}
                to={`/inspections/${inspection.id}`}
                className="inspection-item"
              >
                <div className="inspection-header">
                  <span className="inspection-code">{inspection.code}</span>
                  <span
                    className={`severity-badge severity-${inspection.severity || 0}`}
                  >
                    {inspection.severity || 'N/A'}
                  </span>
                </div>
                <div className="inspection-details">
                  <span>{inspection.location}</span>
                  <span>{new Date(inspection.inspection_date).toLocaleDateString('pt-BR')}</span>
                </div>
              </Link>
            ))}
          </div>
          <Link to="/inspections" className="view-all-link">
            Ver todas as inspeções →
          </Link>
        </section>

        <section className="dashboard-section">
          <h2>Ativos por Condição</h2>
          <div className="condition-stats">
            {['Good', 'Fair', 'Poor', 'Critical'].map((condition) => {
              const count =
                assets?.filter((a: any) => a.condition_status === condition).length || 0
              return (
                <div key={condition} className="condition-item">
                  <span className="condition-label">{condition}</span>
                  <div className="condition-bar">
                    <div
                      className={`condition-fill condition-${condition.toLowerCase()}`}
                      style={{
                        width: `${assets?.length ? (count / assets.length) * 100 : 0}%`,
                      }}
                    />
                  </div>
                  <span className="condition-count">{count}</span>
                </div>
              )
            })}
          </div>
        </section>
      </div>
    </div>
  )
}

