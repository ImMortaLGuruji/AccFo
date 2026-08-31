/**
 * AccFo Local File System Access & Storage Engine
 * Enables true local data ownership via File System Access API (FileSystemFileHandle)
 * and seamless IndexedDB handle persistence.
 */

const AccFoFS = {
  DB_NAME: "AccFo_Storage",
  STORE_NAME: "handles",
  KEY_FILE_HANDLE: "linked_vault_handle",
  KEY_ENCRYPTED_VAULT: "cached_encrypted_vault",

  isSupported() {
    return "showOpenFilePicker" in window && "showSaveFilePicker" in window;
  },

  /**
   * Initializes IndexedDB for handle persistence
   */
  async openDB() {
    return new Promise((resolve, reject) => {
      const request = indexedDB.open(this.DB_NAME, 1);
      request.onupgradeneeded = (e) => {
        const db = e.target.result;
        if (!db.objectStoreNames.contains(this.STORE_NAME)) {
          db.createObjectStore(this.STORE_NAME);
        }
      };
      request.onsuccess = () => resolve(request.result);
      request.onerror = () => reject(request.error);
    });
  },

  /**
   * Persists a FileSystemFileHandle in IndexedDB
   */
  async saveStoredHandle(handle) {
    try {
      const db = await this.openDB();
      const tx = db.transaction(this.STORE_NAME, "readwrite");
      tx.objectStore(this.STORE_NAME).put(handle, this.KEY_FILE_HANDLE);
      return new Promise((resolve) => {
        tx.oncomplete = () => resolve(true);
        tx.onerror = () => resolve(false);
      });
    } catch (err) {
      console.warn("Failed to save file handle in IndexedDB:", err);
      return false;
    }
  },

  /**
   * Retrieves previously saved FileSystemFileHandle from IndexedDB
   */
  async getStoredHandle() {
    try {
      const db = await this.openDB();
      const tx = db.transaction(this.STORE_NAME, "readonly");
      const request = tx.objectStore(this.STORE_NAME).get(this.KEY_FILE_HANDLE);
      return new Promise((resolve) => {
        request.onsuccess = () => resolve(request.result || null);
        request.onerror = () => resolve(null);
      });
    } catch {
      return null;
    }
  },

  /**
   * Removes saved FileSystemFileHandle from IndexedDB
   */
  async clearStoredHandle() {
    try {
      const db = await this.openDB();
      const tx = db.transaction(this.STORE_NAME, "readwrite");
      tx.objectStore(this.STORE_NAME).delete(this.KEY_FILE_HANDLE);
      return new Promise((resolve) => {
        tx.oncomplete = () => resolve(true);
        tx.onerror = () => resolve(false);
      });
    } catch {
      return false;
    }
  },

  /**
   * Verifies / prompts read & write permission on a file handle
   */
  async verifyPermission(fileHandle, readWrite = true) {
    if (!fileHandle) return false;
    const options = { mode: readWrite ? "readwrite" : "read" };

    // Check current permission state
    if ((await fileHandle.queryPermission(options)) === "granted") {
      return true;
    }

    // Request permission if not already granted
    if ((await fileHandle.requestPermission(options)) === "granted") {
      return true;
    }

    return false;
  },

  /**
   * Prompts user to pick a new local file location to create/link an .accfo vault
   * @param {string} suggestedName
   * @returns {Promise<FileSystemFileHandle>}
   */
  async createNewLocalFile(suggestedName = "my_vault.accfo") {
    if (!this.isSupported()) {
      throw new Error(
        "File System Access API is not supported on this browser.",
      );
    }

    const handle = await window.showSaveFilePicker({
      suggestedName: suggestedName,
      types: [
        {
          description: "AccFo Encrypted Vault (*.accfo)",
          accept: { "application/json": [".accfo", ".json"] },
        },
      ],
    });

    await this.saveStoredHandle(handle);
    return handle;
  },

  /**
   * Prompts user to link an existing local vault file
   * @returns {Promise<FileSystemFileHandle>}
   */
  async pickExistingLocalFile() {
    if (!this.isSupported()) {
      throw new Error(
        "File System Access API is not supported on this browser.",
      );
    }

    const [handle] = await window.showOpenFilePicker({
      types: [
        {
          description: "AccFo Encrypted Vault (*.accfo, *.json)",
          accept: { "application/json": [".accfo", ".json"] },
        },
      ],
      multiple: false,
    });

    await this.saveStoredHandle(handle);
    return handle;
  },

  /**
   * Writes string data directly to the linked local file
   * @param {FileSystemFileHandle} handle
   * @param {string} content
   */
  async writeToFile(handle, content) {
    if (!handle) throw new Error("No local file handle provided.");
    const hasPerm = await this.verifyPermission(handle, true);
    if (!hasPerm) throw new Error("File write permission was denied.");

    const writable = await handle.createWritable();
    await writable.write(content);
    await writable.close();
  },

  /**
   * Reads text content from a FileSystemFileHandle
   * @param {FileSystemFileHandle} handle
   * @returns {Promise<string>}
   */
  async readFromFile(handle) {
    if (!handle) throw new Error("No local file handle provided.");
    const hasPerm = await this.verifyPermission(handle, false);
    if (!hasPerm) throw new Error("File read permission was denied.");

    const file = await handle.getFile();
    return await file.text();
  },

  /**
   * Fallback for downloading vault file directly in browsers without File System Access API
   * @param {string} filename
   * @param {string} content
   */
  downloadFallback(filename, content) {
    const blob = new Blob([content], {
      type: "application/json;charset=utf-8",
    });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = filename.endsWith(".accfo") ? filename : `${filename}.accfo`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  },

  /**
   * Reads an uploaded File object (from standard <input type="file">)
   * @param {File} file
   * @returns {Promise<string>}
   */
  async readUploadedFile(file) {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = (e) => resolve(e.target.result);
      reader.onerror = () => reject(reader.error);
      reader.readAsText(file);
    });
  },
};

window.AccFoFS = AccFoFS;
