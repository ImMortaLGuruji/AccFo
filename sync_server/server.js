/**
 * AccFo Self-Hostable Node.js Sync Server
 * Zero-dependency standalone microservice for cross-device encrypted vault synchronization.
 *
 * Security Hardened:
 * - Constant-time token comparison (crypto.timingSafeEqual)
 * - 10MB maximum payload size limit
 * - JSON payload validation
 * - Proper error handling
 *
 * Usage:
 *   node sync_server/server.js [PORT] [AUTH_TOKEN]
 */

const http = require("http");
const fs = require("fs");
const path = require("path");
const crypto = require("crypto");

const PORT = parseInt(process.argv[2], 10) || 8765;
const AUTH_TOKEN =
  process.argv[3] || process.env.ACCFO_SYNC_TOKEN || "accfo_secret_token";
const DATA_DIR = path.join(__dirname, "vault_data");
const VAULT_FILE = path.join(DATA_DIR, "vault.json");
const MAX_PAYLOAD_BYTES = 10 * 1024 * 1024; // 10 MB

if (!fs.existsSync(DATA_DIR)) {
  fs.mkdirSync(DATA_DIR, { recursive: true });
}

function setCors(res) {
  res.setHeader("Access-Control-Allow-Origin", "*");
  res.setHeader("Access-Control-Allow-Methods", "GET, POST, OPTIONS");
  res.setHeader("Access-Control-Allow-Headers", "Content-Type, Authorization");
  res.setHeader("X-Content-Type-Options", "nosniff");
}

function verifyAuth(req) {
  if (!AUTH_TOKEN) return true;
  const header = req.headers["authorization"] || "";
  const expected = `Bearer ${AUTH_TOKEN}`;

  const headerBuf = Buffer.from(header);
  const expectedBuf = Buffer.from(expected);

  if (headerBuf.length !== expectedBuf.length) {
    return false;
  }

  return crypto.timingSafeEqual(headerBuf, expectedBuf);
}

const server = http.createServer((req, res) => {
  setCors(res);

  if (req.method === "OPTIONS") {
    res.writeHead(204);
    res.end();
    return;
  }

  const host = req.headers.host || "localhost";
  const url = new URL(req.url, `http://${host}`);

  if (url.pathname !== "/api/vault") {
    res.writeHead(404, { "Content-Type": "application/json" });
    res.end(JSON.stringify({ error: "Not Found" }));
    return;
  }

  if (!verifyAuth(req)) {
    res.writeHead(401, { "Content-Type": "application/json" });
    res.end(JSON.stringify({ error: "Unauthorized" }));
    return;
  }

  if (req.method === "GET") {
    if (!fs.existsSync(VAULT_FILE)) {
      res.writeHead(404, { "Content-Type": "application/json" });
      res.end(JSON.stringify({ error: "Vault not found" }));
      return;
    }
    fs.readFile(VAULT_FILE, "utf8", (err, data) => {
      if (err) {
        res.writeHead(500, { "Content-Type": "application/json" });
        res.end(JSON.stringify({ error: "Failed to read vault" }));
        return;
      }
      res.writeHead(200, { "Content-Type": "application/json" });
      res.end(data);
    });
  } else if (req.method === "POST") {
    let body = "";
    let bodyLength = 0;

    req.on("data", (chunk) => {
      bodyLength += chunk.length;
      if (bodyLength > MAX_PAYLOAD_BYTES) {
        res.writeHead(413, { "Content-Type": "application/json" });
        res.end(JSON.stringify({ error: "Payload exceeds 10MB limit" }));
        req.destroy();
        return;
      }
      body += chunk;
    });

    req.on("end", () => {
      try {
        JSON.parse(body);
        fs.writeFile(VAULT_FILE, body, "utf8", (err) => {
          if (err) {
            res.writeHead(500, { "Content-Type": "application/json" });
            res.end(JSON.stringify({ error: "Failed to save vault" }));
            return;
          }
          res.writeHead(200, { "Content-Type": "application/json" });
          res.end(
            JSON.stringify({
              status: "ok",
              message: "Vault synchronized successfully",
            }),
          );
        });
      } catch {
        res.writeHead(400, { "Content-Type": "application/json" });
        res.end(JSON.stringify({ error: "Malformed JSON payload" }));
      }
    });
  } else {
    res.writeHead(405, { "Content-Type": "application/json" });
    res.end(JSON.stringify({ error: "Method Not Allowed" }));
  }
});

server.listen(PORT, "0.0.0.0", () => {
  console.log(`🔒 AccFo Node Sync Server running at http://0.0.0.0:${PORT}`);
  console.log(`🔑 Auth Token: ${AUTH_TOKEN}`);
});
