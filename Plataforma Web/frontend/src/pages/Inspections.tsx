import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { inspectionsApi, assetsApi } from '../api/client'
import InspectionForm from '../components/InspectionForm'
import './Inspections.css'

export default function Inspections() {
  const [showForm, setShowForm] = useState(false)
  const [selectedAssetId, setSelectedAssetId] = useState<number | null>(null)
  const queryClient = useQueryClient()

  const { data: inspections, isLoading } = useQuery({
    queryKey: ['inspections'],
    queryFn: () => inspectionsApi.list().then((res) => res.data),
  })

  const { data: assets } = useQuery({
    queryKey: ['assets'],
    queryFn: () => assetsApi.list().then((res) => res.data),
  })

  const deleteMutation = useMutation({
    mutationFn: (id: number) => inspectionsApi.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['inspections'] })
    },
  })

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

  const getSeverityLabel = (severity: number | null) => {
    if (!severity) return 'N/A'
    const labels: { [key: number]: string } = {
      1: 'Crítico',
      2: 'Ruim',
      3: 'Regular',
      4: 'Bom',
    }
    return labels[severity] || 'N/A'
  }

  if (isLoading) {
    return <div className="loading">Carregando inspeções...</div>
  }

  return (
    <div className="inspections">
      <div className="inspections-header">
        <h1>Inspeções</h1>
        <button className="btn-primary" onClick={() => setShowForm(true)}>
          Nova Inspeção
        </button>
      </div>

      {showForm && (
        <InspectionForm
          assets={assets || []}
          selectedAssetId={selectedAssetId}
          onClose={() => {
            setShowForm(false)
            setSelectedAssetId(null)
          }}
          onSuccess={() => {
            setShowForm(false)
            setSelectedAssetId(null)
            queryClient.invalidateQueries({ queryKey: ['inspections'] })
          }}
        />
      )}

      <div className="inspections-list">
        {inspections && inspections.length > 0 ? (
          inspections.map((inspection: any) => {
            const asset = assets?.find((a: any) => a.id === inspection.asset_id)
            return (
              <div key={inspection.id} className="inspection-card">
                <div className="inspection-card-header">
                  <div>
                    <h3>
                      <Link to={`/inspections/${inspection.id}`}>{inspection.code}</Link>
                    </h3>
                    <p className="inspection-asset">
                      {asset?.name || `Ativo #${inspection.asset_id}`}
                    </p>
                  </div>
                  <div className="inspection-badges">
                    <span
                      className="severity-badge"
                      style={{ backgroundColor: getSeverityColor(inspection.severity) }}
                    >
                      {getSeverityLabel(inspection.severity)}
                    </span>
                    {inspection.has_pathology && (
                      <span className="pathology-badge">Patologia</span>
                    )}
                    {inspection.ai_analysis_performed && (
                      <span className="ai-badge">IA</span>
                    )}
                  </div>
                </div>

                <div className="inspection-card-body">
                  <div className="inspection-info">
                    <div>
                      <strong>Local:</strong> {inspection.location}
                    </div>
                    <div>
                      <strong>Data:</strong>{' '}
                      {new Date(inspection.inspection_date).toLocaleString('pt-BR')}
                    </div>
                    {inspection.observations && (
                      <div>
                        <strong>Observações:</strong> {inspection.observations}
                      </div>
                    )}
                  </div>

                  <div className="inspection-actions">
                    <Link to={`/inspections/${inspection.id}`} className="btn-link">
                      Ver Detalhes
                    </Link>
                    <button
                      className="btn-danger"
                      onClick={() => {
                        if (confirm('Tem certeza que deseja excluir esta inspeção?')) {
                          deleteMutation.mutate(inspection.id)
                        }
                      }}
                    >
                      Excluir
                    </button>
                  </div>
                </div>
              </div>
            )
          })
        ) : (
          <div className="empty-state">
            <p>Nenhuma inspeção cadastrada.</p>
            <button className="btn-primary" onClick={() => setShowForm(true)}>
              Criar Primeira Inspeção
            </button>
          </div>
        )}
      </div>
    </div>
  )
}

