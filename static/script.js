document.getElementById("find-btn").addEventListener("click", function () {
    var start = document.getElementById("start").value.trim();
    var end = document.getElementById("end").value.trim();
    var results = document.getElementById("results");
    var loading = document.getElementById("loading");
    var timer = document.getElementById("timer");
    var btn = document.getElementById("find-btn");

    results.textContent = "";
    results.innerHTML = "";
    results.className = "";

    if (!start || !end) {
        results.className = "error";
        results.textContent = "Please enter both a start and end article.";
        return;
    }

    loading.style.display = "block";
    btn.disabled = true;

    var seconds = 0;
    timer.textContent = "0s";
    var timerInterval = setInterval(function () {
        seconds++;
        timer.textContent = seconds + "s";
    }, 1000);

    var controller = new AbortController();
    var timeoutId = setTimeout(function () {
        controller.abort();
    }, 90000);

    fetch("/api/find-path", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ start: start, end: end }),
        signal: controller.signal,
    })
        .then(function (resp) {
            clearTimeout(timeoutId);
            clearInterval(timerInterval);
            return resp.json().then(function (data) {
                return { ok: resp.ok, data: data };
            });
        })
        .then(function (result) {
            loading.style.display = "none";
            btn.disabled = false;

            if (!result.ok || !result.data.success) {
                results.className = "error";
                results.textContent = result.data.message || "Search failed.";
                return;
            }

            results.className = "success";
            var path = result.data.path;
            results.innerHTML = "";
            for (var i = 0; i < path.length; i++) {
                var a = document.createElement("a");
                a.href = "https://en.wikipedia.org/wiki/" + encodeURIComponent(path[i]);
                a.textContent = path[i];
                a.target = "_blank";
                results.appendChild(a);
                if (i < path.length - 1) {
                    results.appendChild(document.createTextNode(" \u2192 "));
                }
            }
        })
        .catch(function (error) {
            clearTimeout(timeoutId);
            clearInterval(timerInterval);
            loading.style.display = "none";
            btn.disabled = false;
            results.className = "error";
            if (error.name === "AbortError") {
                results.textContent = "The search is taking too long. Please try again.";
            } else {
                results.textContent = "Something went wrong. Please try again.";
            }
        });
});
