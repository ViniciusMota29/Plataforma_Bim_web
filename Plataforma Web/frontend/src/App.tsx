import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import Layout from './components/Layout'
import Dashboard from './pages/Dashboard'
import IFCViewer from './pages/IFCViewer'
import Inspections from './pages/Inspections'
import Assets from './pages/Assets'
import InspectionDetail from './pages/InspectionDetail'
import AssetDetail from './pages/AssetDetail'

function App() {
  return (
    <Router>
      <Layout>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/viewer/:fileId?" element={<IFCViewer />} />
          <Route path="/inspections" element={<Inspections />} />
          <Route path="/inspections/:id" element={<InspectionDetail />} />
          <Route path="/assets" element={<Assets />} />
          <Route path="/assets/:id" element={<AssetDetail />} />
        </Routes>
      </Layout>
    </Router>
  )
}

export default App

