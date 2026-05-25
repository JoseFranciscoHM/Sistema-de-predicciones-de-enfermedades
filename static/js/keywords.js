(function () {
  var disease = "dengue";
  var kwList = document.getElementById("kw-list");
  var kwInput = document.getElementById("kw-input");
  var kwAddBtn = document.getElementById("kw-add-btn");
  var kwRetrainBtn = document.getElementById("kw-retrain-btn");
  var kwCount = document.getElementById("kw-count");

  function getKeywords() {
    fetch(API_BASE_URL + "/api/keywords/" + disease)
      .then(function (r) { return r.json(); })
      .then(function (data) {
        renderKeywords(data.keywords || [], data.overrides || []);
      })
      .catch(function (err) {
        kwList.innerHTML = "<span style='color:#e74c3c'>Error: " + err.message + "</span>";
      });
  }

  function renderKeywords(allKw, overrides) {
    kwList.innerHTML = "";
    var overrideSet = {};
    overrides.forEach(function (kw) { overrideSet[kw] = true; });

    allKw.forEach(function (kw) {
      var tag = document.createElement("span");
      tag.className = "kw-tag" + (overrideSet[kw] ? " kw-tag-override" : " kw-tag-base");
      tag.textContent = kw;

      if (overrideSet[kw]) {
        var removeBtn = document.createElement("span");
        removeBtn.className = "kw-remove";
        removeBtn.textContent = "x";
        removeBtn.title = "Eliminar keyword";
        removeBtn.addEventListener("click", function () {
          fetch(API_BASE_URL + "/api/keywords/" + disease, {
            method: "DELETE",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ keyword: kw }),
          })
            .then(function (r) { return r.json(); })
            .then(function () { getKeywords(); })
            .catch(function (err) { alert("Error: " + err.message); });
        });
        tag.appendChild(removeBtn);
      }

      kwList.appendChild(tag);
    });

    kwCount.textContent = allKw.length;
  }

  kwAddBtn.addEventListener("click", function () {
    var kw = kwInput.value.trim();
    if (!kw) return;
    kwInput.value = "";
    kwInput.focus();

    fetch(API_BASE_URL + "/api/keywords/" + disease, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ keyword: kw }),
    })
      .then(function (r) { return r.json(); })
      .then(function () { getKeywords(); })
      .catch(function (err) { alert("Error: " + err.message); });
  });

  kwInput.addEventListener("keydown", function (e) {
    if (e.key === "Enter") kwAddBtn.click();
  });

  kwRetrainBtn.addEventListener("click", function () {
    kwRetrainBtn.disabled = true;
    kwRetrainBtn.textContent = "Reentrenando...";

    fetch(API_BASE_URL + "/api/retrain/" + disease, { method: "POST" })
      .then(function (r) { return r.json(); })
      .then(function (data) {
        alert(data.message);
        kwRetrainBtn.textContent = "Reentrenar modelo";
        kwRetrainBtn.disabled = false;
      })
      .catch(function (err) {
        alert("Error: " + err.message);
        kwRetrainBtn.textContent = "Reentrenar modelo";
        kwRetrainBtn.disabled = false;
      });
  });

  // Listen for disease tab changes
  document.addEventListener("DOMContentLoaded", function () {
    getKeywords();
  });

  document.querySelectorAll(".tab").forEach(function (tab) {
    tab.addEventListener("click", function () {
      disease = tab.dataset.disease;
      getKeywords();
    });
  });
})();
