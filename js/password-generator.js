/**
 * AccFo Cryptographically Secure Password & Passphrase Generator
 * Uses window.crypto.getRandomValues with zero-bias rejection sampling CSPRNG.
 */

const AccFoGenerator = {
  CHARSETS: {
    uppercase: "ABCDEFGHJKLMNPQRSTUVWXYZ",
    uppercaseAll: "ABCDEFGHIJKLMNOPQRSTUVWXYZ",
    lowercase: "abcdefghijkmnopqrstuvwxyz",
    lowercaseAll: "abcdefghijklmnopqrstuvwxyz",
    numbers: "23456789",
    numbersAll: "0123456789",
    symbols: "@#$%^&*()_+-=[]{}|;:,.<>?~",
    ambiguous: "1lI0O8B",
  },

  WORDS: [
    "anchor",
    "beacon",
    "breeze",
    "bridge",
    "castle",
    "canyon",
    "cherry",
    "cipher",
    "comet",
    "copper",
    "cosmic",
    "crater",
    "crystal",
    "delta",
    "dragon",
    "eagle",
    "echo",
    "ember",
    "falcon",
    "feather",
    "forest",
    "fossil",
    "galaxy",
    "garden",
    "glacier",
    "granite",
    "harbor",
    "haven",
    "horizon",
    "island",
    "jasper",
    "jungle",
    "knight",
    "lagoon",
    "legend",
    "lotus",
    "lunar",
    "marble",
    "meadow",
    "meteor",
    "monarch",
    "mountain",
    "nebula",
    "nexus",
    "oasis",
    "ocean",
    "orbit",
    "orchid",
    "pacific",
    "palace",
    "phoenix",
    "pillar",
    "planet",
    "portal",
    "prism",
    "pulsar",
    "pyramid",
    "quantum",
    "quartz",
    "quest",
    "radar",
    "radiant",
    "ranger",
    "rebel",
    "ridge",
    "river",
    "rocket",
    "ruby",
    "safari",
    "samurai",
    "saphir",
    "saturn",
    "shadow",
    "shield",
    "siren",
    "solar",
    "spark",
    "sphinx",
    "spirit",
    "summit",
    "sunset",
    "thunder",
    "titan",
    "topaz",
    "torrent",
    "tower",
    "tsunami",
    "tulip",
    "tundra",
    "typhoon",
    "unicorn",
    "valley",
    "vector",
    "velvet",
    "vessel",
    "viper",
    "vortex",
    "voyage",
    "vulcan",
    "walnut",
    "wander",
    "wave",
    "whisper",
    "willow",
    "winter",
    "wizard",
    "wolf",
    "zenith",
    "zephyr",
    "zodiac",
  ],

  /**
   * Generates a mathematically unbiased random integer in [0, max) using CSPRNG rejection sampling
   * @param {number} max
   * @returns {number}
   */
  getRandomInt(max) {
    if (max <= 0) return 0;
    if (max === 1) return 0;

    // Zero-bias rejection sampling over 32-bit integer space
    const maxUint32 = 0xffffffff;
    const limit = maxUint32 - (maxUint32 % max);
    const randomBuffer = new Uint32Array(1);

    let val;
    do {
      window.crypto.getRandomValues(randomBuffer);
      val = randomBuffer[0];
    } while (val >= limit);

    return val % max;
  },

  /**
   * Generates a random character string based on user options
   */
  generatePassword(options = {}) {
    const length = Math.max(8, Math.min(128, options.length || 18));
    const includeUpper = options.uppercase !== false;
    const includeLower = options.lowercase !== false;
    const includeNumbers = options.numbers !== false;
    const includeSymbols = options.symbols !== false;
    const avoidAmbiguous = options.avoidAmbiguous === true;

    let availableChars = "";
    const guaranteedChars = [];

    if (includeUpper) {
      const set = avoidAmbiguous
        ? this.CHARSETS.uppercase
        : this.CHARSETS.uppercaseAll;
      availableChars += set;
      guaranteedChars.push(set[this.getRandomInt(set.length)]);
    }

    if (includeLower) {
      const set = avoidAmbiguous
        ? this.CHARSETS.lowercase
        : this.CHARSETS.lowercaseAll;
      availableChars += set;
      guaranteedChars.push(set[this.getRandomInt(set.length)]);
    }

    if (includeNumbers) {
      const set = avoidAmbiguous
        ? this.CHARSETS.numbers
        : this.CHARSETS.numbersAll;
      availableChars += set;
      guaranteedChars.push(set[this.getRandomInt(set.length)]);
    }

    if (includeSymbols) {
      const set = this.CHARSETS.symbols;
      availableChars += set;
      guaranteedChars.push(set[this.getRandomInt(set.length)]);
    }

    if (!availableChars) {
      availableChars = this.CHARSETS.lowercaseAll + this.CHARSETS.numbersAll;
    }

    const passwordArr = [...guaranteedChars];
    while (passwordArr.length < length) {
      const char = availableChars[this.getRandomInt(availableChars.length)];
      passwordArr.push(char);
    }

    // Fisher-Yates shuffle with unbiased CSPRNG
    for (let i = passwordArr.length - 1; i > 0; i--) {
      const j = this.getRandomInt(i + 1);
      [passwordArr[i], passwordArr[j]] = [passwordArr[j], passwordArr[i]];
    }

    return passwordArr.join("");
  },

  /**
   * Generates an easy-to-remember yet cryptographically secure passphrase
   */
  generatePassphrase(options = {}) {
    const wordCount = Math.max(3, Math.min(12, options.wordCount || 4));
    const separator = options.separator || "-";
    const capitalize = options.capitalize !== false;
    const includeNumber = options.includeNumber === true;

    const words = [];
    for (let i = 0; i < wordCount; i++) {
      let word = this.WORDS[this.getRandomInt(this.WORDS.length)];
      if (capitalize) {
        word = word.charAt(0).toUpperCase() + word.slice(1);
      }
      words.push(word);
    }

    if (includeNumber) {
      const num = this.getRandomInt(90) + 10;
      words.push(num.toString());
    }

    return words.join(separator);
  },
};

window.AccFoGenerator = AccFoGenerator;
