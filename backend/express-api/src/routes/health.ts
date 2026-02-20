import { Router } from "express";
const router = Router();

router.get("/", (_req, res) => {
  res.json({ status: "ok", service: "infinity-express-api", timestamp: new Date().toISOString() });
});

router.get("/ready", (_req, res) => {
  res.json({ ready: true, checks: { api: "ok" } });
});

export { router as healthRouter };
