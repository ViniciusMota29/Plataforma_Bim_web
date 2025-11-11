import { useParams, Link } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { inspectionsApi, assetsApi } from '../api/client'
import './InspectionDetail.css'

export default function InspectionDetail() {
  const { id } = useParams()
  const inspectionId = id ? parseInt(id) : null

  const { data: inspection, isLoading } = useQuery({
    queryKey: ['inspection', inspectionId],
    queryFn: () => inspectionsApi.get(inspectionId!).then((res) => res.data),
    enabled: !!inspectionId,
  })

  const { data: asset } = useQuery({
    queryKey: ['asset', inspection?.asset_id],
    queryFn: () => assetsApi.get(inspection!.asset_id).then((res) => res.data),
    enabled: !!inspection?.asset_id,
  })

  if (isLoading) {
    return <div className="loading">Carregando...</div>
  }

  if (!inspection) {
    return <div className="error">Inspeção não encontrada</div>
  }

  const getSeverityColor = (severity: number | null) => {
    if (!severity) return '#95a5a6'
    const colors: { [key: number]: string } = {
      1: '#e74c3c',
      2: '#f39c12',
      3: '#f1c40f',
      4: '#27ae60',
    }
    return colors[severity] || '#95a5a6'
  }

  return (
    <div className="inspection-detail">
      <div className="detail-header">
        <Link to="/inspections" className="back-link">
          ← Voltar para Inspeções
        </Link>
        <h1>Inspeção {inspection.code}</h1>
      </div>

      <div className="detail-content">
        <div className="detail-section">
          <h2>Informações Gerais</h2>
          <div className="info-grid">
            <div className="info-item">
              <strong>Ativo:</strong>
              {asset ? (
                <Link to={`/assets/${asset.id}`}>{asset.name || `Ativo #${asset.id}`}</Link>
              ) : (
                <span>Ativo #{inspection.asset_id}</span>
              )}
            </div>
            <div className="info-item">
              <strong>Data:</strong>
              <span>{new Date(inspection.inspection_date).toLocaleString('pt-BR')}</span>
            </div>
            <div className="info-item">
              <strong>Local:</strong>
              <span>{inspection.location}</span>
            </div>
            <div className="info-item">
              <strong>Patologia:</strong>
              <span>{inspection.has_pathology ? 'Sim' : 'Não'}</span>
            </div>
            {inspection.has_pathology && (
              <>
                <div className="info-item">
                  <strong>Severidade:</strong>
                  <span
                    className="severity-badge"
                    style={{ backgroundColor: getSeverityColor(inspection.severity) }}
                  >
                    {inspection.severity || 'N/A'}
                  </span>
                </div>
                {inspection.pathology_type && (
                  <div className="info-item">
                    <strong>Tipo de Patologia:</strong>
                    <span>{inspection.pathology_type}</span>
                  </div>
                )}
              </>
            )}
          </div>
        </div>

        {inspection.observations && (
          <div className="detail-section">
            <h2>Observações</h2>
            <p>{inspection.observations}</p>
          </div>
        )}

        {inspection.ai_analysis_performed && (
          <div className="detail-section">
            <h2>Análise de IA</h2>
            <div className="ai-results">
              <div className="ai-item">
                <strong>Análise Realizada:</strong>
                <span>Sim</span>
              </div>
              {inspection.ai_confidence && (
                <div className="ai-item">
                  <strong>Confiança:</strong>
                  <span>{(inspection.ai_confidence * 100).toFixed(1)}%</span>
                </div>
              )}
              {inspection.ai_heatmap_path && (
                <div className="ai-item">
                  <strong>Heatmap:</strong>
                  <a href={inspection.ai_heatmap_path} target="_blank" rel="noopener noreferrer">
                    Ver Heatmap
                  </a>
                </div>
              )}
              {inspection.ai_detection_mask_path && (
                <div className="ai-item">
                  <strong>Máscara de Detecção:</strong>
                  <a
                    href={inspection.ai_detection_mask_path}
                    target="_blank"
                    rel="noopener noreferrer"
                  >
                    Ver Máscara
                  </a>
                </div>
              )}
            </div>
          </div>
        )}

        {inspection.photos && inspection.photos.length > 0 && (
          <div className="detail-section">
            <h2>Fotos ({inspection.photos.length})</h2>
            <div className="photos-grid">
              {inspection.photos.map((photo: any) => (
                <div key={photo.id} className="photo-item">
                  <img src={photo.file_path} alt={photo.file_name} />
                  <p>{photo.file_name}</p>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

