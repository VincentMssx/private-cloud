document.addEventListener('DOMContentLoaded', () => {
  const root = document.querySelector('#family-review')
  const status = document.querySelector('#tri-status')
  for (const section of root.querySelectorAll('.serie')) {
    const checks = Array.from(section.querySelectorAll('input[type=checkbox]'))
    const discard = section.querySelector('.discard')
    const ignore = section.querySelector('.ignore')
    function update() {
      const count = checks.filter(el => el.checked).length
      discard.disabled = count === 0 || (checks.length > 1 && count === checks.length)
      discard.textContent = count ? 'Mettre à la corbeille (' + count + ')' : 'Confirmer la sélection'
    }
    section.addEventListener('change', update)
    section.addEventListener('click', async event => {
      const button = event.target
      if (button !== ignore && button !== discard) return
      const selected = checks.filter(el => el.checked)
      if (button === discard && !window.confirm('Mettre les ' + selected.length + ' photo(s) sélectionnée(s) à la corbeille pendant 30 jours ?')) return
      for (const el of [...checks, discard, ignore]) el.disabled = true
      const headers = { requesttoken: OC.requestToken }
      try {
        if (button === ignore) {
          const response = await fetch(root.dataset.ignore, {method: 'POST', headers,
            body: new URLSearchParams({key: section.dataset.key})})
          if (!response.ok) throw new Error()
        } else {
          for (const el of selected) {
            const response = await fetch(el.dataset.url, {method: 'DELETE',
              headers: {...headers, 'If-Match': '"' + el.dataset.etag + '"'}})
            if (!response.ok) throw new Error()
          }
        }
        window.location.reload()
      } catch {
        status.textContent = 'Action interrompue. Rechargez la page pour vérifier les photos restantes.'
        status.scrollIntoView()
      }
    })
  }
})
