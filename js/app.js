/**
 * AccFo Master Application Coordinator
 * Handles authentication lifecycle, cryptographic key lifetime,
 * local file handle auto-sync, remote sync orchestration, and auto-lock security.
 */

class AccFoApp {
  constructor() {
    this.vault = new AccFoVault();
    this.masterKey = null;
    this.salt = null;
    this.username = "";
    this.isUnlocked = false;
    this.linkedFileHandle = null;
    this.autoLockMinutes = 15;
    this.autoLockTimeoutId = null;
    this.lastActivityTime = Date.now();
  }

  async init() {
    AccFoUI.init();
    this.setupEventListeners();
    this.setupActivityTracker();

    // Check for saved local file handle in IndexedDB
    try {
      const storedHandle = await AccFoFS.getStoredHandle();
      if (storedHandle) {
        this.linkedFileHandle = storedHandle;
        this.updateSyncBadge(`Linked: ${storedHandle.name}`, "emerald");
      }
    } catch (err) {
      console.warn("Could not restore file handle:", err);
    }

    // Check if account already exists
    const hasLocalAccount = this.hasStoredVault();
    if (hasLocalAccount) {
      this.showAuthMode("signin");
    } else {
      this.showAuthMode("signup");
    }
  }

  hasStoredVault() {
    return Boolean(
      localStorage.getItem("accfo_vault_salt") || this.linkedFileHandle,
    );
  }

  showAuthMode(mode) {
    document.querySelectorAll(".auth-nav-tab").forEach((tab) => {
      tab.classList.toggle("active", tab.getAttribute("data-tab") === mode);
    });

    const isSignUp = mode === "signup";
    const isRestore = mode === "restore";

    document.getElementById("auth-tab-signup").style.display = isSignUp
      ? "block"
      : "none";
    document.getElementById("auth-tab-signin").style.display =
      !isSignUp && !isRestore ? "block" : "none";
    document.getElementById("auth-tab-restore").style.display = isRestore
      ? "block"
      : "none";

    document.getElementById("auth-screen").style.display = "flex";
    document.getElementById("app-screen").style.display = "none";
  }

  /**
   * Creates a new Master Account & Vault
   */
  async handleSignUp(username, masterPassword, confirmPassword) {
    if (!username || username.trim().length < 2) {
      AccFoUI.showToast(
        "Please enter a vault identifier (min 2 characters)",
        "error",
      );
      return;
    }

    if (!masterPassword || masterPassword.length < 8) {
      AccFoUI.showToast(
        "Master password must be at least 8 characters long",
        "error",
      );
      return;
    }

    if (masterPassword !== confirmPassword) {
      AccFoUI.showToast("Master passwords do not match", "error");
      return;
    }

    try {
      AccFoUI.showToast("Deriving cryptographic key...", "info");

      // 1. Generate 16-byte cryptographic salt
      const salt = AccFoCrypto.generateSalt(16);
      this.salt = salt;
      this.username = username.trim();

      // 2. Derive 256-bit AES-GCM master key
      this.masterKey = await AccFoCrypto.deriveKey(masterPassword, salt);

      // 3. Initialize empty vault
      this.vault = new AccFoVault();
      this.vault.owner = this.username;

      // 4. Save salt & metadata in browser storage
      localStorage.setItem("accfo_vault_salt", AccFoCrypto.bufferToHex(salt));
      localStorage.setItem("accfo_vault_owner", this.username);

      // 5. Initial save and optional prompt to link a physical file
      await this.saveAndSync();

      this.isUnlocked = true;
      this.enterApp();
      AccFoUI.showToast("Vault initialized successfully", "success");

      // If File System Access API is supported and not yet linked, open prompt modal
      if (AccFoFS.isSupported() && !this.linkedFileHandle) {
        setTimeout(() => {
          AccFoUI.openModal("modal-prompt-link-file");
        }, 500);
      }
    } catch (err) {
      console.error("Sign up error:", err);
      AccFoUI.showToast("Initialization failed: " + err.message, "error");
    }
  }

  /**
   * Authenticates Master Password & Decrypts Vault
   */
  async handleSignIn(masterPassword) {
    if (!masterPassword) {
      AccFoUI.showToast("Enter your master password", "error");
      return;
    }

    try {
      AccFoUI.showToast("Decrypting vault...", "info");

      // Retrieve salt
      let saltHex = localStorage.getItem("accfo_vault_salt");
      let encryptedPayload = null;

      // Check if we have a linked file handle to read from directly
      if (this.linkedFileHandle) {
        try {
          const fileContent = await AccFoFS.readFromFile(this.linkedFileHandle);
          const parsed = JSON.parse(fileContent);
          if (parsed.salt) saltHex = parsed.salt;
          encryptedPayload = parsed;
        } catch (fileErr) {
          console.warn("Could not read from linked file handle:", fileErr);
        }
      }

      // If not from file, read from local storage cache
      if (!encryptedPayload) {
        const cached = localStorage.getItem("accfo_encrypted_vault");
        if (cached) {
          encryptedPayload = JSON.parse(cached);
          if (encryptedPayload.salt) saltHex = encryptedPayload.salt;
        }
      }

      if (!saltHex) {
        AccFoUI.showToast(
          "No vault found on this device. Create a vault or restore a backup.",
          "error",
        );
        return;
      }

      const salt = AccFoCrypto.hexToBuffer(saltHex);
      this.salt = salt;

      // Derive key
      const key = await AccFoCrypto.deriveKey(masterPassword, salt);

      // Decrypt
      if (
        encryptedPayload &&
        encryptedPayload.ciphertext &&
        encryptedPayload.iv
      ) {
        try {
          const decryptedData = await AccFoCrypto.decrypt(
            encryptedPayload.ciphertext,
            encryptedPayload.iv,
            key,
          );
          this.vault = new AccFoVault();
          this.vault.loadData(decryptedData);
        } catch (decryptErr) {
          AccFoUI.showToast("Incorrect master password", "error");
          return;
        }
      } else {
        // Fresh empty vault
        this.vault = new AccFoVault();
        this.vault.owner = localStorage.getItem("accfo_vault_owner") || "User";
      }

      this.masterKey = key;
      this.username =
        this.vault.owner || localStorage.getItem("accfo_vault_owner") || "User";
      this.isUnlocked = true;

      this.enterApp();
      AccFoUI.showToast(`Vault unlocked (${this.username})`, "success");

      // Background remote sync check
      this.checkRemoteSync();
    } catch (err) {
      console.error("Sign in error:", err);
      AccFoUI.showToast("Sign in failed: " + err.message, "error");
    }
  }

  /**
   * Enters the unlocked dashboard
   */
  enterApp() {
    document.getElementById("auth-screen").style.display = "none";
    document.getElementById("app-screen").style.display = "block";
    document.getElementById("nav-user-label").textContent = this.username;

    this.resetInactivityTimer();
    AccFoUI.switchView("vault");
  }

  /**
   * Locks the vault, purges cryptographic keys, and wipes DOM cards
   */
  lockVault() {
    this.masterKey = null;
    this.salt = null;
    this.isUnlocked = false;
    this.vault = new AccFoVault();

    if (this.autoLockTimeoutId) {
      clearTimeout(this.autoLockTimeoutId);
      this.autoLockTimeoutId = null;
    }

    // Wipe password inputs & sensitive card containers
    const signinPwd = document.getElementById("signin-password");
    if (signinPwd) signinPwd.value = "";
    const signupPwd = document.getElementById("signup-password");
    if (signupPwd) signupPwd.value = "";
    const signupConf = document.getElementById("signup-confirm-password");
    if (signupConf) signupConf.value = "";
    const modalPwd = document.getElementById("form-acc-password");
    if (modalPwd) modalPwd.value = "";

    const grid = document.getElementById("vault-cards-grid");
    if (grid) grid.innerHTML = "";

    // Clear clipboard for safety
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText("").catch(() => {});
    }

    this.showAuthMode("signin");
    AccFoUI.showToast("Vault locked", "info");
  }

  /**
   * Encrypts and saves the current vault state
   */
  async saveAndSync() {
    if (!this.masterKey || !this.salt) return;

    try {
      const dataToEncrypt = this.vault.exportData();
      const encrypted = await AccFoCrypto.encrypt(
        dataToEncrypt,
        this.masterKey,
      );

      const vaultPackage = {
        version: "2.0",
        salt: AccFoCrypto.bufferToHex(this.salt),
        iv: encrypted.iv,
        ciphertext: encrypted.ciphertext,
        owner: this.vault.owner || this.username,
        lastModified: Date.now(),
      };

      const vaultJSON = JSON.stringify(vaultPackage, null, 2);

      // 1. Save to local browser cache
      localStorage.setItem("accfo_encrypted_vault", vaultJSON);

      // 2. Write to linked physical local file if handle is present
      if (this.linkedFileHandle) {
        try {
          await AccFoFS.writeToFile(this.linkedFileHandle, vaultJSON);
          this.updateSyncBadge(
            `Synced: ${this.linkedFileHandle.name}`,
            "emerald",
          );
        } catch (fileErr) {
          console.warn("Could not auto-save to local file handle:", fileErr);
          this.updateSyncBadge(`Save failed: ${fileErr.message}`, "amber");
        }
      }

      // 3. Dispatch to remote sync backend if active
      AccFoSync.uploadVault(vaultJSON).then((res) => {
        if (
          res.success &&
          AccFoSync.getConfig().provider !== AccFoSync.PROVIDERS.NONE
        ) {
          this.updateSyncBadge(res.message, "emerald");
        }
      });
    } catch (err) {
      console.error("Save and sync error:", err);
      AccFoUI.showToast("Failed to save: " + err.message, "error");
    }
  }

  /**
   * Checks remote sync for newer updates
   */
  async checkRemoteSync() {
    const config = AccFoSync.getConfig();
    if (!config || config.provider === AccFoSync.PROVIDERS.NONE) return;

    try {
      const res = await AccFoSync.fetchVault(config);
      if (res.success && res.data && this.masterKey) {
        const remoteParsed = JSON.parse(res.data);
        if (
          remoteParsed.lastModified &&
          remoteParsed.lastModified > (this.vault.lastModified || 0)
        ) {
          // Newer remote version detected! Decrypt and merge
          const decrypted = await AccFoCrypto.decrypt(
            remoteParsed.ciphertext,
            remoteParsed.iv,
            this.masterKey,
          );
          this.vault.loadData(decrypted);
          AccFoUI.showToast(
            "Vault synchronized with remote changes",
            "success",
          );
          AccFoUI.renderVault();
        }
      }
    } catch (err) {
      console.warn("Remote sync check warning:", err);
    }
  }

  /**
   * Links a new physical local file (.accfo)
   */
  async linkNewFile() {
    try {
      const safeName = (this.username || "vault")
        .replace(/[^a-zA-Z0-9_-]/g, "_")
        .toLowerCase();
      const filename = `${safeName}_vault.accfo`;
      const handle = await AccFoFS.createNewLocalFile(filename);
      this.linkedFileHandle = handle;
      await this.saveAndSync();
      AccFoUI.closeModal("modal-prompt-link-file");
      AccFoUI.showToast(`Linked to ${handle.name}`, "success");
      this.updateSyncBadge(`Linked: ${handle.name}`, "emerald");
      AccFoUI.renderSettingsView();
    } catch (err) {
      if (err.name !== "AbortError") {
        AccFoUI.showToast("File linking cancelled: " + err.message, "error");
      }
    }
  }

  /**
   * Links an existing physical local file (.accfo)
   */
  async linkExistingFile() {
    try {
      const handle = await AccFoFS.pickExistingLocalFile();
      this.linkedFileHandle = handle;

      const content = await AccFoFS.readFromFile(handle);
      const parsed = JSON.parse(content);

      if (parsed.salt && this.masterKey) {
        try {
          const decrypted = await AccFoCrypto.decrypt(
            parsed.ciphertext,
            parsed.iv,
            this.masterKey,
          );
          this.vault.loadData(decrypted);
          AccFoUI.renderVault();
        } catch {
          AccFoUI.showToast("Linked file uses a different master key", "info");
        }
      }

      this.updateSyncBadge(`Linked: ${handle.name}`, "emerald");
      AccFoUI.closeModal("modal-prompt-link-file");
      AccFoUI.showToast(`Linked to ${handle.name}`, "success");
      AccFoUI.renderSettingsView();
    } catch (err) {
      if (err.name !== "AbortError") {
        AccFoUI.showToast("Failed to link file: " + err.message, "error");
      }
    }
  }

  /**
   * Unlinks local file handle
   */
  async unlinkLocalFile() {
    this.linkedFileHandle = null;
    await AccFoFS.clearStoredHandle();
    this.updateSyncBadge("Local Storage", "cyan");
    AccFoUI.showToast("Local file unlinked", "info");
    AccFoUI.renderSettingsView();
  }

  updateSyncBadge(text, colorType = "emerald") {
    const badge = document.getElementById("nav-sync-status-pill");
    const dot = document.getElementById("nav-sync-dot");
    const label = document.getElementById("nav-sync-label");

    if (!badge || !dot || !label) return;

    label.textContent = text;
    dot.className = "status-dot";
    if (colorType === "amber") dot.classList.add("syncing");
    if (colorType === "cyan") dot.classList.add("offline");
  }

  setupActivityTracker() {
    const reset = () => this.resetInactivityTimer();
    window.addEventListener("mousemove", reset, { passive: true });
    window.addEventListener("keydown", reset, { passive: true });
    window.addEventListener("touchstart", reset, { passive: true });
  }

  resetInactivityTimer() {
    if (!this.isUnlocked) return;
    this.lastActivityTime = Date.now();

    if (this.autoLockTimeoutId) {
      clearTimeout(this.autoLockTimeoutId);
    }

    if (this.autoLockMinutes > 0) {
      this.autoLockTimeoutId = setTimeout(
        () => {
          if (this.isUnlocked) {
            this.lockVault();
          }
        },
        this.autoLockMinutes * 60 * 1000,
      );
    }
  }

  setupEventListeners() {
    // Auth Tabs
    document.querySelectorAll(".auth-nav-tab").forEach((tab) => {
      tab.addEventListener("click", () => {
        const mode = tab.getAttribute("data-tab");
        if (mode) this.showAuthMode(mode);
      });
    });

    // Sign Up Form Submit
    const signupForm = document.getElementById("form-signup");
    if (signupForm) {
      signupForm.addEventListener("submit", (e) => {
        e.preventDefault();
        const username = document.getElementById("signup-username").value;
        const password = document.getElementById("signup-password").value;
        const confirm = document.getElementById(
          "signup-confirm-password",
        ).value;
        this.handleSignUp(username, password, confirm);
      });
    }

    // Sign In Form Submit
    const signinForm = document.getElementById("form-signin");
    if (signinForm) {
      signinForm.addEventListener("submit", (e) => {
        e.preventDefault();
        const password = document.getElementById("signin-password").value;
        this.handleSignIn(password);
      });
    }

    // Live Password Strength Meter on Sign Up
    const signupPwdInput = document.getElementById("signup-password");
    if (signupPwdInput) {
      signupPwdInput.addEventListener("input", (e) => {
        const strength = AccFoCrypto.evaluateStrength(e.target.value);
        const fill = document.getElementById("signup-strength-bar");
        const label = document.getElementById("signup-strength-label");
        if (fill && label) {
          fill.style.width = `${Math.min(100, (strength.score / 5) * 100)}%`;
          fill.style.backgroundColor = strength.color;
          label.textContent = `${strength.label} (${strength.entropy} bits)`;
          label.style.color = strength.color;
        }
      });
    }

    // Account Editor Form Submit (Add / Edit)
    const accForm = document.getElementById("form-account-editor");
    if (accForm) {
      accForm.addEventListener("submit", (e) => {
        e.preventDefault();
        const data = {
          service: document.getElementById("form-acc-service").value,
          username: document.getElementById("form-acc-username").value,
          password: document.getElementById("form-acc-password").value,
          url: document.getElementById("form-acc-url").value,
          category: document.getElementById("form-acc-category").value,
          notes: document.getElementById("form-acc-notes").value,
        };

        if (AccFoUI.activeEditingId) {
          this.vault.updateAccount(AccFoUI.activeEditingId, data);
          AccFoUI.showToast("Item updated", "success");
        } else {
          this.vault.addAccount(data);
          AccFoUI.showToast("Item saved to vault", "success");
        }

        this.saveAndSync();
        AccFoUI.closeModal("modal-account-editor");
        AccFoUI.renderVault();
      });
    }

    // Inline Generate Password inside Account Editor Modal
    const inlineGenBtn = document.getElementById("btn-inline-generate-pwd");
    if (inlineGenBtn) {
      inlineGenBtn.addEventListener("click", () => {
        const pwd = AccFoGenerator.generatePassword({ length: 18 });
        document.getElementById("form-acc-password").value = pwd;
        AccFoUI.showToast("Generated 18-character password", "info");
      });
    }

    // Lock Vault Buttons
    document.querySelectorAll('[data-action="lock-vault"]').forEach((btn) => {
      btn.addEventListener("click", () => this.lockVault());
    });

    // Add Account Buttons
    document.querySelectorAll('[data-action="add-account"]').forEach((btn) => {
      btn.addEventListener("click", () => AccFoUI.handleOpenAddModal());
    });

    // Sync Provider Tab switching in Settings
    document.querySelectorAll(".provider-tab").forEach((tab) => {
      tab.addEventListener("click", () => {
        const provider = tab.getAttribute("data-provider");
        const cfg = AccFoSync.getConfig();
        cfg.provider = provider;
        AccFoSync.saveConfig(cfg);
        AccFoUI.renderSettingsView();
        AccFoUI.showToast(`Provider set to ${provider}`, "info");
      });
    });

    // Save WebDAV Config
    const btnSaveWebdav = document.getElementById("btn-save-webdav");
    if (btnSaveWebdav) {
      btnSaveWebdav.addEventListener("click", () => {
        const url = document.getElementById("webdav-url").value.trim();
        const user = document.getElementById("webdav-user").value.trim();
        const pass = document.getElementById("webdav-pass").value;

        const cfg = AccFoSync.getConfig();
        cfg.provider = AccFoSync.PROVIDERS.WEBDAV;
        cfg.webdav = {
          url,
          username: user,
          password: pass,
          filename: "accfo_vault.accfo",
        };
        AccFoSync.saveConfig(cfg);

        this.saveAndSync();
        AccFoUI.showToast("WebDAV settings saved", "success");
      });
    }

    // Save Self-Hosted Config
    const btnSaveSelfHosted = document.getElementById("btn-save-self-hosted");
    if (btnSaveSelfHosted) {
      btnSaveSelfHosted.addEventListener("click", () => {
        const endpoint = document
          .getElementById("self-hosted-endpoint")
          .value.trim();
        const token = document.getElementById("self-hosted-token").value.trim();

        const cfg = AccFoSync.getConfig();
        cfg.provider = AccFoSync.PROVIDERS.SELF_HOSTED;
        cfg.selfHosted = { endpoint, token };
        AccFoSync.saveConfig(cfg);

        this.saveAndSync();
        AccFoUI.showToast("Self-hosted settings saved", "success");
      });
    }

    // File Drop & Import
    const importInput = document.getElementById("import-file-input");
    if (importInput) {
      importInput.addEventListener("change", async (e) => {
        const file = e.target.files[0];
        if (!file) return;

        try {
          const text = await AccFoFS.readUploadedFile(file);
          let imported = [];

          if (file.name.endsWith(".csv")) {
            imported = AccFoMigration.parseCSV(text);
          } else {
            // Check if encrypted .accfo vault or raw JSON
            try {
              const parsed = JSON.parse(text);
              if (
                parsed.ciphertext &&
                parsed.iv &&
                parsed.salt &&
                this.masterKey
              ) {
                const decrypted = await AccFoCrypto.decrypt(
                  parsed.ciphertext,
                  parsed.iv,
                  this.masterKey,
                );
                imported = decrypted.accounts || [];
              } else {
                imported = AccFoMigration.parseJSON(text);
              }
            } catch {
              imported = AccFoMigration.parseJSON(text);
            }
          }

          if (imported.length > 0) {
            const count = this.vault.importAccounts(imported, "merge");
            await this.saveAndSync();
            AccFoUI.closeModal("modal-import-credentials");
            AccFoUI.renderVault();
            AccFoUI.showToast(`Imported ${count} items`, "success");
          } else {
            AccFoUI.showToast("No valid items found in file", "error");
          }
        } catch (err) {
          AccFoUI.showToast("Import error: " + err.message, "error");
        }
      });
    }

    // Export Backup Button
    const btnExport = document.getElementById("btn-export-vault");
    if (btnExport) {
      btnExport.addEventListener("click", () => {
        const cached = localStorage.getItem("accfo_encrypted_vault");
        if (cached) {
          const filename = `${(this.username || "accfo").toLowerCase()}_backup_${new Date().toISOString().slice(0, 10)}.accfo`;
          AccFoFS.downloadFallback(filename, cached);
          AccFoUI.showToast("Encrypted backup exported", "success");
        }
      });
    }
  }
}

// Instantiate and attach to global window
window.accfoApp = new AccFoApp();
window.addEventListener("DOMContentLoaded", () => {
  window.accfoApp.init();
});
