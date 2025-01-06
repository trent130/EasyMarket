class MockRedis {
  private store: { [key: string]: string } = {};

  /**
   * Sets a value in the mock Redis store. If expiryMode is 'EX' and time is a number, the value
   * will be deleted after the specified time period in seconds.
   * @param key The key to set.
   * @param value The value to set.
   * @param expiryMode The expiry mode.
   * @param time The time after which the value will expire.
   * @returns A promise that resolves with 'OK'.
   */
  async set(key: string, value: string, expiryMode?: string, time?: number): Promise<'OK'> {
    this.store[key] = value;
    if (expiryMode === 'EX' && time) {
      setTimeout(() => {
        delete this.store[key];
      }, time * 1000);
    }
    return 'OK';
  }

  /**
   * Retrieves a value from the mock Redis store.
   * @param key The key of the value to retrieve.
   * @returns The retrieved value, or null if the key does not exist.
   */
  async get(key: string): Promise<string | null> {
    return this.store[key] || null;
  }

  /**
   * Deletes a value from the mock Redis store.
   * @param key The key of the value to delete.
   * @returns 1 if the key existed, 0 if it did not.
   */
  async del(key: string): Promise<number> {
    if (this.store[key]) {
      delete this.store[key];
      return 1;
    }
    return 0;
  }
}

export const redis = new MockRedis();
