document.addEventListener("DOMContentLoaded", () => {
  initLoader()
  initGlobalSearch()
  initSafeAlert()
  initSafeDeleteHandler()
  bindSqladminSafeErrors()
})

function initLoader() {
  const loader = document.getElementById("admin-loader")
  if (!loader) return

  loader.style.transform = "scaleX(1)"
  window.addEventListener("load", () => {
    loader.style.transform = "scaleX(0)"
  })
}

function adminToast(message) {
  const toast = document.createElement("div")
  toast.className = "admin-toast"
  toast.innerText = message
  document.body.appendChild(toast)

  requestAnimationFrame(() => {
    toast.classList.add("show")
  })

  setTimeout(() => {
    toast.classList.remove("show")
    setTimeout(() => toast.remove(), 200)
  }, 2200)
}

function initGlobalSearch() {
  const miniSearch = document.getElementById("admin-search-mini")
  if (!miniSearch) return

  document.addEventListener("keydown", (event) => {
    if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === "k") {
      event.preventDefault()
      miniSearch.focus()
    }
  })

  miniSearch.addEventListener("keydown", (event) => {
    if (event.key !== "Enter") return

    const value = miniSearch.value.trim()
    if (!value) {
      adminToast("Enter a search query")
      return
    }

    const url = new URL(window.location.href)
    if (!url.pathname.includes("/list")) {
      url.pathname = "/admin/user/list"
    }

    url.searchParams.set("search", value)
    window.location.href = url.toString()
  })
}

function initSafeDeleteHandler() {
  document.addEventListener(
    "click",
    async (event) => {
      const target = event.target
      if (!(target instanceof Element)) return

      const button = target.closest("#modal-delete-button")
      if (!button) return

      event.preventDefault()
      event.stopPropagation()
      event.stopImmediatePropagation()

      const deleteUrl = button.getAttribute("data-url")
    if (!deleteUrl) return

      try {
        const response = await fetch(deleteUrl, {
          method: "DELETE",
          credentials: "same-origin",
          headers: {
            Accept: "application/json, text/plain, */*",
          },
        })

        if (response.ok) {
          const redirectUrl = await response.text()
          window.location.href = redirectUrl
          return
        }

        let message = `Operation failed (${response.status}).`
        try {
          const json = await response.json()
          if (typeof json.detail === "string" && json.detail.trim()) {
            message = json.detail
          }
        } catch {
          // keep generic non-sensitive text
        }

        adminToast(message)
      } catch {
        adminToast("Network error while processing delete operation.")
      } finally {
        if (typeof window.$ === "function") {
          window.$("#modal-delete").modal("hide")
        }
      }
    },
    true,
  )
}

function initSafeAlert() {
  const originalAlert = window.alert.bind(window)

  window.alert = (message) => {
    const text = String(message ?? "")
    if (text.includes("Traceback") || text.includes("site-packages")) {
      adminToast("Operation failed. You do not have access for this action.")
      return
    }

    originalAlert(text)
  }
}

function bindSqladminSafeErrors() {
  window.addEventListener("admin:safe-error", (event) => {
    const message = event?.detail?.message || "Operation failed."
    adminToast(String(message))
  })
}
