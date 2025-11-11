import { useState } from 'react'
import { useMutation } from '@tanstack/react-query'
import { inspectionsApi, aiApi } from '../api/client'
import './InspectionForm.css'

interface InspectionFormProps {
  assets: any[]
  selectedAssetId?: number | null
  onClose: () => void
  onSuccess: () => void
}

export default function InspectionForm({
  assets,
  selectedAssetId,
  onClose,
  onSuccess,
}: InspectionFormProps) {
  const [formData, setFormData] = useState({
    code: '',
    asset_id: selectedAssetId || '',
    inspection_date: new Date().toISOString().slice(0, 16),
    has_pathology: false,
    severity: '',
    location: '',
    observations: '',
    pathology_type: '',
  })
  const [photos, setPhotos] = useState<File[]>([])
  const [analyzing, setAnalyzing] = useState(false)

  const createMutation = useMutation({
    mutationFn: async (data: FormData) => {
      return inspectionsApi.create(data)
    },
    onSuccess: (response) => {
      // If photos were uploaded, analyze them with AI
      if (photos.length > 0) {
        analyzePhotos(response.data.id)
      } else {
        onSuccess()
      }
    },
  })

  const analyzePhotos = async (inspectionId: number) => {
    setAnalyzing(true)
    try {
      await aiApi.analyze(photos, formData.asset_id ? parseInt(formData.asset_id.toString()) : undefined, inspectionId)
    } catch (error) {
      console.error('Error analyzing photos:', error)
    } finally {
      setAnalyzing(false)
      onSuccess()
    }
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()

    const formDataToSend = new FormData()
    formDataToSend.append('code', formData.code)
    formDataToSend.append('asset_id', formData.asset_id.toString())
    formDataToSend.append('inspection_date', new Date(formData.inspection_date).toISOString())
    formDataToSend.append('has_pathology', formData.has_pathology.toString())
    if (formData.has_pathology && formData.severity) {
      formDataToSend.append('severity', formData.severity)
    }
    formDataToSend.append('location', formData.location)
    if (formData.observations) {
      formDataToSend.append('observations', formData.observations)
    }
    if (formData.pathology_type) {
      formDataToSend.append('pathology_type', formData.pathology_type)
    }

    photos.forEach((photo) => {
      formDataToSend.append('photos', photo)
    })

    createMutation.mutate(formDataToSend)
  }

  const handlePhotoChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      setPhotos(Array.from(e.target.files))
    }
  }

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>Nova Inspeção</h2>
          <button className="modal-close" onClick={onClose}>
            ×
          </button>
        </div>

        <form onSubmit={handleSubmit} className="inspection-form">
          <div className="form-group">
            <label htmlFor="code">Código *</label>
            <input
              type="text"
              id="code"
              value={formData.code}
              onChange={(e) => setFormData({ ...formData, code: e.target.value })}
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="asset_id">Ativo *</label>
            <select
              id="asset_id"
              value={formData.asset_id}
              onChange={(e) => setFormData({ ...formData, asset_id: e.target.value })}
              required
            >
              <option value="">Selecione um ativo</option>
              {assets.map((asset) => (
                <option key={asset.id} value={asset.id}>
                  {asset.name || `Ativo #${asset.id}`} ({asset.ifc_type})
                </option>
              ))}
            </select>
          </div>

          <div className="form-group">
            <label htmlFor="inspection_date">Data da Inspeção *</label>
            <input
              type="datetime-local"
              id="inspection_date"
              value={formData.inspection_date}
              onChange={(e) => setFormData({ ...formData, inspection_date: e.target.value })}
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="location">Local *</label>
            <input
              type="text"
              id="location"
              value={formData.location}
              onChange={(e) => setFormData({ ...formData, location: e.target.value })}
              required
            />
          </div>

          <div className="form-group">
            <label>
              <input
                type="checkbox"
                checked={formData.has_pathology}
                onChange={(e) =>
                  setFormData({ ...formData, has_pathology: e.target.checked })
                }
              />
              Há patologia?
            </label>
          </div>

          {formData.has_pathology && (
            <>
              <div className="form-group">
                <label htmlFor="severity">Severidade *</label>
                <select
                  id="severity"
                  value={formData.severity}
                  onChange={(e) => setFormData({ ...formData, severity: e.target.value })}
                  required
                >
                  <option value="">Selecione</option>
                  <option value="1">1 - Crítico</option>
                  <option value="2">2 - Ruim</option>
                  <option value="3">3 - Regular</option>
                  <option value="4">4 - Bom</option>
                </select>
              </div>

              <div className="form-group">
                <label htmlFor="pathology_type">Tipo de Patologia</label>
                <input
                  type="text"
                  id="pathology_type"
                  value={formData.pathology_type}
                  onChange={(e) =>
                    setFormData({ ...formData, pathology_type: e.target.value })
                  }
                  placeholder="Ex: Armadura exposta, Fissura, etc."
                />
              </div>
            </>
          )}

          <div className="form-group">
            <label htmlFor="observations">Observações</label>
            <textarea
              id="observations"
              value={formData.observations}
              onChange={(e) => setFormData({ ...formData, observations: e.target.value })}
              rows={4}
            />
          </div>

          <div className="form-group">
            <label htmlFor="photos">Fotos</label>
            <input
              type="file"
              id="photos"
              accept="image/*"
              multiple
              onChange={handlePhotoChange}
            />
            {photos.length > 0 && (
              <p className="photo-count">{photos.length} foto(s) selecionada(s)</p>
            )}
          </div>

          <div className="form-actions">
            <button type="button" className="btn-secondary" onClick={onClose}>
              Cancelar
            </button>
            <button type="submit" className="btn-primary" disabled={createMutation.isPending || analyzing}>
              {analyzing ? 'Analisando...' : createMutation.isPending ? 'Salvando...' : 'Salvar'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

