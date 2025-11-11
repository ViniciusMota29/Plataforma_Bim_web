import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { assetsApi } from '../api/client'
import './Assets.css'

export default function Assets() {
  const { data: assets, isLoading } = useQuery({
    queryKey: ['assets'],
    queryFn: () => assetsApi.list().then((res) => res.data),
  })

  const getConditionColor = (status: string | null) => {
    const colors: { [key: string]: string } = {
      Good: '#27ae60',
      Fair: '#f1c40f',
      Poor: '#f39c12',
      Critical: '#e74c3c',
    }
    return colors[status || ''] || '#95a5a6'
  }

  if (isLoading) {
    return <div className="loading">Carregando ativos...</div>
  }

  return (
    <div className="assets">
      <div className="assets-header">
        <h1>Ativos</h1>
        <div className="assets-filters">
          <select
            onChange={(e) => {
              // Filter logic would go here
            }}
          >
            <option value="">Todos os status</option>
            <option value="Good">Bom</option>
            <option value="Fair">Regular</option>
            <option value="Poor">Ruim</option>
            <option value="Critical">Crítico</option>
          </select>
        </div>
      </div>

      <div className="assets-grid">
        {assets && assets.length > 0 ? (
          assets.map((asset: any) => (
            <Link key={asset.id} to={`/assets/${asset.id}`} className="asset-card">
              <div className="asset-card-header">
                <h3>{asset.name || `Ativo #${asset.id}`}</h3>
                <span
                  className="condition-badge"
                  style={{ backgroundColor: getConditionColor(asset.condition_status) }}
                >
                  {asset.condition_status || 'N/A'}
                </span>
              </div>
              <div className="asset-card-body">
                <div className="asset-info">
                  <div>
                    <strong>Tipo:</strong> {asset.ifc_type}
                  </div>
                  {asset.manufacturer && (
                    <div>
                      <strong>Fabricante:</strong> {asset.manufacturer}
                    </div>
                  )}
                  {asset.serial_number && (
                    <div>
                      <strong>Nº Série:</strong> {asset.serial_number}
                    </div>
                  )}
                  {asset.location_building && (
                    <div>
                      <strong>Localização:</strong> {asset.location_building}
                      {asset.location_floor && ` - ${asset.location_floor}`}
                    </div>
                  )}
                  {asset.condition_score && (
                    <div>
                      <strong>Score:</strong> {asset.condition_score}/4
                    </div>
                  )}
                </div>
              </div>
            </Link>
          ))
        ) : (
          <div className="empty-state">
            <p>Nenhum ativo cadastrado.</p>
          </div>
        )}
      </div>
    </div>
  )
}

