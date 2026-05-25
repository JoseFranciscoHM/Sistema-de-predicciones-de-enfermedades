var DISEASE_COLORS = {
    hantavirus: "#e74c3c",
    covid: "#3498db",
    dengue: "#f39c12",
};

var DISEASE_NAMES = {
    hantavirus: "Hantavirus",
    covid: "COVID-19",
    dengue: "Dengue",
};

var currentDisease = "dengue";
var pollInterval = null;
var isInitialLoad = true;

async function fetchJSON(url) {
    var resp = await fetch(API_BASE_URL + url);
    if (!resp.ok) throw new Error("HTTP " + resp.status);
    return resp.json();
}

async function loadDashboard(disease) {
    var statusBar = document.getElementById("status-bar");
    statusBar.textContent = "Cargando datos epidemiologicos de " + DISEASE_NAMES[disease] + "...";

    try {
        var [dashboard, trends] = await Promise.all([
            fetchJSON("/api/dashboard/" + disease),
            fetchJSON("/api/search-trends/" + disease + "?days=180"),
        ]);

        renderTimeseries("timeseries-chart", dashboard.timeseries, DISEASE_COLORS[disease]);
        renderTrends("trends-chart", trends, DISEASE_COLORS[disease]);
        renderHeatmap("heatmap-chart", dashboard.municipality_data, disease);
        updatePredictionCard(dashboard.prediction);
        updateMetricsCard(dashboard.metrics);

        var totalCases = dashboard.timeseries.reduce(function (sum, d) {
            return sum + (d.confirmed_cases || 0);
        }, 0);

        var now = new Date().toLocaleTimeString("es-MX");
        statusBar.textContent =
            DISEASE_NAMES[disease] + " | Total casos (ultimo ano): " + totalCases +
            " | Ultima actualizacion: " + now;

        if (isInitialLoad) {
            isInitialLoad = false;
        }
    } catch (err) {
        statusBar.textContent = "Error cargando datos: " + err.message;
        console.error("Dashboard error:", err);
    }
}

function switchDisease(disease) {
    if (disease === currentDisease) return;
    currentDisease = disease;

    document.querySelectorAll(".tab").forEach(function (tab) {
        tab.classList.toggle("active", tab.dataset.disease === disease);
    });

    loadDashboard(disease);
}

function startPolling() {
    if (pollInterval) clearInterval(pollInterval);
    pollInterval = setInterval(function () {
        loadDashboard(currentDisease);
    }, 60000);
}

document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll(".tab").forEach(function (tab) {
        tab.addEventListener("click", function () { switchDisease(tab.dataset.disease); });
    });

    loadDashboard("dengue");
    startPolling();
});
