import "dotenv/config";

export const config = {
  PORT: parseInt(process.env.PORT ?? "8001", 10),
  NODE_ENV: process.env.NODE_ENV ?? "development",
  JWT_SECRET: process.env.JWT_SECRET ?? "change-me-in-production",
  JWT_EXPIRES_IN: process.env.JWT_EXPIRES_IN ?? "1h",
  CORS_ORIGINS: (process.env.CORS_ORIGINS ?? "http://localhost:3000,https://infinityxai.com").split(","),
  LOG_LEVEL: process.env.LOG_LEVEL ?? "info",
};
