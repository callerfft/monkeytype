export const animate = () => {};
export const AnimationParams = {};
export const JSAnimation = {};
export const envConfig = { isDev: true, isDevelopment: true };
export const languageHashes = {};

// Schemas types imported as values in legacy code
export const Config = {};
export const CustomThemeColors = {};
export const TypingSpeedUnit = {};
export const Mode = {};
export const Mode2 = {};
export const PersonalBests = {};
export const Result = {};
export const RankAndCount = {};

const mockProxy = new Proxy({}, {
  get: () => () => {},
});
export default mockProxy;
