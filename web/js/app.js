const COI_COLOR = "#1f77b4";
const EDO_COLOR = "#d62728";
const LUMP_COLOR = "#c7c7c7";

const els = {
  lump: document.getElementById("lump"),
  lumpN: document.getElementById("lump-n"),
  hz: document.getElementById("hz"),
  hzVal: document.getElementById("hz-val"),
  inf: document.getElementById("inf"),
  infN: document.getElementById("inf-n"),
  belka: document.getElementById("belka"),
  status: document.getElementById("status"),
  tableBody: document.getElementById("table-body"),
  kpiCoiWallet: document.getElementById("kpi-coi-wallet"),
  kpiEdoWallet: document.getElementById("kpi-edo-wallet"),
  kpiCoiProfit: document.getElementById("kpi-coi-profit"),
  kpiEdoProfit: document.getElementById("kpi-edo-profit"),
  kpiDelta: document.getElementById("kpi-delta"),
};

let chart;
let pyodide = null;
let runToken = 0;

function money(n) {
  return (
    n.toLocaleString("pl-PL", {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    }) + " PLN"
  );
}

function setStatus(text, isError = false) {
  els.status.textContent = text;
  els.status.classList.toggle("error", isError);
}

function readControls() {
  return {
    lumpSum: Number(els.lumpN.value),
    horizon: Number(els.hz.value),
    inflationPct: Number(els.infN.value),
    belka: els.belka.checked,
  };
}

function pathFromDict(path, lumpSum) {
  return {
    years: path.years,
    wallet: path.wallet,
    profit: path.wallet.map((w) => w - lumpSum),
    exit_profit: path.exit_profit,
    income: path.income,
    bonds: path.bonds,
    idle: path.idle,
    rolls: path.rolls,
    exit_fee: path.exit_fee,
    exit_tax: path.exit_tax,
    exit_income: path.exit_income,
    final_wallet: path.final_wallet,
    profit_total: path.profit_total,
  };
}

function resultToView(raw, lumpSum) {
  return {
    coi: pathFromDict(raw.coi, lumpSum),
    edo: pathFromDict(raw.edo, lumpSum),
    delta: raw.delta,
  };
}

function updateKpis(view) {
  els.kpiCoiWallet.textContent = money(view.coi.final_wallet);
  els.kpiEdoWallet.textContent = money(view.edo.final_wallet);
  els.kpiCoiProfit.textContent = money(view.coi.profit_total);
  els.kpiEdoProfit.textContent = money(view.edo.profit_total);
  els.kpiDelta.textContent = money(view.delta);
}

function updateTable(view) {
  const rows = view.coi.years
    .map((year, i) => {
      const bool = (v) => (v ? "yes" : "");
      const n = (v) => Number(v).toFixed(2);
      return `<tr>
        <td>${year}</td>
        <td>${n(view.coi.wallet[i])}</td>
        <td>${n(view.coi.income[i])}</td>
        <td>${view.coi.bonds[i]}</td>
        <td>${n(view.coi.idle[i])}</td>
        <td>${bool(view.coi.rolls[i])}</td>
        <td>${n(view.coi.exit_fee[i])}</td>
        <td>${n(view.coi.exit_tax[i])}</td>
        <td>${n(view.coi.exit_income[i])}</td>
        <td>${n(view.coi.exit_profit[i])}</td>
        <td>${n(view.edo.wallet[i])}</td>
        <td>${n(view.edo.income[i])}</td>
        <td>${view.edo.bonds[i]}</td>
        <td>${n(view.edo.idle[i])}</td>
        <td>${bool(view.edo.rolls[i])}</td>
        <td>${n(view.edo.exit_fee[i])}</td>
        <td>${n(view.edo.exit_tax[i])}</td>
        <td>${n(view.edo.exit_income[i])}</td>
        <td>${n(view.edo.exit_profit[i])}</td>
      </tr>`;
    })
    .join("");
  els.tableBody.innerHTML = rows;
}

function drawChart(view, lumpSum) {
  const ctx = document.getElementById("chart");
  const labels = view.coi.years.map(String);
  const lump = labels.map(() => lumpSum);
  const data = {
    labels,
    datasets: [
      {
        type: "bar",
        label: "lump sum",
        data: lump,
        backgroundColor: LUMP_COLOR,
        stack: "coi",
        yAxisID: "y",
        order: 2,
      },
      {
        type: "bar",
        label: "COI profit",
        data: view.coi.profit,
        backgroundColor: COI_COLOR,
        stack: "coi",
        yAxisID: "y",
        order: 2,
      },
      {
        type: "bar",
        label: "lump sum ",
        data: lump,
        backgroundColor: LUMP_COLOR,
        stack: "edo",
        yAxisID: "y",
        order: 2,
        legend: { display: false },
      },
      {
        type: "bar",
        label: "EDO profit",
        data: view.edo.profit,
        backgroundColor: EDO_COLOR,
        stack: "edo",
        yAxisID: "y",
        order: 2,
      },
      {
        type: "line",
        label: "COI exit profit",
        data: view.coi.exit_profit,
        borderColor: COI_COLOR,
        backgroundColor: COI_COLOR,
        pointStyle: "circle",
        pointRadius: 4,
        yAxisID: "y1",
        tension: 0.15,
        order: 1,
      },
      {
        type: "line",
        label: "EDO exit profit",
        data: view.edo.exit_profit,
        borderColor: EDO_COLOR,
        backgroundColor: EDO_COLOR,
        borderDash: [6, 4],
        pointStyle: "rect",
        pointRadius: 4,
        yAxisID: "y1",
        tension: 0.15,
        order: 1,
      },
    ],
  };
  const options = {
    responsive: true,
    maintainAspectRatio: false,
    interaction: { mode: "index", intersect: false },
    plugins: {
      title: {
        display: true,
        text: "COI vs EDO — wallet composition + exit profit",
      },
      legend: {
        position: "top",
        labels: {
          filter: (item) => item.text.trim() !== "lump sum" || item.datasetIndex === 0,
        },
      },
    },
    scales: {
      x: { title: { display: true, text: "Year" } },
      y: {
        position: "left",
        stacked: true,
        title: { display: true, text: "Wallet (PLN)" },
      },
      y1: {
        position: "right",
        title: { display: true, text: "Exit profit (PLN)" },
        grid: { drawOnChartArea: false },
      },
    },
  };
  if (chart) {
    chart.data = data;
    chart.options = options;
    chart.update();
    return;
  }
  chart = new Chart(ctx, { data, options });
}

function render(view, lumpSum) {
  updateKpis(view);
  updateTable(view);
  drawChart(view, lumpSum);
}

function recompute() {
  if (!pyodide) return;
  const token = ++runToken;
  const { lumpSum, horizon, inflationPct, belka } = readControls();
  els.hzVal.textContent = String(horizon);
  try {
    pyodide.globals.set("bw_lump", lumpSum);
    pyodide.globals.set("bw_horizon", horizon);
    pyodide.globals.set("bw_inflation", inflationPct / 100.0);
    pyodide.globals.set("bw_belka", belka);
    const rawJson = pyodide.runPython(`
import json
from bondwise import simulate
_r = simulate(bw_lump, bw_horizon, bw_inflation, bw_belka)

def _path(p):
    return {
        "years": [y.year for y in p.years],
        "wallet": [y.wallet for y in p.years],
        "income": [y.income for y in p.years],
        "bonds": [y.bonds for y in p.years],
        "idle": [y.idle_cash for y in p.years],
        "rolls": [y.is_roll for y in p.years],
        "exit_fee": [y.exit.fee for y in p.years],
        "exit_tax": [y.exit.tax for y in p.years],
        "exit_income": [y.exit.income for y in p.years],
        "exit_profit": [y.exit.profit for y in p.years],
        "final_wallet": p.final_wallet,
        "profit_total": p.profit,
    }

json.dumps({
    "coi": _path(_r.coi),
    "edo": _path(_r.edo),
    "delta": _r.delta_edo_minus_coi,
})
`);
    if (token !== runToken) return;
    const view = resultToView(JSON.parse(rawJson), lumpSum);
    render(view, lumpSum);
    setStatus("Ready");
  } catch (err) {
    console.error(err);
    setStatus(`Simulate failed: ${err}`, true);
  }
}

function bindControls() {
  const syncPair = (range, number, parse) => {
    const apply = (raw, source) => {
      const value = parse(raw);
      range.value = value;
      number.value = value;
      if (source === "range" || source === "number") recompute();
    };
    range.addEventListener("input", () => apply(range.value, "range"));
    number.addEventListener("input", () => apply(number.value, "number"));
  };
  syncPair(els.lump, els.lumpN, (v) => {
    const n = Number(v);
    return Number.isFinite(n) ? Math.max(0, Math.min(500000, Math.round(n))) : 0;
  });
  els.hz.addEventListener("input", () => {
    els.hzVal.textContent = els.hz.value;
    recompute();
  });
  syncPair(els.inf, els.infN, (v) => {
    const n = Number(v);
    if (!Number.isFinite(n)) return 0;
    return Math.max(0, Math.min(15, Math.round(n * 10) / 10));
  });
  els.belka.addEventListener("change", recompute);
}

async function boot() {
  bindControls();
  setStatus("Loading Pyodide…");
  try {
    pyodide = await loadPyodide();
    setStatus("Fetching simulator package…");
    const zipUrl = new URL("pkg/bondwise-sim.zip", document.baseURI);
    const zip = await (await fetch(zipUrl)).arrayBuffer();
    pyodide.unpackArchive(zip, "zip");
    pyodide.runPython("import importlib; importlib.invalidate_caches()");
    setStatus("Running…");
    recompute();
  } catch (err) {
    console.error(err);
    setStatus(`Boot failed: ${err}`, true);
  }
}

boot();
