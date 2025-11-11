import { useEffect, useRef, useState } from 'react'
import { useParams } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { ifcApi } from '../api/client'
import * as THREE from 'three'
import { IFCLoader } from 'web-ifc'
import './IFCViewer.css'

export default function IFCViewer() {
  const { fileId } = useParams()
  const containerRef = useRef<HTMLDivElement>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const { data: ifcFiles } = useQuery({
    queryKey: ['ifcFiles'],
    queryFn: () => ifcApi.list().then((res) => res.data),
  })

  useEffect(() => {
    if (!containerRef.current) return

    // Initialize Three.js scene
    const scene = new THREE.Scene()
    scene.background = new THREE.Color(0xf0f0f0)

    const camera = new THREE.PerspectiveCamera(
      75,
      containerRef.current.clientWidth / containerRef.current.clientHeight,
      0.1,
      1000
    )
    camera.position.set(10, 10, 10)

    const renderer = new THREE.WebGLRenderer({ antialias: true })
    renderer.setSize(containerRef.current.clientWidth, containerRef.current.clientHeight)
    renderer.shadowMap.enabled = true
    containerRef.current.appendChild(renderer.domElement)

    // Add lights
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.6)
    scene.add(ambientLight)

    const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8)
    directionalLight.position.set(10, 10, 5)
    directionalLight.castShadow = true
    scene.add(directionalLight)

    // Add grid
    const gridHelper = new THREE.GridHelper(20, 20)
    scene.add(gridHelper)

    // Add axes helper
    const axesHelper = new THREE.AxesHelper(5)
    scene.add(axesHelper)

    // Load IFC file if fileId is provided
    if (fileId) {
      loadIFCFile(parseInt(fileId), scene, renderer, camera)
    }

    // Handle window resize
    const handleResize = () => {
      if (!containerRef.current) return
      camera.aspect = containerRef.current.clientWidth / containerRef.current.clientHeight
      camera.updateProjectionMatrix()
      renderer.setSize(containerRef.current.clientWidth, containerRef.current.clientHeight)
    }
    window.addEventListener('resize', handleResize)

    // Animation loop
    const animate = () => {
      requestAnimationFrame(animate)
      renderer.render(scene, camera)
    }
    animate()

    // Cleanup
    return () => {
      window.removeEventListener('resize', handleResize)
      if (containerRef.current && renderer.domElement.parentNode) {
        containerRef.current.removeChild(renderer.domElement)
      }
      renderer.dispose()
    }
  }, [fileId])

  const loadIFCFile = async (
    id: number,
    scene: THREE.Scene,
    renderer: THREE.WebGLRenderer,
    camera: THREE.PerspectiveCamera
  ) => {
    setLoading(true)
    setError(null)

    try {
      const response = await ifcApi.get(id)
      const ifcFile = response.data

      // Note: In a real implementation, you would need to:
      // 1. Fetch the IFC file from the server
      // 2. Use web-ifc to load and parse it
      // 3. Create Three.js meshes from IFC geometry

      // This is a placeholder - actual IFC loading requires:
      // - File download from server
      // - IFCLoader from web-ifc
      // - Geometry extraction and mesh creation

      setLoading(false)
    } catch (err: any) {
      setError(err.message || 'Erro ao carregar arquivo IFC')
      setLoading(false)
    }
  }

  return (
    <div className="ifc-viewer">
      <div className="viewer-header">
        <h1>Visualizador 3D IFC</h1>
        <div className="viewer-controls">
          {ifcFiles && (
            <select
              value={fileId || ''}
              onChange={(e) => {
                if (e.target.value) {
                  window.location.href = `/viewer/${e.target.value}`
                }
              }}
            >
              <option value="">Selecione um arquivo IFC</option>
              {ifcFiles.map((file: any) => (
                <option key={file.id} value={file.id}>
                  {file.filename}
                </option>
              ))}
            </select>
          )}
        </div>
      </div>

      {loading && (
        <div className="viewer-loading">
          <p>Carregando modelo IFC...</p>
        </div>
      )}

      {error && (
        <div className="viewer-error">
          <p>Erro: {error}</p>
        </div>
      )}

      <div ref={containerRef} className="viewer-container" />
    </div>
  )
}

