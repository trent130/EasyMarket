class MockRedis {
  private store: { [key: string]: string } = {};

  async set(key: string, value: string, expiryMode?: string, time?: number): Promise<'OK'> {
    this.store[key] = value;
    if (expiryMode === 'EX' && time) {
      setTimeout(() => {
        delete this.store[key];
      }, time * 1000);
    }
    return 'OK';
  }

  async get(key: string): Promise<string | null> {
    return this.store[key] || null;
  }

  async del(key: string): Promise<number> {
    if (this.store[key]) {
      delete this.store[key];
      return 1;
    }
    return 0;
  }
}

export const redis = new MockRedis();
