document.addEventListener('DOMContentLoaded', () => {
  for (const form of document.querySelectorAll('.family-quota')) {
    const card = form.closest('.family-account')
    const amount = form.elements.amount
    form.elements.unit.addEventListener('change', () => {
      amount.disabled = form.elements.unit.value === 'default'
    })
    form.addEventListener('submit', async event => {
      event.preventDefault()
      const status = card.querySelector('[role=status]')
      const button = form.querySelector('button')
      button.disabled = true
      try {
        const response = await fetch(form.action, {
          method: 'POST', headers: {requesttoken: OC.requestToken}, body: new FormData(form)
        })
        if (!response.ok) throw new Error()
        const {quota} = await response.json()
        card.querySelector('[data-metric=quota]').textContent = quota === 'none' ? 'Sans limite' : quota
        status.textContent = 'Quota enregistré.'
      } catch {
        status.textContent = 'Enregistrement impossible. Vérifiez la limite et votre session.'
      } finally {
        button.disabled = false
      }
    })
  }
})
