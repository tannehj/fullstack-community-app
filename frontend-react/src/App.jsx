import Community from './Community.jsx'
import Resources from './Resources.jsx'

import { useState } from 'react'

const sections = {
  community: {
    title: 'Community',
    description: 'Share your stories, experiences, and recommendations.',
  },
  resources: {
    title: 'Resources',
    description: 'Find documents and articles explained in simple language.',
  },
  directory: {
    title: 'Directory',
    description: 'Discover African restaurants and stores by city.',
  },
}

function App() {
  const [activeSection, setActiveSection] = useState('community')
  const currentSection = sections[activeSection]

  return (
    <>
      <header>
        <h1>Immigrants Hub</h1>
       <p>Connect, find useful resources, and discover African businesses across the U.S.</p>

        <nav aria-label="Main navigation">
          {Object.entries(sections).map(([key, section]) => (
            <button
              key={key}
              type="button"
              aria-pressed={activeSection === key}
              onClick={() => setActiveSection(key)}
            >
              {section.title}
            </button>
          ))}
        </nav>
      </header>

      <main>
        {activeSection === 'community' ? (
          <Community />
        ) : activeSection === 'resources' ? (
          <Resources />
        ) : (
          <section>
            <h2>{currentSection.title}</h2>
            <p>{currentSection.description}</p>
          </section>
        )}
      </main>
    </>
  )
}

export default App