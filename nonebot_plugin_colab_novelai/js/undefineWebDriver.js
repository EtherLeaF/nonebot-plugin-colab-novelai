Object.defineProperties(navigator,{ webdriver:{ get: () => undefined } })
window.navigator.chrome = { runtime: {},  };
Object.defineProperty(navigator, 'languages', { get: () => ['en-US', 'en'] });
Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5,6], });