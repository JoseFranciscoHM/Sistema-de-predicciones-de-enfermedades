function renderTimeseries(containerId, data, diseaseColor) {
    if (!data || data.length === 0) {
        document.getElementById(containerId).innerHTML = '<p style="color:#8899aa;text-align:center;padding:2rem;">No hay datos disponibles</p>';
        return;
    }

    var dates = data.map(function (d) { return d.date; });
    var cases = data.map(function (d) { return d.confirmed_cases || 0; });
    var hosp = data.map(function (d) { return d.hospitalizations || 0; });
    var deaths = data.map(function (d) { return d.deaths || 0; });

    var traces = [
        {
            x: dates, y: cases, type: "scatter", mode: "lines+markers",
            name: "Casos Confirmados", line: { color: diseaseColor, width: 2 },
            marker: { size: 4 },
        },
        {
            x: dates, y: hosp, type: "scatter", mode: "lines+markers",
            name: "Hospitalizaciones", line: { color: "#ff9800", width: 2, dash: "dash" },
            marker: { size: 3 },
        },
        {
            x: dates, y: deaths, type: "scatter", mode: "lines+markers",
            name: "Defunciones", line: { color: "#e74c3c", width: 2, dash: "dot" },
            marker: { size: 3 },
        },
    ];

    var layout = {
        paper_bgcolor: "#1a2a3a",
        plot_bgcolor: "#1a2a3a",
        font: { color: "#8899aa", size: 11 },
        dragmode: "zoom",
        xaxis: {
            gridcolor: "#2a3a4a",
            title: "Fecha",
            rangeselector: {
                buttons: [
                    { count: 30, label: "1m", step: "day", stepmode: "backward" },
                    { count: 90, label: "3m", step: "day", stepmode: "backward" },
                    { count: 180, label: "6m", step: "day", stepmode: "backward" },
                    { count: 365, label: "1a", step: "day", stepmode: "backward" },
                    { step: "all" },
                ],
                bgcolor: "#1a2a3a",
                activecolor: "#4fc3f7",
            },
            rangeslider: { visible: true, bgcolor: "#0f1923" },
        },
        yaxis: { gridcolor: "#2a3a4a", title: "Numero de casos" },
        legend: { orientation: "h", y: 1.12 },
        margin: { l: 50, r: 20, t: 30, b: 50 },
    };

    Plotly.newPlot(containerId, traces, layout, {
        responsive: true,
        displayModeBar: true,
        modeBarButtonsToRemove: ["sendDataToCloud", "lasso2d"],
        modeBarButtonsToAdd: ["drawline", "eraseshape"],
    });
}

function renderTrends(containerId, data, diseaseColor) {
    var el = document.getElementById(containerId);
    if (!data || !data.series || data.series.length === 0) {
        el.innerHTML = '<p style="color:#8899aa;text-align:center;padding:2rem;">Sin datos de tendencias de busqueda</p>';
        return;
    }

    var traces = [];
    var colors = ["#4fc3f7", "#e74c3c", "#ff9800", "#4caf50", "#9c27b0", "#f44336", "#00bcd4", "#ffeb3b", "#795548", "#607d8b"];

    data.series.forEach(function (s, i) {
        var pts = s.data || [];
        if (pts.length === 0) return;
        var dates = pts.map(function (p) { return p.date; });
        var values = pts.map(function (p) { return p.value || 0; });
        traces.push({
            x: dates, y: values, type: "scatter", mode: "lines",
            name: s.keyword,
            line: { color: colors[i % colors.length], width: 1.5 },
        });
    });

    var layout = {
        paper_bgcolor: "#1a2a3a",
        plot_bgcolor: "#1a2a3a",
        font: { color: "#8899aa", size: 11 },
        dragmode: "zoom",
        xaxis: {
            gridcolor: "#2a3a4a",
            title: "Fecha",
            rangeselector: {
                buttons: [
                    { count: 30, label: "1m", step: "day", stepmode: "backward" },
                    { count: 90, label: "3m", step: "day", stepmode: "backward" },
                    { count: 180, label: "6m", step: "day", stepmode: "backward" },
                    { step: "all" },
                ],
                bgcolor: "#1a2a3a",
                activecolor: "#4fc3f7",
            },
            rangeslider: { visible: true, bgcolor: "#0f1923" },
        },
        yaxis: { gridcolor: "#2a3a4a", title: "Volumen de busqueda (0-100)", range: [0, 100] },
        legend: { orientation: "h", y: 1.12, font: { size: 9 } },
        margin: { l: 50, r: 20, t: 30, b: 50 },
    };

    Plotly.newPlot(containerId, traces, layout, {
        responsive: true,
        displayModeBar: true,
        modeBarButtonsToRemove: ["sendDataToCloud", "lasso2d"],
    });
}

function renderForecastChart(containerId, prediction, diseaseColor) {
    var el = document.getElementById(containerId);
    if (!prediction) {
        el.innerHTML = "";
        return;
    }

    var today = new Date();
    var labels = [];
    var cases = [];
    var ciLow = [];
    var ciHigh = [];
    for (var i = 1; i <= 7; i++) {
        var d = new Date(today);
        d.setDate(d.getDate() + i);
        labels.push(d.toLocaleDateString("es-MX", { weekday: "short", day: "numeric", month: "short" }));
        cases.push(prediction.estimated_cases_7d / 7);
        ciLow.push(prediction.ci_lower / 7);
        ciHigh.push(prediction.ci_upper / 7);
    }

    var trace = {
        x: labels,
        y: cases,
        type: "bar",
        name: "Casos estimados",
        marker: { color: diseaseColor, opacity: 0.8 },
        error_y: {
            type: "data",
            symmetric: false,
            array: ciHigh.map(function (v, i) { return v - cases[i]; }),
            arrayminus: cases.map(function (v, i) { return v - ciLow[i]; }),
            color: "#8899aa",
            thickness: 1.5,
            width: 3,
        },
    };

    var layout = {
        paper_bgcolor: "#1a2a3a",
        plot_bgcolor: "#1a2a3a",
        font: { color: "#8899aa", size: 9 },
        xaxis: { gridcolor: "#2a3a4a", tickangle: -45 },
        yaxis: { gridcolor: "#2a3a4a", title: "Casos / dia" },
        margin: { l: 40, r: 10, t: 10, b: 50 },
        showlegend: false,
        height: 130,
        bargap: 0.3,
    };

    Plotly.newPlot(containerId, [trace], layout, {
        responsive: true,
        displayModeBar: false,
        staticPlot: false,
    });
}

function renderHeatmap(containerId, municipalities, disease) {
    var el = document.getElementById(containerId);
    if (!municipalities || municipalities.length === 0) {
        el.innerHTML = '<p style="color:#8899aa;text-align:center;padding:2rem;">No hay datos de municipios</p>';
        return;
    }

    var names = municipalities.map(function (m) { return m.municipality; });
    var cases = municipalities.map(function (m) { return m.total_cases || 0; });
    var maxCases = Math.max.apply(null, cases.length ? cases : [1]);

    var colors = cases.map(function (c) {
        var ratio = maxCases > 0 ? c / maxCases : 0;
        if (ratio === 0) return "#1a2a3a";
        if (ratio < 0.05) return "#1b5e20";
        if (ratio < 0.15) return "#f57f17";
        if (ratio < 0.3) return "#e65100";
        return "#b71c1c";
    });

    var trace = {
        type: "bar",
        x: names,
        y: cases,
        marker: { color: colors },
        text: cases.map(function (c) { return c.toString(); }),
        textposition: "outside",
        hovertemplate: "%{x}<br>Casos: %{y}<extra></extra>",
    };

    var layout = {
        paper_bgcolor: "#1a2a3a",
        plot_bgcolor: "#1a2a3a",
        font: { color: "#8899aa", size: 10 },
        dragmode: "zoom",
        xaxis: {
            gridcolor: "#2a3a4a",
            tickangle: -90,
            title: "Municipio",
            automargin: true,
        },
        yaxis: { gridcolor: "#2a3a4a", title: "Casos" },
        margin: { l: 50, r: 20, t: 10, b: 200 },
        height: 500,
    };

    Plotly.newPlot(containerId, [trace], layout, {
        responsive: true,
        displayModeBar: true,
        modeBarButtonsToRemove: ["sendDataToCloud", "lasso2d"],
    });
}

function updatePredictionCard(prediction) {
    var probEl = document.querySelector("#prob-brote .metric-value");
    var casesEl = document.querySelector("#casos-estimados .metric-value");
    var icEl = document.querySelector("#ic .metric-value");

    if (!prediction) {
        probEl.textContent = "N/A";
        casesEl.textContent = "N/A";
        icEl.textContent = "N/A";
        renderForecastChart("forecast-chart", null, "#4fc3f7");
        return;
    }

    var prob = (prediction.outbreak_probability * 100).toFixed(1);
    probEl.textContent = prob + "%";
    probEl.style.color = prediction.outbreak_probability > 0.5 ? "#e74c3c" : "#4fc3f7";

    casesEl.textContent = prediction.estimated_cases_7d.toFixed(0);
    icEl.textContent = "[" + prediction.ci_lower.toFixed(0) + " - " + prediction.ci_upper.toFixed(0) + "]";

    renderForecastChart("forecast-chart", prediction, "#4fc3f7");
}

function updateMetricsCard(metrics) {
    if (!metrics) {
        document.querySelectorAll("#metrics-content .metric-value").forEach(function (el) { el.textContent = "--"; });
        return;
    }
    document.getElementById("m-sens").textContent = (metrics.sensitivity * 100).toFixed(1) + "%";
    document.getElementById("m-spec").textContent = (metrics.specificity * 100).toFixed(1) + "%";
    document.getElementById("m-rmse").textContent = metrics.rmse.toFixed(1);
    document.getElementById("m-prec").textContent = (metrics.precision * 100).toFixed(1) + "%";
    if (metrics.trained_at) {
        document.getElementById("m-trained").textContent = new Date(metrics.trained_at).toLocaleDateString("es-MX");
    } else {
        document.getElementById("m-trained").textContent = metrics.trained_at || "--";
    }
}
