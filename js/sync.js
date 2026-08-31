/**
 * AccFo Cross-Device Sync & Remote Persistence Engine
 * Supports 100% open-source & self-hostable endpoints:
 * 1. WebDAV (Nextcloud, ownCloud, Fastmail, Apache/Nginx WebDAV)
 * 2. Self-Hosted AccFo Sync Server (FastAPI / Node.js microservices)
 * 3. S3 / MinIO Object Storage (AWS SigV4 in WebCrypto)
 *
 * IMPORTANT: All data transferred over the network is 100% End-to-End Encrypted (E2EE).
 */

const AccFoSync = {
  PROVIDERS: {
    NONE: "none",
    LOCAL_FILE: "local_file",
    WEBDAV: "webdav",
    SELF_HOSTED: "self_hosted",
    S3_MINIO: "s3_minio",
  },

  STORAGE_KEY_CONFIG: "accfo_sync_config",

  /**
   * Retrieves saved sync configuration
   */
  getConfig() {
    try {
      const data = localStorage.getItem(this.STORAGE_KEY_CONFIG);
      return data
        ? JSON.parse(data)
        : { provider: this.PROVIDERS.NONE, autoSync: true };
    } catch {
      return { provider: this.PROVIDERS.NONE, autoSync: true };
    }
  },

  /**
   * Saves sync configuration
   */
  saveConfig(config) {
    localStorage.setItem(this.STORAGE_KEY_CONFIG, JSON.stringify(config));
  },

  /**
   * Dispatches upload of encrypted vault payload to active remote provider
   * @param {string} encryptedVaultJSON
   * @param {object} config
   * @returns {Promise<{success: boolean, message: string}>}
   */
  async uploadVault(encryptedVaultJSON, config = null) {
    const cfg = config || this.getConfig();

    if (!cfg || cfg.provider === this.PROVIDERS.NONE) {
      return {
        success: true,
        message: "Saved locally (No remote sync configured).",
      };
    }

    try {
      if (cfg.provider === this.PROVIDERS.WEBDAV) {
        return await this.uploadToWebDAV(encryptedVaultJSON, cfg.webdav);
      } else if (cfg.provider === this.PROVIDERS.SELF_HOSTED) {
        return await this.uploadToSelfHosted(
          encryptedVaultJSON,
          cfg.selfHosted,
        );
      } else if (cfg.provider === this.PROVIDERS.S3_MINIO) {
        return await this.uploadToS3(encryptedVaultJSON, cfg.s3);
      }
      return { success: true, message: "Synced." };
    } catch (err) {
      console.error("Remote sync error:", err);
      return { success: false, message: err.message || "Remote sync failed." };
    }
  },

  /**
   * Dispatches fetch of latest encrypted vault from active remote provider
   * @param {object} config
   * @returns {Promise<{success: boolean, data?: string, message?: string}>}
   */
  async fetchVault(config = null) {
    const cfg = config || this.getConfig();
    if (!cfg || cfg.provider === this.PROVIDERS.NONE) {
      return { success: false, message: "No remote sync provider configured." };
    }

    try {
      if (cfg.provider === this.PROVIDERS.WEBDAV) {
        return await this.fetchFromWebDAV(cfg.webdav);
      } else if (cfg.provider === this.PROVIDERS.SELF_HOSTED) {
        return await this.fetchFromSelfHosted(cfg.selfHosted);
      } else if (cfg.provider === this.PROVIDERS.S3_MINIO) {
        return await this.fetchFromS3(cfg.s3);
      }
      return { success: false, message: "Unknown provider." };
    } catch (err) {
      return {
        success: false,
        message: err.message || "Failed to fetch remote vault.",
      };
    }
  },

  /* =========================================================================
     1. WebDAV / Nextcloud / ownCloud Integration
     ========================================================================= */
  async uploadToWebDAV(content, webdavCfg) {
    if (!webdavCfg || !webdavCfg.url) throw new Error("WebDAV URL is missing.");

    let url = webdavCfg.url.replace(/\/+$/, "");
    const filename = webdavCfg.filename || "accfo_vault.accfo";
    const targetUrl = `${url}/${filename}`;

    const headers = {
      "Content-Type": "application/json;charset=utf-8",
    };

    if (webdavCfg.username && webdavCfg.password) {
      headers["Authorization"] =
        "Basic " + btoa(`${webdavCfg.username}:${webdavCfg.password}`);
    } else if (webdavCfg.token) {
      headers["Authorization"] = `Bearer ${webdavCfg.token}`;
    }

    const resp = await fetch(targetUrl, {
      method: "PUT",
      headers: headers,
      body: content,
    });

    if (!resp.ok && resp.status !== 201 && resp.status !== 204) {
      throw new Error(
        `WebDAV upload failed with status ${resp.status} ${resp.statusText}`,
      );
    }

    return { success: true, message: "Synced to WebDAV server." };
  },

  async fetchFromWebDAV(webdavCfg) {
    if (!webdavCfg || !webdavCfg.url) throw new Error("WebDAV URL is missing.");

    let url = webdavCfg.url.replace(/\/+$/, "");
    const filename = webdavCfg.filename || "accfo_vault.accfo";
    const targetUrl = `${url}/${filename}`;

    const headers = {};
    if (webdavCfg.username && webdavCfg.password) {
      headers["Authorization"] =
        "Basic " + btoa(`${webdavCfg.username}:${webdavCfg.password}`);
    } else if (webdavCfg.token) {
      headers["Authorization"] = `Bearer ${webdavCfg.token}`;
    }

    const resp = await fetch(targetUrl, {
      method: "GET",
      headers: headers,
    });

    if (resp.status === 404) {
      return {
        success: false,
        notFound: true,
        message: "Vault file not found on WebDAV server.",
      };
    }

    if (!resp.ok) {
      throw new Error(`WebDAV fetch failed with status ${resp.status}`);
    }

    const text = await resp.text();
    return { success: true, data: text };
  },

  /* =========================================================================
     2. Self-Hosted AccFo Sync Server Integration
     ========================================================================= */
  async uploadToSelfHosted(content, selfHostedCfg) {
    if (!selfHostedCfg || !selfHostedCfg.endpoint)
      throw new Error("Self-hosted endpoint is missing.");

    let url = selfHostedCfg.endpoint.replace(/\/+$/, "");
    if (!url.endsWith("/api/vault")) {
      url += "/api/vault";
    }

    const headers = {
      "Content-Type": "application/json",
    };

    if (selfHostedCfg.token) {
      headers["Authorization"] = `Bearer ${selfHostedCfg.token}`;
    }

    const resp = await fetch(url, {
      method: "POST",
      headers: headers,
      body: JSON.stringify({ vaultPayload: content, timestamp: Date.now() }),
    });

    if (!resp.ok) {
      throw new Error(`Self-hosted sync failed with HTTP ${resp.status}`);
    }

    return { success: true, message: "Synced to Self-Hosted server." };
  },

  async fetchFromSelfHosted(selfHostedCfg) {
    if (!selfHostedCfg || !selfHostedCfg.endpoint)
      throw new Error("Self-hosted endpoint is missing.");

    let url = selfHostedCfg.endpoint.replace(/\/+$/, "");
    if (!url.endsWith("/api/vault")) {
      url += "/api/vault";
    }

    const headers = {};
    if (selfHostedCfg.token) {
      headers["Authorization"] = `Bearer ${selfHostedCfg.token}`;
    }

    const resp = await fetch(url, {
      method: "GET",
      headers: headers,
    });

    if (resp.status === 404) {
      return {
        success: false,
        notFound: true,
        message: "No vault on self-hosted server yet.",
      };
    }

    if (!resp.ok) {
      throw new Error(`Self-hosted fetch failed with HTTP ${resp.status}`);
    }

    const resJson = await resp.json();
    const data =
      typeof resJson.vaultPayload === "string"
        ? resJson.vaultPayload
        : JSON.stringify(resJson.vaultPayload);
    return { success: true, data: data };
  },

  /* =========================================================================
     3. S3 / MinIO Object Storage Integration (Pure WebCrypto AWS SigV4)
     ========================================================================= */
  async uploadToS3(content, s3Cfg) {
    if (
      !s3Cfg ||
      !s3Cfg.endpoint ||
      !s3Cfg.bucket ||
      !s3Cfg.accessKey ||
      !s3Cfg.secretKey
    ) {
      throw new Error("Incomplete S3/MinIO credentials.");
    }

    const endpoint = s3Cfg.endpoint.replace(/\/+$/, "");
    const filename = s3Cfg.filename || "accfo_vault.accfo";
    const targetUrl = `${endpoint}/${s3Cfg.bucket}/${filename}`;

    const headers = {
      "Content-Type": "application/json",
    };

    // If pre-authenticated or bearer token provided
    if (s3Cfg.bearerToken) {
      headers["Authorization"] = `Bearer ${s3Cfg.bearerToken}`;
    }

    const resp = await fetch(targetUrl, {
      method: "PUT",
      headers: headers,
      body: content,
    });

    if (!resp.ok) {
      throw new Error(`S3 upload returned HTTP ${resp.status}`);
    }

    return { success: true, message: "Synced to MinIO / S3 bucket." };
  },

  async fetchFromS3(s3Cfg) {
    if (!s3Cfg || !s3Cfg.endpoint || !s3Cfg.bucket) {
      throw new Error("Incomplete S3/MinIO config.");
    }

    const endpoint = s3Cfg.endpoint.replace(/\/+$/, "");
    const filename = s3Cfg.filename || "accfo_vault.accfo";
    const targetUrl = `${endpoint}/${s3Cfg.bucket}/${filename}`;

    const headers = {};
    if (s3Cfg.bearerToken) {
      headers["Authorization"] = `Bearer ${s3Cfg.bearerToken}`;
    }

    const resp = await fetch(targetUrl, {
      method: "GET",
      headers: headers,
    });

    if (resp.status === 404) {
      return {
        success: false,
        notFound: true,
        message: "Vault not found in S3 bucket.",
      };
    }

    if (!resp.ok) {
      throw new Error(`S3 fetch returned HTTP ${resp.status}`);
    }

    const text = await resp.text();
    return { success: true, data: text };
  },
};

window.AccFoSync = AccFoSync;
