import { useParams, Link } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { assetsApi } from '../api/client'
import './AssetDetail.css'

export default function AssetDetail() {
  const { id } = useParams()
  const assetId = id ? parseInt(id) : null

  const { data: asset, isLoading } = useQuery({
    queryKey: ['asset', assetId],
    queryFn: () => assetsApi.get(assetId!).then((res) => res.data),
    enabled: !!assetId,
  })

  const { data: inspections } = useQuery({
    queryKey: ['asset-inspections', assetId],
    queryFn: () => assetsApi.getInspections(assetId!).then((res) => res.data),
    enabled: !!assetId,
  })

  const { data: statistics } = useQuery({
    queryKey: ['asset-statistics', assetId],
    queryFn: () => assetsApi.getStatistics(assetId!).then((res) => res.data),
    enabled: !!assetId,
  })

  if (isLoading) {
    return <div className="loading">Carregando...</div>
  }

  if (!asset) {
    return <div className="error">Ativo não encontrado</div>
  }

  const getConditionColor = (status: string | null) => {
    const colors: { [key: string]: string } = {
      Good: '#27ae60',
      Fair: '#f1c40f',
      Poor: '#f39c12',
      Critical: '#e74c3c',
    }
    return colors[status || ''] || '#95a5a6'
  }

  return (
    <div className="asset-detail">
      <div className="detail-header">
        <Link to="/assets" className="back-link">
          ← Voltar para Ativos
        </Link>
        <h1>{asset.name || `Ativo #${asset.id}`}</h1>
      </div>

      <div className="detail-content">
        <div className="detail-section">
          <h2>Informações do Ativo</h2>
          <div className="info-grid">
            <div className="info-item">
              <strong>Tipo IFC:</strong>
              <span>{asset.ifc_type}</span>
            </div>
            <div className="info-item">
              <strong>GUID:</strong>
              <span className="guid">{asset.ifc_guid}</span>
            </div>
            {asset.manufacturer && (
              <div className="info-item">
                <strong>Fabricante:</strong>
                <span>{asset.manufacturer}</span>
              </div>
            )}
            {asset.serial_number && (
              <div className="info-item">
                <strong>Nº Série:</strong>
                <span>{asset.serial_number}</span>
              </div>
            )}
            {asset.location_building && (
              <div className="info-item">
                <strong>Localização:</strong>
                <span>
                  {asset.location_building}
                  {asset.location_floor && ` - ${asset.location_floor}`}
                  {asset.location_room && ` - ${asset.location_room}`}
                </span>
              </div>
            )}
            <div className="info-item">
              <strong>Condição:</strong>
              <span
                className="condition-badge"
                style={{ backgroundColor: getConditionColor(asset.condition_status) }}
              >
                {asset.condition_status || 'N/A'}
              </span>
            </div>
            {asset.condition_score && (
              <div className="info-item">
                <strong>Score:</strong>
                <span>{asset.condition_score}/4</span>
              </div>
            )}
            {asset.last_inspection_date && (
              <div className="info-item">
                <strong>Última Inspeção:</strong>
                <span>{new Date(asset.last_inspection_date).toLocaleDateString('pt-BR')}</span>
              </div>
            )}
          </div>
        </div>

        {statistics && (
          <div className="detail-section">
            <h2>Estatísticas</h2>
            <div className="stats-grid">
              <div className="stat-item">
                <strong>Total de Inspeções:</strong>
                <span>{statistics.total_inspections}</span>
              </div>
              <div className="stat-item">
                <strong>Com Patologia:</strong>
                <span>{statistics.inspections_with_pathology}</span>
              </div>
              <div className="stat-item">
                <strong>Última Inspeção:</strong>
                <span>
                  {statistics.latest_inspection_date
                    ? new Date(statistics.latest_inspection_date).toLocaleDateString('pt-BR')
                    : 'N/A'}
                </span>
              </div>
            </div>
          </div>
        )}

        {inspections && inspections.length > 0 && (
          <div className="detail-section">
            <h2>Histórico de Inspeções ({inspections.length})</h2>
            <div className="inspections-list">
              {inspections.map((inspection: any) => (
                <Link
                  key={inspection.id}
                  to={`/inspections/${inspection.id}`}
                  className="inspection-item"
                >
                  <div className="inspection-item-header">
                    <span className="inspection-code">{inspection.code}</span>
                    <span
                      className="severity-badge"
                      style={{
                        backgroundColor:
                          inspection.severity === 1
                            ? '#e74c3c'
                            : inspection.severity === 2
                            ? '#f39c12'
                            : inspection.severity === 3
                            ? '#f1c40f'
                            : '#27ae60',
                      }}
                    >
                      {inspection.severity || 'N/A'}
                    </span>
                  </div>
                  <div className="inspection-item-body">
                    <div>{inspection.location}</div>
                    <div>{new Date(inspection.inspection_date).toLocaleDateString('pt-BR')}</div>
                  </div>
                </Link>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

