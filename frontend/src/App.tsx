import { BrowserRouter, Routes, Route } from 'react-router-dom'
import { AnimatePresence } from 'framer-motion'
import LandingPage from './features/landing/pages/LandingPage'
import QueryPage from './features/query/pages/QueryPage'

export default function App() {
  return (
    <BrowserRouter>
      <AnimatePresence mode="wait">
        <Routes>
          <Route path="/" element={<LandingPage />} />
          <Route path="/query" element={<QueryPage />} />
        </Routes>
      </AnimatePresence>
    </BrowserRouter>
  )
}
