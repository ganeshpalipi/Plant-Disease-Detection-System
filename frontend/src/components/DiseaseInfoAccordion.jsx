import { useState } from 'react'

const SECTIONS = [
  { key: 'symptoms', label: 'Symptoms', icon: '🔍' },
  { key: 'causes', label: 'Causes', icon: '🧬' },
  { key: 'treatment', label: 'Treatment', icon: '💊' },
  { key: 'prevention', label: 'Prevention', icon: '🛡️' },
]

function DiseaseInfoAccordion({ result }) {
  const [openKey, setOpenKey] = useState('symptoms')

  return (
    <div className="mt-6 space-y-4">
      <div className="rounded-2xl border border-gray-200 bg-white p-6 shadow-sm">
        <h3 className="mb-2 text-lg font-semibold text-gray-900">Description</h3>
        <p className="leading-relaxed text-gray-600">{result.description}</p>
      </div>

      <div className="divide-y divide-gray-200 overflow-hidden rounded-2xl border border-gray-200 bg-white shadow-sm">
        {SECTIONS.map(({ key, label, icon }) => {
          const items = result[key] ?? []
          const isOpen = openKey === key

          return (
            <div key={key}>
              <button
                type="button"
                onClick={() => setOpenKey(isOpen ? null : key)}
                className="flex w-full items-center justify-between px-6 py-4 text-left transition-colors hover:bg-gray-50"
                aria-expanded={isOpen}
              >
                <span className="flex items-center gap-3 font-semibold text-gray-800">
                  <span aria-hidden="true">{icon}</span>
                  {label}
                </span>
                <span className={`text-gray-400 transition-transform ${isOpen ? 'rotate-180' : ''}`}>▾</span>
              </button>

              {isOpen && (
                <ul className="animate-fade-in space-y-2 px-6 pb-5 text-gray-600">
                  {items.map((item, index) => (
                    <li key={index} className="flex gap-2">
                      <span className="mt-1.5 h-1.5 w-1.5 flex-shrink-0 rounded-full bg-primary-500" />
                      <span>{item}</span>
                    </li>
                  ))}
                </ul>
              )}
            </div>
          )
        })}
      </div>
    </div>
  )
}

export default DiseaseInfoAccordion
