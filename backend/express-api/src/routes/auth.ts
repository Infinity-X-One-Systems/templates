import { Router } from "express";
import bcrypt from "bcryptjs";
import jwt from "jsonwebtoken";
import { z } from "zod";
import { config } from "../config";

const router = Router();
const users = new Map<string, { id: string; email: string; name: string; role: string; hash: string }>();

const RegisterSchema = z.object({ email: z.string().email(), password: z.string().min(8), name: z.string().min(2) });
const LoginSchema = z.object({ email: z.string().email(), password: z.string() });

router.post("/register", async (req, res) => {
  const parsed = RegisterSchema.safeParse(req.body);
  if (!parsed.success) { res.status(422).json({ error: "Validation failed", details: parsed.error.flatten() }); return; }
  const { email, password, name } = parsed.data;
  if (users.has(email)) { res.status(409).json({ error: "Email already registered" }); return; }
  const id = crypto.randomUUID();
  const hash = await bcrypt.hash(password, 12);
  users.set(email, { id, email, name, role: "user", hash });
  res.status(201).json({ id, email, name, role: "user" });
});

router.post("/login", async (req, res) => {
  const parsed = LoginSchema.safeParse(req.body);
  if (!parsed.success) { res.status(422).json({ error: "Validation failed" }); return; }
  const { email, password } = parsed.data;
  const user = users.get(email);
  if (!user || !(await bcrypt.compare(password, user.hash))) { res.status(401).json({ error: "Invalid credentials" }); return; }
  const token = jwt.sign({ sub: user.id, role: user.role }, config.JWT_SECRET, { expiresIn: config.JWT_EXPIRES_IN as string });
  res.json({ access_token: token, token_type: "bearer" });
});

export { router as authRouter };
