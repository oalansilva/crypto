const http = require("http");
const { execFile } = require("child_process");
const fs = require("fs");
const path = require("path");
const ExcelJS = require("exceljs");

const PORT = Number(process.env.PORT || 5174);
const HOST = process.env.HOST || "0.0.0.0";
const DRIVE_FILE_ID = process.env.DRIVE_FILE_ID || "";
const TELEGRAM_TARGET = process.env.TELEGRAM_TARGET || "";
const TELEGRAM_THREAD_ID = process.env.TELEGRAM_THREAD_ID || "";
const TELEGRAM_BOT_TOKEN = process.env.TELEGRAM_BOT_TOKEN || "";
const EMAIL_TO = process.env.EMAIL_TO || "";
const BACKEND_LEADS_ENDPOINT = process.env.BACKEND_LEADS_ENDPOINT || "http://127.0.0.1:8003/api/leads";
const LEADS_FILE = process.env.LEADS_FILE || path.join(__dirname, "data", "leads-cripto-farol.xlsx");
const ALLOWED_ORIGINS = (process.env.ALLOWED_ORIGINS ||
  "https://criptofarol.com.br,https://www.criptofarol.com.br,http://72.60.150.140:5173,http://localhost:5173,http://127.0.0.1:5173")
  .split(",")
  .map((origin) => origin.trim())
  .filter(Boolean);

const HEADERS = ["Data", "Nome", "Email", "WhatsApp", "Perfil", "Dificuldade", "Origem"];
const LEGACY_HEADERS = ["Data", "Nome", "Email", "Perfil", "Dificuldade", "Origem"];
let queue = Promise.resolve();

function corsHeaders(origin) {
  const allowedOrigin = ALLOWED_ORIGINS.includes(origin) ? origin : ALLOWED_ORIGINS[0];
  return {
    "Access-Control-Allow-Origin": allowedOrigin,
    "Access-Control-Allow-Methods": "POST, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type",
    Vary: "Origin",
  };
}

function sendJson(res, status, body, origin) {
  res.writeHead(status, {
    "Content-Type": "application/json; charset=utf-8",
    ...corsHeaders(origin),
  });
  res.end(JSON.stringify(body));
}

function readBody(req) {
  return new Promise((resolve, reject) => {
    let body = "";
    req.on("data", (chunk) => {
      body += chunk;
      if (body.length > 20_000) {
        reject(new Error("payload_too_large"));
        req.destroy();
      }
    });
    req.on("end", () => resolve(body));
    req.on("error", reject);
  });
}

function clean(value) {
  return String(value || "").trim().replace(/\s+/g, " ");
}

async function ensureWorkbook() {
  fs.mkdirSync(path.dirname(LEADS_FILE), { recursive: true });
  const workbook = new ExcelJS.Workbook();
  if (fs.existsSync(LEADS_FILE)) {
    await workbook.xlsx.readFile(LEADS_FILE);
    return workbook;
  }

  const sheet = workbook.addWorksheet("Leads");
  sheet.addRow(HEADERS);
  await workbook.xlsx.writeFile(LEADS_FILE);
  return workbook;
}

function rowValues(row) {
  return row.values.slice(1).map((value) => (value == null ? "" : String(value)));
}

async function appendLead(lead) {
  const workbook = await ensureWorkbook();
  const sheet = workbook.worksheets[0] || workbook.addWorksheet("Leads");
  const rows = [];
  sheet.eachRow({ includeEmpty: false }, (row) => rows.push(rowValues(row)));
  if (!rows.length) rows.push(HEADERS);

  const currentHeaders = rows[0].join("|");
  if (currentHeaders === LEGACY_HEADERS.join("|")) {
    rows[0] = HEADERS;
    for (let index = 1; index < rows.length; index += 1) {
      const row = rows[index];
      rows[index] = [row[0], row[1], row[2], "", row[3], row[4], row[5]];
    }
  } else if (currentHeaders !== HEADERS.join("|")) {
    rows[0] = HEADERS;
  }
  rows.push([lead.createdAt, lead.name, lead.email, lead.whatsapp, lead.profile, lead.pain, lead.origin]);

  sheet.spliceRows(1, sheet.rowCount, ...rows);
  await workbook.xlsx.writeFile(LEADS_FILE);
}

function run(command, args) {
  return new Promise((resolve, reject) => {
    execFile(command, args, { timeout: 30_000 }, (error, stdout, stderr) => {
      if (error) {
        error.stdout = stdout;
        error.stderr = stderr;
        reject(error);
        return;
      }
      resolve({ stdout, stderr });
    });
  });
}

async function createBetaAccess(lead) {
  const response = await fetch(BACKEND_LEADS_ENDPOINT, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      name: lead.name,
      email: lead.email,
      whatsapp: lead.whatsapp,
      profile: lead.profile,
      pain: lead.pain,
      origin: lead.origin,
    }),
  });

  if (!response.ok) {
    throw new Error(`backend_leads_failed_${response.status}`);
  }
}

async function syncDrive() {
  if (!DRIVE_FILE_ID) return;
  await run("gog", [
    "drive",
    "upload",
    LEADS_FILE,
    "--replace",
    DRIVE_FILE_ID,
    "--mime-type",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "--json",
  ]);
}

async function notifyTelegram(lead) {
  if (!TELEGRAM_TARGET || !TELEGRAM_BOT_TOKEN) return;
  const message = [
    "Novo lead do Cripto Farol",
    `Nome: ${lead.name}`,
    `Email: ${lead.email}`,
    `WhatsApp: ${lead.whatsapp || "-"}`,
    `Perfil: ${lead.profile || "-"}`,
    `Dificuldade: ${lead.pain || "-"}`,
  ].join("\n");

  const body = {
    chat_id: TELEGRAM_TARGET.replace(/^telegram:/, ""),
    text: message,
  };
  if (TELEGRAM_THREAD_ID) body.message_thread_id = Number(TELEGRAM_THREAD_ID);

  const response = await fetch(`https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!response.ok) {
    throw new Error(`telegram_failed_${response.status}`);
  }
}

async function notifyEmail(lead) {
  if (!EMAIL_TO) return;
  const subject = `Novo lead Cripto Farol: ${lead.name}`;
  const body = [
    "Novo lead do Cripto Farol",
    "",
    `Nome: ${lead.name}`,
    `Email: ${lead.email}`,
    `WhatsApp: ${lead.whatsapp || "-"}`,
    `Perfil: ${lead.profile || "-"}`,
    `Dificuldade: ${lead.pain || "-"}`,
    `Origem: ${lead.origin || "-"}`,
    `Data: ${lead.createdAt}`,
  ].join("\n");

  await run("gog", [
    "gmail",
    "send",
    "--to",
    EMAIL_TO,
    "--subject",
    subject,
    "--body",
    body,
    "--json",
  ]);
}

async function handleLead(req, res, origin) {
  const rawBody = await readBody(req);
  const payload = JSON.parse(rawBody || "{}");
  const lead = {
    createdAt: new Date().toISOString(),
    name: clean(payload.name),
    email: clean(payload.email).toLowerCase(),
    whatsapp: clean(payload.whatsapp),
    profile: clean(payload.profile),
    pain: clean(payload.pain),
    origin: clean(payload.origin) || "landing",
  };

  if (!lead.name || lead.name.length < 2) {
    sendJson(res, 400, { ok: false, error: "name_required" }, origin);
    return;
  }
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(lead.email)) {
    sendJson(res, 400, { ok: false, error: "email_required" }, origin);
    return;
  }
  if (!lead.whatsapp || lead.whatsapp.length < 8) {
    sendJson(res, 400, { ok: false, error: "whatsapp_required" }, origin);
    return;
  }

  queue = queue.then(async () => {
    await createBetaAccess(lead);
    await appendLead(lead);
    await syncDrive();
    await notifyTelegram(lead);
    await notifyEmail(lead);
  });
  await queue;
  sendJson(res, 200, { ok: true }, origin);
}

const server = http.createServer(async (req, res) => {
  const origin = req.headers.origin || "";

  if (req.method === "OPTIONS") {
    res.writeHead(204, corsHeaders(origin));
    res.end();
    return;
  }

  if (req.method === "GET" && req.url === "/health") {
    sendJson(res, 200, { ok: true }, origin);
    return;
  }

  if (req.method !== "POST" || req.url !== "/api/leads") {
    sendJson(res, 404, { ok: false, error: "not_found" }, origin);
    return;
  }

  try {
    await handleLead(req, res, origin);
  } catch (error) {
    console.error("lead_error", error.stderr || error.message);
    sendJson(res, 500, { ok: false, error: "submit_failed" }, origin);
  }
});

server.listen(PORT, HOST, () => {
  ensureWorkbook()
    .then(() => {
      console.log(`Cripto Farol leads server listening on ${HOST}:${PORT}`);
    })
    .catch((error) => {
      console.error("workbook_init_error", error.message);
      process.exit(1);
    });
});
