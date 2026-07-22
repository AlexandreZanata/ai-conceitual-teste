(() => {
  const statusEl = document.getElementById("status");
  const labels = [];
  const meanData = [];
  const maxData = [];
  let experimentId = null;

  const chart = new Chart(document.getElementById("chart"), {
    type: "line",
    data: {
      labels,
      datasets: [
        { label: "fitness_mean", data: meanData, borderColor: "#3d9a7a", tension: 0.15 },
        { label: "fitness_max", data: maxData, borderColor: "#c4a35a", tension: 0.15 },
      ],
    },
    options: {
      animation: false,
      scales: {
        x: { title: { display: true, text: "generation" } },
        y: { title: { display: true, text: "fitness" } },
      },
    },
  });

  function setStatus(text) {
    statusEl.textContent = text;
  }

  function resetChart() {
    labels.length = 0;
    meanData.length = 0;
    maxData.length = 0;
    chart.update();
  }

  function onGeneration(msg) {
    labels.push(String(msg.generation));
    meanData.push(msg.fitness_mean);
    maxData.push(msg.fitness_max);
    chart.update();
    const alive =
      msg.alive_mean === undefined ? "" : ` alive=${msg.alive_mean.toFixed(2)}`;
    setStatus(
      `gen ${msg.generation} mean=${msg.fitness_mean.toFixed(4)} max=${msg.fitness_max.toFixed(4)}${alive}`
    );
  }

  function buildStartBody() {
    const condition = document.getElementById("condition").value;
    const environment = document.getElementById("environment").value;
    const learning = condition === "A" ? 0.0 : 0.01;
    const body = {
      condition,
      environment,
      population_size: 20,
      max_generations: Number(document.getElementById("gens").value),
      seed: Number(document.getElementById("seed").value),
      inheritance_mode: "Darwinian",
      initial_mutation_rate: condition === "B" ? 0.0 : 0.05,
      initial_learning_rate: learning,
      genome_size: 8,
      generation_delay_ms: 40,
    };
    if (environment === "survival_arena") {
      Object.assign(body, {
        grid_w: 16,
        grid_h: 16,
        food_density: 0.08,
        energy_drain: 0.05,
        hazard_rate: 0.02,
        start_energy: 1.0,
        episode_ticks: 32,
      });
    } else {
      Object.assign(body, { function_task: "xor", episode_length: 4 });
    }
    return body;
  }

  const wsProto = location.protocol === "https:" ? "wss" : "ws";
  const ws = new WebSocket(`${wsProto}://${location.host}/ws/metrics`);
  ws.onmessage = (ev) => {
    const msg = JSON.parse(ev.data);
    if (msg.type === "generation") onGeneration(msg);
  };
  ws.onopen = () => setStatus("ws connected — idle");
  ws.onclose = () => setStatus("ws disconnected");

  async function post(path, body) {
    const res = await fetch(path, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: body ? JSON.stringify(body) : undefined,
    });
    const data = await res.json().catch(() => ({}));
    if (!res.ok) throw new Error(data.error?.message || res.statusText);
    return data;
  }

  document.getElementById("start").onclick = async () => {
    try {
      resetChart();
      const data = await post("/experiments", buildStartBody());
      experimentId = data.experiment_id;
      setStatus(`running ${experimentId}`);
    } catch (err) {
      setStatus(`error: ${err.message}`);
    }
  };

  async function lifecycle(action) {
    if (!experimentId) {
      setStatus("no experiment");
      return;
    }
    try {
      const data = await post(`/experiments/${experimentId}/${action}`);
      setStatus(`${data.status} ${experimentId}`);
    } catch (err) {
      setStatus(`error: ${err.message}`);
    }
  }

  document.getElementById("pause").onclick = () => lifecycle("pause");
  document.getElementById("resume").onclick = () => lifecycle("resume");
  document.getElementById("stop").onclick = () => lifecycle("stop");
})();
