import { ReactNode } from 'react'
import { Link, useLocation } from 'react-router-dom'
import './Layout.css'

interface LayoutProps {
  children: ReactNode
}

export default function Layout({ children }: LayoutProps) {
  const location = useLocation()

  const isActive = (path: string) => location.pathname.startsWith(path)

  return (
    <div className="layout">
      <nav className="navbar">
        <div className="navbar-brand">
          <h1>BIM-FM Platform</h1>
        </div>
        <ul className="navbar-nav">
          <li>
            <Link to="/" className={isActive('/') && location.pathname === '/' ? 'active' : ''}>
              Dashboard
            </Link>
          </li>
          <li>
            <Link to="/viewer" className={isActive('/viewer') ? 'active' : ''}>
              Visualizador 3D
            </Link>
          </li>
          <li>
            <Link to="/assets" className={isActive('/assets') ? 'active' : ''}>
              Ativos
            </Link>
          </li>
          <li>
            <Link to="/inspections" className={isActive('/inspections') ? 'active' : ''}>
              Inspeções
            </Link>
          </li>
        </ul>
      </nav>
      <main className="main-content">
        {children}
      </main>
    </div>
  )
}

