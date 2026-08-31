/**
 * AccFo Legacy & Universal Migration Engine
 * Supports importing:
 * 1. Legacy Python AccFo database exports / backups
 * 2. Standard CSV files (Service, Username, Password, URL, Notes, Category)
 * 3. Standard JSON password exports (Bitwarden, 1Password, Chrome, Firefox)
 */

const AccFoMigration = {
  /**
   * Parses generic CSV string into account objects
   */
  parseCSV(csvText) {
    if (!csvText || typeof csvText !== "string") return [];

    const lines = csvText
      .split(/\r?\n/)
      .filter((line) => line.trim().length > 0);
    if (lines.length === 0) return [];

    const accounts = [];
    const headerLine = lines[0].toLowerCase();

    // Auto-detect column indexes
    const headers = this.parseCSVLine(headerLine);
    let serviceIdx = headers.findIndex(
      (h) =>
        h.includes("name") ||
        h.includes("service") ||
        h.includes("title") ||
        h.includes("site"),
    );
    let usernameIdx = headers.findIndex(
      (h) => h.includes("user") || h.includes("login") || h.includes("email"),
    );
    let passwordIdx = headers.findIndex(
      (h) => h.includes("pass") || h.includes("secret"),
    );
    let urlIdx = headers.findIndex(
      (h) =>
        h.includes("url") ||
        h.includes("uri") ||
        h.includes("web") ||
        h.includes("link"),
    );
    let notesIdx = headers.findIndex(
      (h) => h.includes("note") || h.includes("comment") || h.includes("extra"),
    );
    let categoryIdx = headers.findIndex(
      (h) => h.includes("folder") || h.includes("cat") || h.includes("group"),
    );

    // Fallbacks if header wasn't matched
    if (serviceIdx === -1) serviceIdx = 0;
    if (usernameIdx === -1) usernameIdx = 1;
    if (passwordIdx === -1) passwordIdx = 2;

    for (let i = 1; i < lines.length; i++) {
      const cols = this.parseCSVLine(lines[i]);
      if (cols.length === 0) continue;

      const service = cols[serviceIdx] || "Imported Entry";
      const username = cols[usernameIdx] || "";
      const password = cols[passwordIdx] || "";
      const url = urlIdx !== -1 ? cols[urlIdx] || "" : "";
      const notes = notesIdx !== -1 ? cols[notesIdx] || "" : "";
      const category =
        categoryIdx !== -1 ? cols[categoryIdx] || "General" : "General";

      if (service || username || password) {
        accounts.push({
          service: String(service).trim(),
          username: String(username).trim(),
          password: String(password),
          url: String(url).trim(),
          notes: String(notes).trim(),
          category: String(category).trim() || "General",
        });
      }
    }

    return accounts;
  },

  /**
   * Helper to parse CSV line handling RFC 4180 quotes & escaped double quotes
   */
  parseCSVLine(line) {
    const result = [];
    let cur = "";
    let inQuotes = false;

    for (let i = 0; i < line.length; i++) {
      const char = line[i];
      const nextChar = line[i + 1];

      if (char === '"') {
        if (inQuotes && nextChar === '"') {
          cur += '"';
          i++; // Skip escaped quote
        } else {
          inQuotes = !inQuotes;
        }
      } else if (char === "," && !inQuotes) {
        result.push(cur.trim());
        cur = "";
      } else {
        cur += char;
      }
    }
    result.push(cur.trim());
    return result;
  },

  /**
   * Parses JSON exports (AccFo native or Bitwarden/1Password format)
   */
  parseJSON(jsonText) {
    try {
      const data = JSON.parse(jsonText);

      // Case 1: AccFo Native Export
      if (data.accounts && Array.isArray(data.accounts)) {
        return data.accounts.map((acc) => ({
          service: String(acc.service || "Imported Item").trim(),
          username: String(acc.username || "").trim(),
          password: String(acc.password || ""),
          url: String(acc.url || "").trim(),
          notes: String(acc.notes || "").trim(),
          category: String(acc.category || "General").trim(),
          favorite: Boolean(acc.favorite),
        }));
      }

      // Case 2: Bitwarden Export format
      if (data.items && Array.isArray(data.items)) {
        return data.items.map((item) => {
          const login = item.login || {};
          const uri =
            login.uris && login.uris.length > 0 ? login.uris[0].uri : "";
          return {
            service: String(item.name || "Bitwarden Entry").trim(),
            username: String(login.username || "").trim(),
            password: String(login.password || ""),
            url: String(uri || "").trim(),
            notes: String(item.notes || "").trim(),
            category: "General",
            favorite: Boolean(item.favorite),
          };
        });
      }

      // Case 3: Raw array of objects
      if (Array.isArray(data)) {
        return data.map((item) => ({
          service: String(item.service || item.name || "Imported Item").trim(),
          username: String(item.username || item.login || "").trim(),
          password: String(item.password || ""),
          url: String(item.url || item.uri || "").trim(),
          notes: String(item.notes || "").trim(),
          category: String(item.category || "General").trim(),
          favorite: Boolean(item.favorite),
        }));
      }

      return [];
    } catch (err) {
      console.error("Failed to parse JSON:", err);
      return [];
    }
  },
};

window.AccFoMigration = AccFoMigration;
