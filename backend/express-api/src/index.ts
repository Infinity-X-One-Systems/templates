import express from "express";
import helmet from "helmet";
import cors from "cors";
import compression from "compression";
import { rateLimit } from "express-rate-limit";
import { pinoHttp } from "pino-http";
import { config } from "./config";
import { healthRouter } from "./routes/health";
import { authRouter } from "./routes/auth";
import { errorHandler } from "./middleware/error";

const app = express();

// Security middleware
app.use(helmet());
app.use(cors({ origin: config.CORS_ORIGINS, credentials: true }));
app.use(compression());
app.use(express.json({ limit: "1mb" }));
app.use(express.urlencoded({ extended: true }));
app.use(pinoHttp({ level: config.LOG_LEVEL }));

// Rate limiting
app.use(rateLimit({ windowMs: 15 * 60 * 1000, max: 100, standardHeaders: true }));

// Routes
app.use("/health", healthRouter);
app.use("/auth", authRouter);

// Error handler
app.use(errorHandler);

if (process.env.NODE_ENV !== "test") {
  app.listen(config.PORT, () => {
    console.log(`Server running on port ${config.PORT}`);
  });
}

export { app };
