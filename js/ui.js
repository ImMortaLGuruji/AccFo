/**
 * AccFo UI Controller & Interaction Layer
 * Security Hardened:
 * - Zero plaintext passwords stored in DOM attributes
 * - Strict URL sanitization against javascript: / data: / vbscript: vectors
 * - Auto-clearing clipboard timers for copied credentials
 * - HTML entity encoding for all rendered user fields
 */

const AccFoUI = {
  currentView: "vault",
  currentCategory: "all",
  searchQuery: "",
  sortBy: "service-asc",
  activeEditingId: null,
  clipboardClearTimeoutId: null,

  init() {
    this.bindEvents();
    this.initGeneratorStudio();
  },

  /**
   * Toast notification helper with clean SVG status indicators
   */
  showToast(message, type = "info", duration = 3000) {
    let container = document.getElementById("toast-container");
    if (!container) {
      container = document.createElement("div");
      container.id = "toast-container";
      container.className = "toast-container";
      document.body.appendChild(container);
    }

    const toast = document.createElement("div");
    toast.className = `toast ${type}`;

    let iconSvg = AccFoIcons.get("info", 16);
    if (type === "success") iconSvg = AccFoIcons.get("check", 16);
    if (type === "error") iconSvg = AccFoIcons.get("alert-triangle", 16);
    if (type === "copy") iconSvg = AccFoIcons.get("copy", 16);

    toast.innerHTML = `<span style="display:inline-flex; align-items:center;">${iconSvg}</span> <span>${this.escapeHTML(message)}</span>`;
    container.appendChild(toast);

    setTimeout(() => {
      toast.style.opacity = "0";
      toast.style.transform = "translateY(12px) scale(0.95)";
      setTimeout(() => toast.remove(), 250);
    }, duration);
  },

  /**
   * Secure clipboard copy with dual-state feedback and auto-clear security timer (30s)
   */
  async copyText(
    text,
    label = "Copied to clipboard",
    btnElement = null,
    autoClearSeconds = 30,
  ) {
    if (!text) return;

    try {
      if (navigator.clipboard && navigator.clipboard.writeText) {
        await navigator.clipboard.writeText(text);
      } else {
        const el = document.createElement("textarea");
        el.value = text;
        el.setAttribute("readonly", "");
        el.style.position = "absolute";
        el.style.left = "-9999px";
        document.body.appendChild(el);
        el.select();
        document.execCommand("copy");
        document.body.removeChild(el);
      }
    } catch (err) {
      console.warn("Clipboard copy failed:", err);
      this.showToast("Unable to copy to clipboard", "error");
      return;
    }

    this.showToast(label, "success");

    // Dual-state button icon animation
    if (btnElement) {
      const origHTML = btnElement.innerHTML;
      btnElement.innerHTML = `${AccFoIcons.get("check", 13)} <span>Copied</span>`;
      btnElement.style.color = "var(--color-emerald)";
      setTimeout(() => {
        btnElement.innerHTML = origHTML;
        btnElement.style.color = "";
      }, 1500);
    }

    // Auto-clear clipboard timer for security hygiene
    if (this.clipboardClearTimeoutId) {
      clearTimeout(this.clipboardClearTimeoutId);
    }
    if (autoClearSeconds > 0) {
      this.clipboardClearTimeoutId = setTimeout(async () => {
        try {
          if (navigator.clipboard && navigator.clipboard.writeText) {
            // Overwrite clipboard
            await navigator.clipboard.writeText("");
          }
        } catch {
          // Ignore if focus lost
        }
      }, autoClearSeconds * 1000);
    }
  },

  /**
   * Secure copy of username without putting username into inline attributes
   */
  copyAccountUsername(id, btnElement) {
    const acc = window.accfoApp?.vault?.getAccount(id);
    if (acc && acc.username) {
      this.copyText(acc.username, "Username copied", btnElement, 0);
    }
  },

  /**
   * Secure copy of password retrieved directly from memory (not DOM)
   */
  copyAccountPassword(id, btnElement) {
    const acc = window.accfoApp?.vault?.getAccount(id);
    if (acc && acc.password) {
      this.copyText(
        acc.password,
        "Password copied (clears in 30s)",
        btnElement,
        30,
      );
    }
  },

  /**
   * View switcher (vault, generator, security, settings)
   */
  switchView(viewName) {
    this.currentView = viewName;

    // Update navigation active states
    document
      .querySelectorAll(".sidebar-nav-item, .mobile-nav-btn")
      .forEach((btn) => {
        btn.classList.toggle(
          "active",
          btn.getAttribute("data-view") === viewName,
        );
      });

    // Update view panes
    document.querySelectorAll(".view-pane").forEach((pane) => {
      pane.classList.remove("active");
    });

    const targetPane = document.getElementById(`view-${viewName}`);
    if (targetPane) {
      targetPane.classList.add("active");
    }

    if (viewName === "vault") {
      this.renderVault();
    } else if (viewName === "security") {
      this.renderSecurityAudit();
    } else if (viewName === "settings") {
      this.renderSettingsView();
    }
  },

  /**
   * Modal management
   */
  openModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
      modal.classList.add("open");
      const firstInput = modal.querySelector("input, select, textarea");
      if (firstInput) setTimeout(() => firstInput.focus(), 100);
    }
  },

  closeModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
      modal.classList.remove("open");
    }
  },

  closeAllModals() {
    document
      .querySelectorAll(".modal-backdrop")
      .forEach((m) => m.classList.remove("open"));
  },

  /**
   * Renders vault cards, stats, and filters
   */
  renderVault() {
    if (!window.accfoApp || !window.accfoApp.vault) return;
    const vault = window.accfoApp.vault;

    // Update Overview Stats
    const audit = vault.getSecurityAudit();
    document.getElementById("stat-total-accounts").textContent =
      vault.accounts.length;
    document.getElementById("stat-strong-passwords").textContent =
      audit.strongCount;
    document.getElementById("stat-security-score").textContent =
      `${audit.score}%`;

    // Update badge in sidebar
    const vaultBadge = document.getElementById("sidebar-vault-count");
    if (vaultBadge) vaultBadge.textContent = vault.accounts.length;

    // Render Filtered Cards
    const accounts = vault.filterAndSort(
      this.searchQuery,
      this.currentCategory,
      this.sortBy,
    );
    const container = document.getElementById("vault-cards-grid");
    const emptyState = document.getElementById("vault-empty-state");

    if (accounts.length === 0) {
      container.innerHTML = "";
      emptyState.style.display = "flex";
      const emptyDesc = document.getElementById("empty-state-desc");
      if (this.searchQuery || this.currentCategory !== "all") {
        emptyDesc.textContent =
          "No matching items found for your current search or category filter.";
      } else {
        emptyDesc.textContent =
          "Your vault is currently empty. Add your first credential or import an existing file.";
      }
      return;
    }

    emptyState.style.display = "none";
    container.innerHTML = accounts
      .map((acc) => this.generateCardHTML(acc))
      .join("");
  },

  /**
   * Strictly sanitizes URLs to permit only http: and https: protocols
   */
  sanitizeUrl(url) {
    if (!url || typeof url !== "string") return null;
    const trimmed = url.trim();
    if (!trimmed) return null;

    // Disallow dangerous URI schemes
    if (/^(javascript|data|vbscript|file):/i.test(trimmed)) {
      return null;
    }

    if (/^https?:\/\//i.test(trimmed)) {
      return trimmed;
    }

    return "https://" + trimmed;
  },

  /**
   * Generates single credential card HTML with SVG icons
   */
  generateCardHTML(acc) {
    const initial = (acc.service || "A").charAt(0).toUpperCase();
    const isFav = acc.favorite;
    const strength = AccFoCrypto.evaluateStrength(acc.password);
    const formattedDate = new Date(
      acc.updatedAt || Date.now(),
    ).toLocaleDateString(undefined, {
      month: "short",
      day: "numeric",
      year: "numeric",
    });

    let catBadgeClass = "badge-cyan";
    if (acc.category === "Work") catBadgeClass = "badge-amber";
    if (acc.category === "Finance") catBadgeClass = "badge-emerald";
    if (acc.category === "Social") catBadgeClass = "badge-red";

    const starIcon = isFav
      ? AccFoIcons.get("star-filled", 15, "text-danger")
      : AccFoIcons.get("star", 15);
    const editIcon = AccFoIcons.get("edit", 15);
    const trashIcon = AccFoIcons.get("trash", 15);
    const copyIcon = AccFoIcons.get("copy", 13);
    const linkIcon = AccFoIcons.get("external-link", 12);

    const safeUrl = this.sanitizeUrl(acc.url);
    const safeId = this.escapeHTML(acc.id);

    return `
      <div class="account-card" data-id="${safeId}">
        <div class="card-header-row">
          <div class="card-service-info">
            <div class="service-avatar">${this.escapeHTML(initial)}</div>
            <div>
              <h4 class="service-title">${this.escapeHTML(acc.service)}</h4>
              ${
                safeUrl
                  ? `<a href="${this.escapeHTML(safeUrl)}" target="_blank" rel="noopener noreferrer nofollow" class="service-url">${linkIcon} <span>${this.escapeHTML(safeUrl.replace(/^https?:\/\//, ""))}</span></a>`
                  : `<span class="service-url text-muted">Local Item</span>`
              }
            </div>
          </div>
          <div class="card-actions-menu">
            <button class="btn-icon btn-sm fav-toggle-btn" onclick="AccFoUI.handleToggleFavorite('${safeId}')" title="Favorite">
              ${starIcon}
            </button>
            <button class="btn-icon btn-sm" onclick="AccFoUI.handleOpenEditModal('${safeId}')" title="Edit">
              ${editIcon}
            </button>
            <button class="btn-icon btn-sm" onclick="AccFoUI.handleConfirmDelete('${safeId}')" title="Delete">
              ${trashIcon}
            </button>
          </div>
        </div>

        <div class="card-data-fields">
          <div class="data-row">
            <span class="data-label">Username / Email</span>
            <div class="data-value-group">
              <span class="data-value" title="${this.escapeHTML(acc.username)}">${this.escapeHTML(acc.username || "—")}</span>
              ${
                acc.username
                  ? `<button class="data-copy-btn" onclick="AccFoUI.copyAccountUsername('${safeId}', this)">${copyIcon} <span>Copy</span></button>`
                  : ""
              }
            </div>
          </div>

          <div class="data-row">
            <span class="data-label">Password</span>
            <div class="data-value-group">
              <span class="data-value password-masked font-mono" id="pwd-val-${safeId}">••••••••••••</span>
              <button class="data-copy-btn" id="pwd-toggle-${safeId}" onclick="AccFoUI.togglePasswordVisibility('${safeId}')">Show</button>
              <button class="data-copy-btn" onclick="AccFoUI.copyAccountPassword('${safeId}', this)">${copyIcon} <span>Copy</span></button>
            </div>
          </div>
        </div>

        <div class="card-footer-row">
          <span class="badge ${catBadgeClass}">${this.escapeHTML(acc.category || "General")}</span>
          <div style="display:flex; align-items:center; gap:0.5rem;">
            <span class="badge" style="background:${strength.color}15; color:${strength.color}; border:1px solid ${strength.color}35;">${strength.label}</span>
            <span class="text-muted" style="font-size:0.75rem;">${formattedDate}</span>
          </div>
        </div>
      </div>
    `;
  },

  /**
   * Securely toggles password display by retrieving it from memory
   */
  togglePasswordVisibility(id) {
    const el = document.getElementById(`pwd-val-${id}`);
    const toggleBtn = document.getElementById(`pwd-toggle-${id}`);
    const acc = window.accfoApp?.vault?.getAccount(id);
    if (!el || !toggleBtn || !acc) return;

    if (el.textContent === "••••••••••••") {
      el.textContent = acc.password;
      toggleBtn.textContent = "Hide";
      setTimeout(() => {
        if (el.textContent === acc.password) {
          el.textContent = "••••••••••••";
          toggleBtn.textContent = "Show";
        }
      }, 8000);
    } else {
      el.textContent = "••••••••••••";
      toggleBtn.textContent = "Show";
    }
  },

  handleToggleFavorite(id) {
    if (!window.accfoApp) return;
    window.accfoApp.vault.toggleFavorite(id);
    window.accfoApp.saveAndSync();
    this.renderVault();
  },

  handleConfirmDelete(id) {
    const acc = window.accfoApp.vault.getAccount(id);
    if (!acc) return;
    document.getElementById("delete-modal-service-name").textContent =
      acc.service;
    document.getElementById("delete-confirm-btn").onclick = () => {
      window.accfoApp.vault.deleteAccount(id);
      window.accfoApp.saveAndSync();
      this.closeModal("modal-delete-confirm");
      this.showToast("Item deleted", "info");
      this.renderVault();
    };
    this.openModal("modal-delete-confirm");
  },

  handleOpenAddModal() {
    this.activeEditingId = null;
    document.getElementById("modal-account-title").textContent = "Add Item";
    document.getElementById("form-acc-service").value = "";
    document.getElementById("form-acc-username").value = "";
    document.getElementById("form-acc-password").value = "";
    document.getElementById("form-acc-url").value = "";
    document.getElementById("form-acc-category").value = "General";
    document.getElementById("form-acc-notes").value = "";
    this.openModal("modal-account-editor");
  },

  handleOpenEditModal(id) {
    const acc = window.accfoApp.vault.getAccount(id);
    if (!acc) return;
    this.activeEditingId = id;
    document.getElementById("modal-account-title").textContent = "Edit Item";
    document.getElementById("form-acc-service").value = acc.service || "";
    document.getElementById("form-acc-username").value = acc.username || "";
    document.getElementById("form-acc-password").value = acc.password || "";
    document.getElementById("form-acc-url").value = acc.url || "";
    document.getElementById("form-acc-category").value =
      acc.category || "General";
    document.getElementById("form-acc-notes").value = acc.notes || "";
    this.openModal("modal-account-editor");
  },

  /**
   * Initializes Password Generator Studio
   */
  initGeneratorStudio() {
    const lengthSlider = document.getElementById("gen-length-slider");
    const lengthValue = document.getElementById("gen-length-display");

    if (lengthSlider && lengthValue) {
      lengthSlider.addEventListener("input", (e) => {
        lengthValue.textContent = e.target.value;
        this.refreshGenerator();
      });
    }

    // Refresh generator on option toggle
    [
      "gen-opt-upper",
      "gen-opt-lower",
      "gen-opt-nums",
      "gen-opt-symbols",
      "gen-opt-avoid-ambiguous",
    ].forEach((id) => {
      const el = document.getElementById(id);
      if (el) el.addEventListener("change", () => this.refreshGenerator());
    });

    this.refreshGenerator();
  },

  refreshGenerator() {
    const length = parseInt(
      document.getElementById("gen-length-slider")?.value || 18,
      10,
    );
    const uppercase = document.getElementById("gen-opt-upper")?.checked ?? true;
    const lowercase = document.getElementById("gen-opt-lower")?.checked ?? true;
    const numbers = document.getElementById("gen-opt-nums")?.checked ?? true;
    const symbols = document.getElementById("gen-opt-symbols")?.checked ?? true;
    const avoidAmbiguous =
      document.getElementById("gen-opt-avoid-ambiguous")?.checked ?? false;

    const pwd = AccFoGenerator.generatePassword({
      length,
      uppercase,
      lowercase,
      numbers,
      symbols,
      avoidAmbiguous,
    });

    const displayEl = document.getElementById("generated-password-output");
    if (displayEl) displayEl.textContent = pwd;

    // Update entropy & strength
    const strength = AccFoCrypto.evaluateStrength(pwd);
    const entropyEl = document.getElementById("generator-entropy-text");
    const crackTimeEl = document.getElementById("generator-crack-time");
    const meterFill = document.getElementById("generator-meter-fill");

    if (entropyEl)
      entropyEl.textContent = `${strength.entropy} bits of entropy • ${strength.label}`;
    if (crackTimeEl)
      crackTimeEl.textContent = `Estimated crack time: ${strength.crackTime}`;
    if (meterFill) {
      meterFill.style.width = `${Math.min(100, (strength.score / 5) * 100)}%`;
      meterFill.style.backgroundColor = strength.color;
    }
  },

  /**
   * Renders the Security Audit view
   */
  renderSecurityAudit() {
    if (!window.accfoApp || !window.accfoApp.vault) return;
    const audit = window.accfoApp.vault.getSecurityAudit();

    document.getElementById("audit-health-score").textContent =
      `${audit.score}%`;
    document.getElementById("audit-strong-count").textContent =
      audit.strongCount;
    document.getElementById("audit-weak-count").textContent = audit.weakCount;
    document.getElementById("audit-reused-count").textContent =
      audit.reusedCount;

    const issuesContainer = document.getElementById("audit-issues-list");
    if (!issuesContainer) return;

    if (audit.weakAccounts.length === 0 && audit.reusedAccounts.length === 0) {
      issuesContainer.innerHTML = `
        <div style="text-align:center; padding: 2.5rem 1rem; color: var(--color-emerald);">
          <div style="margin-bottom:0.75rem;">${AccFoIcons.get("shield-check", 40)}</div>
          <h4 style="font-size:1.05rem; font-weight:700;">No Vulnerabilities Detected</h4>
          <p class="text-secondary" style="font-size:0.85rem; margin-top:0.25rem;">All passwords in your vault meet recommended length and entropy standards.</p>
        </div>
      `;
      return;
    }

    let html = "";

    // Weak Passwords List
    if (audit.weakAccounts.length > 0) {
      html += `<div style="display:flex; align-items:center; gap:0.4rem; margin-bottom:0.75rem; color:var(--color-imperial-red);">
        ${AccFoIcons.get("alert-triangle", 16)}
        <h4 style="font-size:0.92rem; font-weight:700;">Weak Passwords (${audit.weakAccounts.length})</h4>
      </div>`;

      audit.weakAccounts.forEach(({ account, strength }) => {
        const safeAccId = this.escapeHTML(account.id);
        html += `
          <div class="option-toggle-card" style="margin-bottom:0.65rem;">
            <div>
              <strong>${this.escapeHTML(account.service)}</strong>
              <div class="text-muted" style="font-size:0.78rem;">${this.escapeHTML(account.username || "No username")} • <span style="color:${strength.color}">${strength.label} (${strength.entropy} bits)</span></div>
            </div>
            <button class="btn btn-sm btn-secondary" onclick="AccFoUI.handleOpenEditModal('${safeAccId}')">Upgrade</button>
          </div>
        `;
      });
    }

    // Reused Passwords List
    if (audit.reusedAccounts.length > 0) {
      html += `<div style="display:flex; align-items:center; gap:0.4rem; margin: 1.5rem 0 0.75rem 0; color:var(--color-amber);">
        ${AccFoIcons.get("refresh", 16)}
        <h4 style="font-size:0.92rem; font-weight:700;">Reused Passwords (${audit.reusedAccounts.length})</h4>
      </div>`;

      audit.reusedAccounts.forEach((item) => {
        const services = item.accounts.map((a) => a.service).join(", ");
        const firstId = this.escapeHTML(item.accounts[0].id);
        html += `
          <div class="option-toggle-card" style="margin-bottom:0.65rem;">
            <div>
              <strong>Reused across ${item.accounts.length} items</strong>
              <div class="text-muted" style="font-size:0.78rem;">${this.escapeHTML(services)}</div>
            </div>
            <button class="btn btn-sm btn-secondary" onclick="AccFoUI.handleOpenEditModal('${firstId}')">Change</button>
          </div>
        `;
      });
    }

    issuesContainer.innerHTML = html;
  },

  /**
   * Renders Settings & Sync Configurations
   */
  renderSettingsView() {
    const syncCfg = AccFoSync.getConfig();

    // Set active sync tab
    document.querySelectorAll(".provider-tab").forEach((tab) => {
      tab.classList.toggle(
        "active",
        tab.getAttribute("data-provider") === syncCfg.provider,
      );
    });

    ["sync-pane-webdav", "sync-pane-self-hosted", "sync-pane-s3"].forEach(
      (id) => {
        const el = document.getElementById(id);
        if (el) el.style.display = "none";
      },
    );

    if (syncCfg.provider === AccFoSync.PROVIDERS.WEBDAV) {
      const el = document.getElementById("sync-pane-webdav");
      if (el) el.style.display = "block";
    } else if (syncCfg.provider === AccFoSync.PROVIDERS.SELF_HOSTED) {
      const el = document.getElementById("sync-pane-self-hosted");
      if (el) el.style.display = "block";
    } else if (syncCfg.provider === AccFoSync.PROVIDERS.S3_MINIO) {
      const el = document.getElementById("sync-pane-s3");
      if (el) el.style.display = "block";
    }

    // Populate saved sync values
    if (syncCfg.webdav) {
      if (document.getElementById("webdav-url"))
        document.getElementById("webdav-url").value = syncCfg.webdav.url || "";
      if (document.getElementById("webdav-user"))
        document.getElementById("webdav-user").value =
          syncCfg.webdav.username || "";
      if (document.getElementById("webdav-pass"))
        document.getElementById("webdav-pass").value =
          syncCfg.webdav.password || "";
    }

    if (syncCfg.selfHosted) {
      if (document.getElementById("self-hosted-endpoint"))
        document.getElementById("self-hosted-endpoint").value =
          syncCfg.selfHosted.endpoint || "";
      if (document.getElementById("self-hosted-token"))
        document.getElementById("self-hosted-token").value =
          syncCfg.selfHosted.token || "";
    }

    // Update Local File Status in Settings
    const localFileStatus = document.getElementById("settings-local-file-info");
    if (localFileStatus) {
      if (window.accfoApp.linkedFileHandle) {
        localFileStatus.innerHTML = `
          <div style="display:flex; align-items:center; gap:0.5rem; color:var(--color-emerald);">
            ${AccFoIcons.get("check", 16)}
            <strong>Linked File:</strong> <span class="font-mono">${this.escapeHTML(window.accfoApp.linkedFileHandle.name)}</span>
          </div>
          <p class="text-secondary" style="font-size:0.78rem; margin-top:0.25rem;">All vault modifications are auto-saved directly to your physical disk handle.</p>
        `;
      } else {
        localFileStatus.innerHTML = `
          <div style="display:flex; align-items:center; gap:0.5rem; color:var(--text-secondary);">
            ${AccFoIcons.get("hard-drive", 16)}
            <span>No physical file linked. Vault data is currently stored in encrypted browser storage.</span>
          </div>
        `;
      }
    }
  },

  /**
   * Binds global UI event listeners
   */
  bindEvents() {
    // Navigation items
    document.querySelectorAll("[data-view]").forEach((el) => {
      el.addEventListener("click", () => {
        const view = el.getAttribute("data-view");
        if (view) this.switchView(view);
      });
    });

    // Category chips
    document.querySelectorAll(".category-chip").forEach((chip) => {
      chip.addEventListener("click", () => {
        document
          .querySelectorAll(".category-chip")
          .forEach((c) => c.classList.remove("active"));
        chip.classList.add("active");
        this.currentCategory = chip.getAttribute("data-category") || "all";
        this.renderVault();
      });
    });

    // Search Box
    const searchInput = document.getElementById("vault-search-input");
    if (searchInput) {
      searchInput.addEventListener("input", (e) => {
        this.searchQuery = e.target.value;
        this.renderVault();
      });
    }

    // Global / key shortcut to focus search
    window.addEventListener("keydown", (e) => {
      if (
        e.key === "/" &&
        document.activeElement !== searchInput &&
        !["INPUT", "TEXTAREA"].includes(document.activeElement.tagName)
      ) {
        e.preventDefault();
        if (this.currentView !== "vault") this.switchView("vault");
        if (searchInput) searchInput.focus();
      }
    });

    // Sort Dropdown
    const sortSelect = document.getElementById("vault-sort-select");
    if (sortSelect) {
      sortSelect.addEventListener("change", (e) => {
        this.sortBy = e.target.value;
        this.renderVault();
      });
    }

    // Modal Close buttons
    document.querySelectorAll("[data-close-modal]").forEach((btn) => {
      btn.addEventListener("click", () => {
        const modalId = btn.getAttribute("data-close-modal");
        if (modalId) this.closeModal(modalId);
      });
    });

    // Close modal on backdrop click
    document.querySelectorAll(".modal-backdrop").forEach((backdrop) => {
      backdrop.addEventListener("click", (e) => {
        if (e.target === backdrop) this.closeAllModals();
      });
    });

    // Global Esc key to close modals
    window.addEventListener("keydown", (e) => {
      if (e.key === "Escape") this.closeAllModals();
    });

    // Password toggles on Auth Screen & Modals
    const toggleSignInPwd = document.getElementById("btn-toggle-signin-pwd");
    if (toggleSignInPwd) {
      toggleSignInPwd.addEventListener("click", () => {
        const p = document.getElementById("signin-password");
        if (p) p.type = p.type === "password" ? "text" : "password";
      });
    }

    const toggleSignUpPwd = document.getElementById("btn-toggle-signup-pwd");
    if (toggleSignUpPwd) {
      toggleSignUpPwd.addEventListener("click", () => {
        const p = document.getElementById("signup-password");
        if (p) p.type = p.type === "password" ? "text" : "password";
      });
    }

    const toggleModalPwd = document.getElementById("btn-toggle-modal-pwd");
    if (toggleModalPwd) {
      toggleModalPwd.addEventListener("click", () => {
        const p = document.getElementById("form-acc-password");
        if (p) p.type = p.type === "password" ? "text" : "password";
      });
    }
  },

  escapeHTML(str) {
    if (!str && str !== 0) return "";
    return String(str)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#039;");
  },
};

window.AccFoUI = AccFoUI;
