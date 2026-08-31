/**
 * AccFo Vault State & Account Management Engine
 */

class AccFoVault {
  constructor() {
    this.accounts = [];
    this.owner = "";
    this.version = "2.0";
    this.lastModified = Date.now();
  }

  /**
   * Initializes or loads accounts into the vault
   */
  loadData(payload) {
    if (!payload) return;
    this.accounts = Array.isArray(payload.accounts) ? payload.accounts : [];
    this.owner = payload.owner || "";
    this.version = payload.version || "2.0";
    this.lastModified = payload.lastModified || Date.now();
  }

  /**
   * Packages vault state into an exportable / encryptable object
   */
  exportData() {
    return {
      version: this.version,
      owner: this.owner,
      lastModified: Date.now(),
      accounts: this.accounts,
    };
  }

  /**
   * Adds a new credential entry
   */
  addAccount(data) {
    const newAccount = {
      id: "acc_" + Date.now() + "_" + Math.random().toString(36).substr(2, 6),
      service: data.service ? data.service.trim() : "Unnamed Service",
      username: data.username ? data.username.trim() : "",
      password: data.password || "",
      url: data.url ? data.url.trim() : "",
      category: data.category || "General",
      notes: data.notes ? data.notes.trim() : "",
      favorite: Boolean(data.favorite),
      createdAt: Date.now(),
      updatedAt: Date.now(),
    };

    this.accounts.unshift(newAccount);
    this.lastModified = Date.now();
    return newAccount;
  }

  /**
   * Updates an existing credential entry
   */
  updateAccount(id, data) {
    const index = this.accounts.findIndex((a) => a.id === id);
    if (index === -1) return null;

    this.accounts[index] = {
      ...this.accounts[index],
      service: data.service
        ? data.service.trim()
        : this.accounts[index].service,
      username:
        data.username !== undefined
          ? data.username.trim()
          : this.accounts[index].username,
      password:
        data.password !== undefined
          ? data.password
          : this.accounts[index].password,
      url: data.url !== undefined ? data.url.trim() : this.accounts[index].url,
      category: data.category || this.accounts[index].category,
      notes:
        data.notes !== undefined
          ? data.notes.trim()
          : this.accounts[index].notes,
      favorite:
        data.favorite !== undefined
          ? Boolean(data.favorite)
          : this.accounts[index].favorite,
      updatedAt: Date.now(),
    };

    this.lastModified = Date.now();
    return this.accounts[index];
  }

  /**
   * Removes an account by ID
   */
  deleteAccount(id) {
    const initialLen = this.accounts.length;
    this.accounts = this.accounts.filter((a) => a.id !== id);
    this.lastModified = Date.now();
    return this.accounts.length < initialLen;
  }

  /**
   * Toggles favorite status for an account
   */
  toggleFavorite(id) {
    const acc = this.accounts.find((a) => a.id === id);
    if (acc) {
      acc.favorite = !acc.favorite;
      acc.updatedAt = Date.now();
      this.lastModified = Date.now();
      return acc.favorite;
    }
    return false;
  }

  /**
   * Retrieves single account by ID
   */
  getAccount(id) {
    return this.accounts.find((a) => a.id === id) || null;
  }

  /**
   * Filters and sorts accounts for search / category views
   */
  filterAndSort(query = "", category = "all", sortBy = "service-asc") {
    let result = [...this.accounts];

    // Filter by category
    if (category && category !== "all") {
      if (category === "favorites") {
        result = result.filter((a) => a.favorite);
      } else {
        result = result.filter(
          (a) => (a.category || "").toLowerCase() === category.toLowerCase(),
        );
      }
    }

    // Filter by search query
    if (query && query.trim()) {
      const q = query.toLowerCase().trim();
      result = result.filter(
        (a) =>
          (a.service && a.service.toLowerCase().includes(q)) ||
          (a.username && a.username.toLowerCase().includes(q)) ||
          (a.url && a.url.toLowerCase().includes(q)) ||
          (a.notes && a.notes.toLowerCase().includes(q)),
      );
    }

    // Sorting
    result.sort((a, b) => {
      if (sortBy === "service-asc") {
        return (a.service || "").localeCompare(b.service || "");
      } else if (sortBy === "service-desc") {
        return (b.service || "").localeCompare(a.service || "");
      } else if (sortBy === "recent") {
        return (b.updatedAt || 0) - (a.updatedAt || 0);
      } else if (sortBy === "oldest") {
        return (a.createdAt || 0) - (b.createdAt || 0);
      }
      return 0;
    });

    return result;
  }

  /**
   * Computes security health audit across all accounts
   */
  getSecurityAudit() {
    const total = this.accounts.length;
    if (total === 0) {
      return {
        total: 0,
        score: 100,
        strongCount: 0,
        weakCount: 0,
        reusedCount: 0,
        weakAccounts: [],
        reusedAccounts: [],
      };
    }

    const passwordUsageMap = new Map();
    const weakAccounts = [];
    let strongCount = 0;

    for (const acc of this.accounts) {
      const pwd = acc.password || "";
      const strength = AccFoCrypto.evaluateStrength(pwd);

      if (strength.score >= 4) {
        strongCount++;
      } else if (strength.score <= 2 || pwd.length < 10) {
        weakAccounts.push({ account: acc, strength });
      }

      if (pwd) {
        const count = passwordUsageMap.get(pwd) || [];
        count.push(acc);
        passwordUsageMap.set(pwd, count);
      }
    }

    const reusedAccounts = [];
    for (const [pwd, accs] of passwordUsageMap.entries()) {
      if (accs.length > 1) {
        reusedAccounts.push({ password: pwd, accounts: accs });
      }
    }

    const weakDeduction = (weakAccounts.length / total) * 50;
    const reusedDeduction = (reusedAccounts.length / total) * 35;
    const score = Math.max(
      10,
      Math.min(100, Math.round(100 - weakDeduction - reusedDeduction)),
    );

    return {
      total,
      score,
      strongCount,
      weakCount: weakAccounts.length,
      reusedCount: reusedAccounts.length,
      weakAccounts,
      reusedAccounts,
    };
  }

  /**
   * Imports multiple accounts, merging or replacing duplicates
   */
  importAccounts(importedAccounts, strategy = "merge") {
    if (!Array.isArray(importedAccounts)) return 0;
    let count = 0;

    for (const item of importedAccounts) {
      if (!item.service && !item.username && !item.password) continue;

      const existing = this.accounts.find(
        (a) =>
          (a.service || "").toLowerCase() ===
            (item.service || "").toLowerCase() &&
          (a.username || "").toLowerCase() ===
            (item.username || "").toLowerCase(),
      );

      if (existing && strategy === "merge") {
        this.updateAccount(existing.id, item);
      } else {
        this.addAccount(item);
      }
      count++;
    }

    return count;
  }
}

window.AccFoVault = AccFoVault;
