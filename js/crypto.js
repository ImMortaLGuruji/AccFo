/**
 * AccFo Cryptographic Engine
 * Zero-Knowledge Client-Side Cryptography using native Web Cryptography API (crypto.subtle)
 * - Key Derivation: PBKDF2-HMAC-SHA256 with 600,000 iterations (OWASP standard)
 * - Authenticated Encryption: AES-256-GCM with unique 12-byte CSPRNG IVs per record
 * - Secure Random: window.crypto.getRandomValues (CSPRNG)
 */

const AccFoCrypto = {
  PBKDF2_ITERATIONS: 600000,
  SALT_LENGTH: 16,
  IV_LENGTH: 12,

  /**
   * Generates a cryptographically secure random salt
   * @param {number} len Length in bytes
   * @returns {Uint8Array}
   */
  generateSalt(len = 16) {
    const salt = new Uint8Array(len);
    window.crypto.getRandomValues(salt);
    return salt;
  },

  /**
   * Generates a cryptographically secure 12-byte IV for AES-GCM
   * @returns {Uint8Array}
   */
  generateIV() {
    const iv = new Uint8Array(this.IV_LENGTH);
    window.crypto.getRandomValues(iv);
    return iv;
  },

  /**
   * Converts a Uint8Array or ArrayBuffer to a hex string
   * @param {Uint8Array|ArrayBuffer} buffer
   * @returns {string}
   */
  bufferToHex(buffer) {
    if (!buffer) return "";
    return Array.from(new Uint8Array(buffer))
      .map((b) => b.toString(16).padStart(2, "0"))
      .join("");
  },

  /**
   * Safely converts a hex string to a Uint8Array with validation
   * @param {string} hex
   * @returns {Uint8Array}
   */
  hexToBuffer(hex) {
    if (!hex || typeof hex !== "string") return new Uint8Array(0);
    const cleanHex = hex.trim().replace(/^0x/i, "");
    if (cleanHex.length % 2 !== 0) {
      throw new Error(
        "Invalid hex string length for cryptographic conversion.",
      );
    }
    const bytes = new Uint8Array(cleanHex.length / 2);
    for (let i = 0; i < bytes.length; i++) {
      const byteVal = parseInt(cleanHex.substr(i * 2, 2), 16);
      if (isNaN(byteVal)) {
        throw new Error("Invalid character in cryptographic hex string.");
      }
      bytes[i] = byteVal;
    }
    return bytes;
  },

  /**
   * Converts a UTF-8 string to Uint8Array
   * @param {string} str
   * @returns {Uint8Array}
   */
  strToBuffer(str) {
    return new TextEncoder().encode(str || "");
  },

  /**
   * Converts a Uint8Array to UTF-8 string
   * @param {Uint8Array|ArrayBuffer} buffer
   * @returns {string}
   */
  bufferToStr(buffer) {
    return new TextDecoder("utf-8").decode(buffer);
  },

  /**
   * Derives a 256-bit AES-GCM CryptoKey from master password and salt using PBKDF2-SHA256
   * Key is non-extractable (extractable: false) to prevent memory-dump extraction via subtle API
   * @param {string} masterPassword
   * @param {Uint8Array|string} salt
   * @returns {Promise<CryptoKey>}
   */
  async deriveKey(masterPassword, salt) {
    if (!masterPassword || typeof masterPassword !== "string") {
      throw new Error("Master password is required for key derivation.");
    }

    const saltBuffer = typeof salt === "string" ? this.hexToBuffer(salt) : salt;
    if (!saltBuffer || saltBuffer.byteLength < 16) {
      throw new Error("Cryptographic salt must be at least 16 bytes.");
    }

    const passwordBuffer = this.strToBuffer(masterPassword);

    const baseKey = await window.crypto.subtle.importKey(
      "raw",
      passwordBuffer,
      { name: "PBKDF2" },
      false,
      ["deriveKey"],
    );

    return await window.crypto.subtle.deriveKey(
      {
        name: "PBKDF2",
        salt: saltBuffer,
        iterations: this.PBKDF2_ITERATIONS,
        hash: "SHA-256",
      },
      baseKey,
      { name: "AES-GCM", length: 256 },
      false, // non-extractable
      ["encrypt", "decrypt"],
    );
  },

  /**
   * Computes SHA-256 hash of a string, returned as hex
   * @param {string} text
   * @returns {Promise<string>}
   */
  async sha256(text) {
    const buffer = this.strToBuffer(text);
    const hash = await window.crypto.subtle.digest("SHA-256", buffer);
    return this.bufferToHex(hash);
  },

  /**
   * Encrypts arbitrary JavaScript object or string with AES-256-GCM
   * Generates a fresh, cryptographically secure 96-bit IV for every encryption call
   * @param {any} data
   * @param {CryptoKey} cryptoKey
   * @returns {Promise<{iv: string, ciphertext: string}>}
   */
  async encrypt(data, cryptoKey) {
    if (!cryptoKey) throw new Error("Encryption key is required.");
    const iv = this.generateIV();
    const plaintext = typeof data === "string" ? data : JSON.stringify(data);
    const encoded = this.strToBuffer(plaintext);

    const ciphertextBuffer = await window.crypto.subtle.encrypt(
      { name: "AES-GCM", iv: iv },
      cryptoKey,
      encoded,
    );

    return {
      iv: this.bufferToHex(iv),
      ciphertext: this.bufferToHex(ciphertextBuffer),
    };
  },

  /**
   * Decrypts AES-256-GCM ciphertext back into original object or string
   * Throws an error if ciphertext or tag was tampered with (authenticated encryption)
   * @param {string} ciphertextHex
   * @param {string} ivHex
   * @param {CryptoKey} cryptoKey
   * @returns {Promise<any>}
   */
  async decrypt(ciphertextHex, ivHex, cryptoKey) {
    if (!cryptoKey) throw new Error("Decryption key is required.");
    if (!ciphertextHex || !ivHex) {
      throw new Error("Ciphertext and initialization vector are required.");
    }

    const iv = this.hexToBuffer(ivHex);
    const ciphertext = this.hexToBuffer(ciphertextHex);

    const decryptedBuffer = await window.crypto.subtle.decrypt(
      { name: "AES-GCM", iv: iv },
      cryptoKey,
      ciphertext,
    );

    const plaintext = this.bufferToStr(decryptedBuffer);
    try {
      return JSON.parse(plaintext);
    } catch {
      return plaintext;
    }
  },

  /**
   * Evaluates password entropy and strength metrics
   * @param {string} password
   * @returns {{score: number, entropy: number, label: string, color: string, crackTime: string}}
   */
  evaluateStrength(password) {
    if (!password) {
      return {
        score: 0,
        entropy: 0,
        label: "Empty",
        color: "#64748B",
        crackTime: "Instant",
      };
    }

    let poolSize = 0;
    if (/[a-z]/.test(password)) poolSize += 26;
    if (/[A-Z]/.test(password)) poolSize += 26;
    if (/[0-9]/.test(password)) poolSize += 10;
    if (/[^a-zA-Z0-9]/.test(password)) poolSize += 33;

    const entropy = Math.round(password.length * Math.log2(poolSize || 1));

    let score = 0;
    let label = "Very Weak";
    let color = "#FB3640";
    let crackTime = "A few seconds";

    if (entropy < 28) {
      score = 1;
      label = "Very Weak";
      color = "#FB3640";
      crackTime = "A few seconds";
    } else if (entropy < 45) {
      score = 2;
      label = "Weak";
      color = "#F59E0B";
      crackTime = "A few minutes";
    } else if (entropy < 65) {
      score = 3;
      label = "Fair";
      color = "#06B6D4";
      crackTime = "Several months";
    } else if (entropy < 85) {
      score = 4;
      label = "Strong";
      color = "#10B981";
      crackTime = "Hundreds of years";
    } else {
      score = 5;
      label = "Unbreakable";
      color = "#10B981";
      crackTime = "Trillions of centuries";
    }

    return { score, entropy, label, color, crackTime };
  },
};

window.AccFoCrypto = AccFoCrypto;
