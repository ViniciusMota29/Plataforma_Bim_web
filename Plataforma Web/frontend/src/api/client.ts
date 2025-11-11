import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// IFC endpoints
export const ifcApi = {
  upload: (file: File) => {
    const formData = new FormData()
    formData.append('file', file)
    return apiClient.post('/api/ifc/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
  },
  list: () => apiClient.get('/api/ifc/'),
  get: (id: number) => apiClient.get(`/api/ifc/${id}`),
  getElements: (id: number) => apiClient.get(`/api/ifc/${id}/elements`),
  getAssets: (id: number) => apiClient.get(`/api/ifc/${id}/assets`),
}

// Assets endpoints
export const assetsApi = {
  list: (params?: { ifc_file_id?: number; condition_status?: string }) =>
    apiClient.get('/api/assets/', { params }),
  get: (id: number) => apiClient.get(`/api/assets/${id}`),
  update: (id: number, data: any) => apiClient.put(`/api/assets/${id}`, data),
  getInspections: (id: number) => apiClient.get(`/api/assets/${id}/inspections`),
  getStatistics: (id: number) => apiClient.get(`/api/assets/${id}/statistics`),
}

// Inspections endpoints
export const inspectionsApi = {
  create: (data: FormData) =>
    apiClient.post('/api/inspections/', data, {
      headers: { 'Content-Type': 'multipart/form-data' },
    }),
  list: (params?: { asset_id?: number }) =>
    apiClient.get('/api/inspections/', { params }),
  get: (id: number) => apiClient.get(`/api/inspections/${id}`),
  update: (id: number, data: any) => apiClient.put(`/api/inspections/${id}`, data),
  delete: (id: number) => apiClient.delete(`/api/inspections/${id}`),
}

// AI Analysis endpoints
export const aiApi = {
  analyze: (files: File[], assetId?: number, inspectionId?: number) => {
    const formData = new FormData()
    files.forEach((file) => formData.append('images', file))
    if (assetId) formData.append('asset_id', assetId.toString())
    if (inspectionId) formData.append('inspection_id', inspectionId.toString())
    return apiClient.post('/api/ai/analyze', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
  },
}

