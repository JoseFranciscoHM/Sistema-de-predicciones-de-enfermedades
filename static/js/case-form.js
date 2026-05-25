(function () {
  var municipios = [
    "Ahualulco","Alaquines","Aquismon","Armadillo de los Infante",
    "Axtla de Terrazas","Cardenas","Catorce","Cedral","Cerritos",
    "Cerro de San Pedro","Charcas","Ciudad del Maiz","Ciudad Fernandez",
    "Ciudad Valles","Coxcatlan","Ebano","El Naranjo","Guadalcazar",
    "Huehuetlan","Lagunillas","Matehuala","Matlapa",
    "Mexquitic de Carmona","Moctezuma","Rayon","Rioverde","Salinas",
    "San Antonio","San Ciro de Acosta","San Luis Potosi",
    "San Martin Chalchicuautla","San Nicolas Tolentino",
    "San Vicente Tancuayalab","Santa Catarina","Santa Maria del Rio",
    "Santo Domingo","Soledad de Graciano Sanchez","Tamasopo",
    "Tamazunchale","Tampacan","Tampamolon Corona","Tamuin",
    "Tancanhuitz","Tanlajas","Tanquian de Escobedo","Tierra Nueva",
    "Vanegas","Venado","Villa de Arista","Villa de Arriaga",
    "Villa de Guadalupe","Villa de la Paz","Villa de Ramos",
    "Villa de Reyes","Villa Hidalgo","Villa Juarez","Xilitla","Zaragoza",
  ];

  var select = document.getElementById("form-municipality");
  var form = document.getElementById("case-form");
  var statusEl = document.getElementById("form-status");
  var submitBtn = document.getElementById("form-submit");
  var dateInput = document.getElementById("form-date");

  municipios.forEach(function (m) {
    var opt = document.createElement("option");
    opt.value = m;
    opt.textContent = m;
    select.appendChild(opt);
  });

  dateInput.value = new Date().toISOString().slice(0, 10);

  // Toggle severity fields based on disease
  document.getElementById("form-disease").addEventListener("change", function () {
    var v = this.value;
    document.getElementById("severity-dengue").style.display = v === "dengue" ? "block" : "none";
    document.getElementById("severity-hantavirus").style.display = v === "hantavirus" ? "block" : "none";
  });

  form.addEventListener("submit", async function (e) {
    e.preventDefault();
    submitBtn.disabled = true;
    statusEl.textContent = "Enviando...";
    statusEl.style.color = "#8899aa";

    // Collect symptoms
    var symptoms = [];
    document.querySelectorAll(".symptom-cb:checked").forEach(function (cb) {
      symptoms.push(cb.value);
    });

    var disease = document.getElementById("form-disease").value;
    var body = {
      disease: disease,
      municipality: select.value,
      date: dateInput.value,
      confirmed_cases: parseInt(document.getElementById("form-cases").value) || 0,
      hospitalizations: parseInt(document.getElementById("form-hosp").value) || 0,
      deaths: parseInt(document.getElementById("form-deaths").value) || 0,
      reporter_name: document.getElementById("form-reporter").value,
      symptoms: symptoms.join(", "),
      hantavirus_type: document.getElementById("form-hantavirus-type")
        ? document.getElementById("form-hantavirus-type").value
        : "",
      dengue_severity: document.getElementById("form-dengue-severity")
        ? document.getElementById("form-dengue-severity").value
        : "",
      auto_retrain: document.getElementById("form-autoretrain").checked,
    };

    try {
      var resp = await fetch(API_BASE_URL + "/api/cases", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });

      var data = await resp.json();
      if (resp.ok) {
        statusEl.textContent = data.message;
        statusEl.style.color = "#4caf50";
        document.getElementById("form-cases").value = "0";
        document.getElementById("form-hosp").value = "0";
        document.getElementById("form-deaths").value = "0";
        document.getElementById("form-reporter").value = "";
        document.querySelectorAll(".symptom-cb").forEach(function (cb) { cb.checked = false; });
        document.getElementById("form-dengue-severity").value = "";
        document.getElementById("form-hantavirus-type").value = "";
        document.getElementById("form-autoretrain").checked = false;
        // Refresh dashboard after submission
        setTimeout(function () { loadDashboard(currentDisease); }, 1000);
      } else {
        statusEl.textContent = "Error: " + (data.detail || "desconocido");
        statusEl.style.color = "#e74c3c";
      }
    } catch (err) {
      statusEl.textContent = "Error de conexion: " + err.message;
      statusEl.style.color = "#e74c3c";
    } finally {
      submitBtn.disabled = false;
    }
  });
})();
