async function loadDashboard() {

  const response = await fetch("/admin/dashboard")

  const data = await response.json()


  /* ===== metrics ===== */

  document.getElementById("metric-users").textContent =
    data.users

  document.getElementById("metric-active").textContent =
    data.active_users

  document.getElementById("metric-admins").textContent =
    data.admins

  document.getElementById("metric-requests").textContent =
    data.requests


  /* ===== system ===== */

  document.getElementById("metric-cpu").textContent =
    data.cpu + "%"

  document.getElementById("metric-memory").textContent =
    data.memory + "%"


  document.getElementById("cpu-bar").style.width =
    data.cpu + "%"

  document.getElementById("memory-bar").style.width =
    data.memory + "%"


  /* ===== chart ===== */

  const ctx = document
    .getElementById("activityChart")
    .getContext("2d")

  new Chart(ctx, {

    type: "line",

    data: {

      labels: [
        "Mon",
        "Tue",
        "Wed",
        "Thu",
        "Fri",
        "Sat",
        "Sun"
      ],

      datasets: [

        {

          label: "Activity",

          data: data.activity,

          borderColor: "#6366f1",

          backgroundColor:
            "rgba(99,102,241,0.1)",

          fill: true,

          tension: 0.4

        }

      ]

    },

    options: {

      plugins: {

        legend: {
          display: false
        }

      },

      responsive: true

    }

  })

}


document.addEventListener(
  "DOMContentLoaded",
  loadDashboard
)